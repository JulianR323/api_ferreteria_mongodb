from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Annotated
from datetime import datetime
from bson import ObjectId
from pydantic.json_schema import JsonSchemaValue
from pydantic_core import core_schema

class _ObjectIdPydanticAnnotation:
    @classmethod
    def __get_pydantic_core_schema__(cls, source_type, handler):
        def validate(v):
            if isinstance(v, ObjectId):
               return str(v)
            if isinstance(v, str) and ObjectId.is_valid(v):
                return v
            raise ValueError("ID Invalido de MongoDB (ObjectID)")
        
        return core_schema.json_or_python_schema(
            json_schema=core_schema.str_schema(),
            python_schema=core_schema.no_info_plain_validator_function(validate),
            serialization=core_schema.to_string_ser_schema()
        )

PyObjectId = Annotated[str, _ObjectIdPydanticAnnotation]


class FerreteriaBase(BaseModel):
    herramienta: str= Field(
        ...,
        min_length=3,
        max_length=100,
        description="Nombre de la herramienta",
        json_schema_extra={"example": "Taladro"}
    )
    marca: str = Field(
        ...,
        min_length=3,
        max_length=100,
        description="Marca de la herramienta",
        json_schema_extra={"example": "CAT"}
    )
    precio_unitario: float = Field(
        ...,
        gt=0,
        description="Precio unitario de la herramienta",
    )
    stock_disponible: int = Field(
        ...,
        ge=0,
        description="Cantidad disponible en stock",
    )

class FerreteriaCreate(FerreteriaBase):
    pass

class Ferreteria(FerreteriaBase):
    id: PyObjectId = Field(alias="_id", description="Identificador unico ObjectId de MongoDB")
    fecha_creacion: datetime = Field(default_factory=datetime.now, description="Fecha de registro")

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_schema_extra={
            "example": {
                "_id": "64b8f1e2c9e77a3f4d5e6b7c",
                "herramienta": "Taladro",
                "marca": "CAT",
                "precio_unitario": 250000,
                "stock_disponible": 27,
                "fecha_creacion": "2023-07-01T12:34:56.789Z"
            }
        }
    )