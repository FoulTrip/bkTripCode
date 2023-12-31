from fastapi import Header, HTTPException
from motor.motor_asyncio import (
    AsyncIOMotorClient,
    AsyncIOMotorDatabase,
    AsyncIOMotorGridFSBucket,
)
from handlers.token import validateToken, BooleanvalidateToken
from os import getenv
from bson import ObjectId

# from gridfs import GridFS


client = AsyncIOMotorClient(getenv("MONGO_URI"))
database: AsyncIOMotorDatabase = client.tcbackend
collectionUsersClient = database.users_client
collectionUsersDevs = database.users_devs
allOrders = database.all_orders

fs: AsyncIOMotorGridFSBucket = AsyncIOMotorGridFSBucket(database)


# Users


async def db_create_user(user_data: dict, type: str):
    if type == "client":
        new_user = await collectionUsersClient.insert_one(user_data)
        created_user = await collectionUsersClient.find_one(
            {"_id": new_user.inserted_id}
        )
        return created_user
    elif type == "dev":
        new_user = await collectionUsersDevs.insert_one(user_data)
        created_user = await collectionUsersClient.find_one(
            {"_id": new_user.inserted_id}
        )
        return created_user


# Función para agregar una orden a un usuario
async def add_order_to_user(user_id: str, order_data: dict):
    try:
        user_data = await collectionUsersClient.find_one({"_id": user_id})
        if user_data:
            order_data["_id"] = str(ObjectId())
            user_data["current_orders"].append(order_data)
            await collectionUsersClient.update_one(
                {"_id": user_id}, {"$set": user_data}
            )
            return True
        else:
            return False
    except Exception as e:
        print(f"Error al agregar la orden al usuario: {str(e)}")
        return False


# Obtener
def get_user_data(Authorization: str = Header(None)):
    user_data = validateToken(Authorization)
    return user_data


def get_user_id(token: str):
    if not token:
        raise HTTPException(
            status_code=401, detail="Token de autorización no proporcionado"
        )

    user_data = validateToken(token)
    if "_id" not in user_data:
        raise HTTPException(
            status_code=401,
            detail="Campo '_id' no encontrado en el token de autorización",
        )

    return user_data["_id"]


# Orders


# Eliminar una orden de los "current_orders" de un usuario
async def remove_order_from_current_orders(user_id: str, order_id: str):
    try:
        # Utiliza la operación $pull para eliminar la orden con el _id especificado
        result = await collectionUsersClient.update_one(
            {"_id": user_id}, {"$pull": {"current_orders": {"_id": order_id}}}
        )

        # Verifica si se realizó con éxito la eliminación
        if result.modified_count > 0:
            return True
        else:
            return False
    except Exception as e:
        print(f"Error al eliminar la orden del usuario: {str(e)}")
        return False


# Crear una nueva orden
async def create_order(order_data: dict):
    new_order = await allOrders.insert_one(order_data)
    created_order = await allOrders.find_one({"_id": new_order.inserted_id})
    return created_order


# Actualizar una orden existente
async def update_order(order_id: str, updated_data: dict):
    await allOrders.update_one({"_id": order_id}, {"$set": updated_data})


# Eliminar una orden
async def delete_order(order_id: str):
    try:
        result = await allOrders.delete_one({"_id": order_id})

        if result.deleted_count > 0:
            return True  # Documento eliminado con éxito
        else:
            return False  # Documento no encontrado para eliminar
    except Exception as e:
        print(f"Error al eliminar la orden: {str(e)}")
        return False


# Obtener todas las ordenes de cada usuario
async def get_all_orders(user_id: str):
    try:
        usrId_obj = ObjectId(user_id)
        user_data = await collectionUsersClient.find_one({"_id": usrId_obj})

        if user_data is None:
            return {"Usuario no encontrado"}

        if user_data and "current_orders" in user_data:
            return user_data["current_orders"]
        else:
            return []
    except Exception as e:
        print(f"Error al obtener los pedidos actuales del usuario: {e}")
        return []
