from bson import ObjectId
from fastapi import HTTPException


def to_Object_id(user_id: str) -> dict:
    try:
        return ObjectId(user_id)
    except:
        raise HTTPException(status_code=404, detail="id not found")


def from_Object_id(user_id: dict) -> dict:
    user_id["_id"] = str(user_id["_id"])
    return user_id
