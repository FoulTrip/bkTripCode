from fastapi import APIRouter, Header, HTTPException
from models.clientUser import User, loginUser
from handlers.token import getToken, validateToken, BooleanvalidateToken
from fastapi.responses import JSONResponse
from passlib.hash import bcrypt
from database.db import (
    collectionUsersClient,
    collectionUsersDevs,
    db_create_user,
    get_user_id,
)

auth_route = APIRouter()


@auth_route.post("/signup/client")
async def register(user: User):
    try:
        user_data = user.model_dump()

        hashed_password = bcrypt.hash(user.password)
        user_data["password"] = hashed_password
        user_data["avatar"] = ""
        user_data["phone"] = ""
        user_data["rol"] = "client"
        user_data["current_orders"] = []
        user_data["history_orders"] = []
        user_data["draft_orders"] = []
        user_data["token"] = getToken(user_data)

        await db_create_user(dict(user_data), type="client")

        return JSONResponse(
            content={
                "message": "Usuario registrado con éxito",
            }
        )
    except Exception as ex:
        print(ex)
        return JSONResponse(content={f"message": "Error al registrar usuario "})


@auth_route.post("/signup/developer")
async def register(user: User):
    try:
        user_data = user.model_dump()

        hashed_password = bcrypt.hash(user.password)
        user_data["password"] = hashed_password
        user_data["avatar"] = ""
        user_data["phone"] = ""
        user_data["rol"] = "developer"
        user_data["current_orders"] = []
        user_data["history_orders"] = []
        user_data["draft_orders"] = []
        user_data["token"] = getToken(user_data)

        new_user = await db_create_user(dict(user_data), type="dev")

        return JSONResponse(
            content={
                "message": "Usuario registrado con éxito",
            }
        )
    except Exception as ex:
        print(ex)
        return JSONResponse(content={f"message": "Error al registrar usuario "})


@auth_route.post("/signin/client")
async def login(login_data: loginUser):
    try:
        print(login_data)
        exist_user = await collectionUsersClient.find_one(
            {
                "$or": [
                    {"username": login_data.username_or_email},
                    {"email": login_data.username_or_email},
                ]
            }
        )

        # print(exist_user)

        if exist_user is None:
            status = "unauthenticated"
        else:
            status = "authenticated"

        # print(status)

        if exist_user and bcrypt.verify(login_data.password, exist_user["password"]):
            token = getToken(
                {
                    "username": exist_user["username"],
                    "email": exist_user["email"],
                    "avatar": exist_user["avatar"],
                    "phone": exist_user["phone"],
                    "status": str(status),
                    "_id": str(exist_user["_id"]),
                }
            )
            # print(validateToken(token))
            return JSONResponse(
                content={"info": "Inicio de sesión exitoso", "token": token}
            )
        else:
            return JSONResponse(content={"message": "Invalid credentials"})
    except Exception as ex:
        print(ex)
        return JSONResponse(
            content={"message": "Credenciales inválidas"}, status_code=401
        )


@auth_route.post("/signin/developer")
async def login(login_data: loginUser):
    try:
        exist_user = await collectionUsersDevs.find_one(
            {
                "$or": [
                    {"username": login_data.username_or_email},
                    {"email": login_data.username_or_email},
                ]
            }
        )

        if exist_user is None:
            status = "unauthenticated"
        else:
            status = "authenticated"

        print(status)

        if exist_user and bcrypt.verify(login_data.password, exist_user["password"]):
            token = getToken(
                {
                    "username": exist_user["username"],
                    "email": exist_user["email"],
                    "avatar": exist_user["avatar"],
                    "phone": exist_user["phone"],
                    "status": str(status),
                    "_id": str(exist_user["_id"]),
                }
            )

            # print(validateToken(token))
            return JSONResponse(
                content={"info": "Inicio de sesión exitoso", "token": token}
            )
        else:
            return JSONResponse(content={"message": "Invalid credentials"})
    except Exception as ex:
        print(ex)
        return JSONResponse(
            content={"message": "Credenciales inválidas"}, status_code=401
        )


@auth_route.post("/verify/token")
def verifyToken(Authorization: str = Header()):
    try:
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
    except Exception as ex:
        print(ex)


@auth_route.get("/getid")
async def get_id_user(Authorization: str = Header(None)):
    if Authorization is None:
        raise HTTPException(
            status_code=401, detail="Token de autorización no proporcionado"
        )

    parts = Authorization.split(" ")
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(
            status_code=401, detail="Formato de token de autorización no válido"
        )

    token = parts[1]
    id = await get_user_id(token)
    return id
