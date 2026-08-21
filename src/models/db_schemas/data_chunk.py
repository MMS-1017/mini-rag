from pydantic import BaseModel, Field, validator
from typing import Optional
from bson.objectid import ObjectId

class DataChunk(BaseModel):
    id: Optional[ObjectId] = Field(None, alias="_id") # None not ... because it is optional
    chunk_text: str = Field(..., min_length=1)
    chunk_meta: dict
    chunk_order: int = Field(..., gt=0) # chunk_order should be a non-negative integer
    chunk_project_id: ObjectId
    chunk_asset_id: ObjectId # File related to the chunks (_id)

    class Config:
        arbitrary_types_allowed = True
    
    @classmethod
    def get_indexes(cls):
        return [
            {
                "key":[("chunk_project_id",1)],
                "name": "chunk_project_id_indx_1",
                "unique":False
            }
        ]

class RetrievedDocument(BaseException):
    text: str
    score: float
    