from fastapi import APIRouter
from database.db import get_all_orders


current_orders = APIRouter()


@current_orders.get("/user_orders/{user_id}")
async def get_current_orders(user_id: str):
    return await get_all_orders(user_id)
