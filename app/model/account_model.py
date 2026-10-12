from datetime import datetime , timezone
from bson import ObjectId
from app.database.mongodb import account_collection

#create Account:
async def CreateAccout(user_id:ObjectId , currecy:str='PKR'):
    now = datetime.now(timezone.utc)
    account={
        "userId":user_id,
        'status':'ACTIVE',
        "currency":currecy,
        "createdAt":now,
        "updatedAt":now
    }
    result = await account_collection.insert_one(account)
    return account


