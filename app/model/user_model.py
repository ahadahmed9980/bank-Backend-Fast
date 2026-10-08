from app.utils.objects import from_Object_id, to_Object_id
from fastapi import HTTPException
from datetime import datetime, timezone
from app.database.mongodb import users_collection
from app.utils.password import hash_Password,compare_password


# reg user
async def userRegister(data: dict) -> dict:
    print("1 - function start")
    isExist = await users_collection.find_one({"email":data["email"]})
    print("2 - find complete")


    if isExist:
        raise HTTPException(status_code=409, detail="user already exist please login")
    print("3 - before password hash")
    
    
    document = {
        "name": data["name"],
        "email": data["email"],
        "password": hash_Password(data["password"]),
        "created_at": datetime.now(timezone.utc),
    }
    print("4 - password hash complete")
    result = await users_collection.insert_one(document)
    print("5 - insert complete")
    document["_id"] = result.inserted_id
    
    return from_Object_id( document)
