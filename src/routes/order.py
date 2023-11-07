from fastapi import APIRouter, Header, UploadFile, File
from fastapi.responses import JSONResponse
from handlers.token import validateToken
from database.db import collection, add_order_to_user, allOrders, remove_order_from_current_orders, update_order, delete_order, fs

orders = APIRouter()
    

@orders.post("/create")
async def create_order(order_data: dict, Authorization: str = Header(None)):
    # parameter of file 'pdf_file: UploadFile = File(None)'
    try:
        # Verificar la autenticación del usuario utilizando el token Authorization
        token = Authorization.split(" ")[1]
        user_data = validateToken(token)  # Suponiendo que validateToken devuelve los datos del usuario
        
        # pdf = order_data["pdf_file"]
        # if pdf:
        #     content = await pdf.read()
        #     file_id = fs.put(content, filename = pdf.filename)
        #     order_data["pdf_file_id"] = str(file_id)
        
        order_data["status"] = "In Progress"
        order_data["meeting"] = "Waiting"
        order_data["meeting_day"] ="Waiting"
        order_data["developer"] = "Waiting"

        # Agregar la orden a la colección del usuario en "current_orders"
        user = await collection.find_one({"username": user_data["username"]})
        user_id = user["_id"]
        
        await add_order_to_user(user_id, order_data)

        # Almacenar la orden en la otra colección
        await allOrders.insert_one(order_data)  # Almacena la orden en "orders_collection"

        return JSONResponse(content={"message": "Orden creada con éxito"})
    except Exception:
        return JSONResponse(content={"message": "Error al crear la orden"}, status_code=500)

# @orders.delete("/remove/{user_id}/{order_id}")
# async def remove_order(user_id: str, order_id: str):
#     try:
#         await remove_order_from_current_orders(user_id, order_id)
        
#         return JSONResponse(content={"message": "Orden eliminada con exito"})
#     except Exception as ex:
#         print(f"Error al eliminar la orden: {str(ex)}")
#         return JSONResponse(content={"message": "Error al eliminar la orden"}, status_code=500)

# @orders.put("/update/{order_id}")
# async def update_existing_order(order_id: str, updated_data: dict):
#     try:
#         # Utiliza la función para actualizar la orden existente
#         await update_order(order_id, updated_data)
        
#         return JSONResponse(content={"message": "Orden actualizada con éxito"})
#     except Exception as ex:
#         print(f"Error al actualizar la orden: {str(ex)}")
#         return JSONResponse(content={"message": "Error al actualizar la orden"}, status_code=500)
