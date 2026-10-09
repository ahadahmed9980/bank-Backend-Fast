from app.utils.objects import from_Object_id, to_Object_id
from fastapi import HTTPException
from datetime import datetime, timezone
from app.database.mongodb import users_collection
from app.utils.password import hash_Password, compare_password



# reg user
async def userRegister(data: dict) -> dict:

    isExist = await users_collection.find_one({"email": data["email"]})

    if isExist:
        raise HTTPException(status_code=409, detail="user already exist please login")

    document = {
        "name": data["name"],
        "email": data["email"],
        "password": hash_Password(data["password"]),
        "created_at": datetime.now(timezone.utc),
    }

    result = await users_collection.insert_one(document)

    document["_id"] = result.inserted_id
    document.pop("password", None)

    return from_Object_id(document)


# login user
async def userLogin(data:dict)->dict:
    isExist= await users_collection.find_one({"email":data['email']})
    if  not isExist:
          raise HTTPException(status_code=404, detail="Invalid email or password")
    
    
    






