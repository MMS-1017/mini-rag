from pydantic import BaseModel, Field, validator
from typing import Optional
from bson.objectid import ObjectId
from datetime import datetime

class Asset(BaseModel):
    id: Optional[ObjectId] = Field(None, alias="_id")  # constant among the collection
    asset_project_id: ObjectId                         # the project related to the asset
    asset_type: str = Field(..., min_length=1)         # file type
    asset_name: str = Field(..., min_length=1)         # alternative to the file_id I used to pass manually
    asset_size: int = Field(ge=0, default=None)        # file size
    asset_config: dict = Field(default=None)           # probable extra information
    asset_pushed_at: Optional[datetime] = Field(default=datetime.utcnow)

    class Config:
        arbitrary_types_allowed = True

    @classmethod 
    def get_indexes(cls): 
        return [
            {
                "key": [("asset_project_id", 1)],
                "name": "asset_project_id_index_1", 
                "unique": False
            },
            {
                "key": [("asset_project_id", 1), ("asset_name", 1)],
                "name": "asset_project_id_name_index_1", 
                "unique": True # combination of name and project_id should be unique
            }
        ]