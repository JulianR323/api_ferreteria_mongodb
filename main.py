from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from bson import ObjectId
from datetime import datetime
from models import Ferreteria, FerreteriaCreate
from database import coleccion_ferreteria, verificar_conexion

app= FastAPI(
    title="API Ferreteria",
    description="API RESTful asincrona para gestionar el inventario de una ferreteria con FastAPI y MongoDB.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    await verificar_conexion()

@app.get("/", tags=["Raíz"])
async def root():
    return {"message": "Bienvenido a la API de inventario de la Ferreteria",
            "documentacion": "/docs"}

@app.post(
    "/ferreteria",
    response_model=Ferreteria,
    status_code=status.HTTP_201_CREATED,
    tags=["Ferreteria"],
    summary="Registrar una herramienta en MongoDB",
)
async def create_herramienta(herramienta_in: FerreteriaCreate):
    herramienta_existente = await coleccion_ferreteria.find_one({
        "herramienta": herramienta_in.herramienta,
        "marca": herramienta_in.marca,
    })
    if herramienta_existente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"La herramienta '{herramienta_in.herramienta}' de marca '{herramienta_in.marca}' ya existe.",
        )

    nueva_herramienta = herramienta_in.model_dump()
    nueva_herramienta["fecha_creacion"] = datetime.now()

    resultado = await coleccion_ferreteria.insert_one(nueva_herramienta)

    herramienta_creada = await coleccion_ferreteria.find_one({"_id": resultado.inserted_id})
    return herramienta_creada

@app.get(
    "/ferreteria",
    response_model=List[Ferreteria],
    status_code=status.HTTP_200_OK,
    tags=["Ferreteria"],
    summary="Listar todas las herramientas"
)
async def get_herramientas():
    herramientas = []
    cursor = coleccion_ferreteria.find()
    async for documento in cursor:
        herramientas.append(documento)
    return herramientas

@app.get(
    "/ferreteria/{id}",
    response_model=Ferreteria,
    status_code=status.HTTP_200_OK,
    tags=["Ferreteria"],
    summary="Obtener una herramienta por ID"
)
async def get_herramienta_por_id(id: str):
    if not ObjectId.is_valid(id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"ID Invalido de MongoDB (ObjectID): {id}",
        )
    herramienta = await coleccion_ferreteria.find_one({"_id": ObjectId(id)})
    if herramienta:
        return herramienta
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Herramienta con ID '{id}' no encontrada.",
    )

@app.put(
    "/ferreteria/{id}",
    response_model=Ferreteria,
    status_code=status.HTTP_200_OK,
    tags=["Ferreteria"],
    summary="Actualizar una herramienta"
)
async def update_herramienta(id: str, herramienta_update: FerreteriaCreate):
    if not ObjectId.is_valid(id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"ID Invalido de MongoDB (ObjectID): {id}",
        )
    datos_a_actualizar = herramienta_update.model_dump(exclude_unset=True)
    if len(datos_a_actualizar) >= 1:
        resultado_actualizacion = await coleccion_ferreteria.update_one(
            {"_id": ObjectId(id)},
            {"$set": datos_a_actualizar}
        )
        if resultado_actualizacion.modified_count == 1 or resultado_actualizacion.matched_count == 1:
            herramienta_modificada = await coleccion_ferreteria.find_one({"_id": ObjectId(id)})
            return herramienta_modificada

    herramienta_existente = await coleccion_ferreteria.find_one({"_id": ObjectId(id)})
    if herramienta_existente:
        return herramienta_existente

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Herramienta con ID '{id}' no encontrada.",
    )

@app.delete(
    "/ferreteria/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["Ferreteria"],
    summary="Eliminar una herramienta de MongoDB"
)
async def delete_herramienta(id: str):
    if not ObjectId.is_valid(id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"ID Invalido de MongoDB (ObjectID): {id}",
        )
    resultado_eliminacion = await coleccion_ferreteria.delete_one({"_id": ObjectId(id)})
    if resultado_eliminacion.deleted_count == 1:
        return None
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Herramienta con ID '{id}' no encontrada.",
        )