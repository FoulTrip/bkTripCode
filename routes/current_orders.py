from fastapi import APIRouter, Header, HTTPException
from fastapi.responses import JSONResponse
from handlers.token import validateToken
from database.db import get_all_orders


current_orders = APIRouter()


@current_orders.get("/user_orders/{user_id}")
async def get_current_orders(user_id: str):
    return await get_all_orders(user_id)
