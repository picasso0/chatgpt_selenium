import motor.motor_asyncio


async def get_database():
    client = motor.motor_asyncio.AsyncIOMotorClient(
        "mongodb://77.238.108.86:27000/log?retryWrites=true&w=majority")
    db = client.gathering
    return db
