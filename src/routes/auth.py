from fastapi import APIRouter, Header
from models.clientUser import User, loginUser
from handlers.token import getToken, validateToken
from fastapi.responses import JSONResponse
from passlib.hash import bcrypt
from database.db import collection, db_create_user

auth_route = APIRouter()

@auth_route.post("/register")
async def register(user: User):
    try:
        
        user_data = user.model_dump()

        hashed_password = bcrypt.hash(user.password)
        user_data["password"] = hashed_password      
        user_data["avatar"] = ""
        user_data["phone"] = ""
        user_data["current_orders"] = []
        user_data["history_orders"] = []
        user_data["draft_orders"] = []
        
        user_data["token"] = getToken(user_data)
        
        new_user = await db_create_user(dict(user_data))

        return JSONResponse(content={"message": "Usuario registrado con éxito", "token": new_user["token"]})
    except Exception as ex:
        print(ex)
        return JSONResponse(content={f"message": "Error al registrar usuario "})

@auth_route.post("/login")
async def login(login_data: loginUser):
    try:
        exist_user = await collection.find_one({
            "$or": [
                {"username": login_data.username_or_email},
                {"email": login_data.username_or_email}
            ]
        })
    
        if exist_user and bcrypt.verify(login_data.password, exist_user["password"]):
                token = getToken({"username": exist_user["username"], "email": exist_user["email"]})
                return JSONResponse(content={"message": "Inicio de sesión exitoso", "token": token})
        else:
            return JSONResponse(content={"message": "Invalid credentials"})
    except Exception as ex:
        print(ex)
        return JSONResponse(content={"message": "Credenciales inválidas"}, status_code=401)

@auth_route.post("/verify/token")
def verifyToken(Authorization: str = Header(None)):
    # El token se genera con un " Bearer ...token " Elimino el Bearer y dejo solo el token
    token = Authorization.split(" ")[1]
    details = validateToken(token)
    
    if "password" in details:
        details.pop("password")
        
    if "username" in details:
        # Si el token es válido y contiene un campo "username", el usuario se considera autenticado
        status = "authenticated"
    else:
        status = "unauthenticated"

    details["status"] = status
    
    return details