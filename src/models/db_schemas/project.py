from pydantic import BaseModel, Field, validator
from typing import Optional
from bson.objectid import ObjectId

class Project(BaseModel):
    id: Optional[ObjectId] = Field(None, alias="_id")
    project_id: str = Field(..., min_length=1)
    
    @validator('project_id')
    def validate_project_id(cls, value): # cls is a reference to the class itself
        if not value.isalnum():
            raise ValueError('project_id must be alphanumeric')
        
        return value
    
    # Pydantic is not familiart with ObjectID, so we need to allow it
    class Config:
        arbitrary_types_allowed = True

    @classmethod 
    def get_indexes(cls): 
        return [
            {
                "key": [("project_id", 1)], # search by project_id, return in ascending order
                "name": "project_id_index_1", 
                "unique": True 
            }
        ]