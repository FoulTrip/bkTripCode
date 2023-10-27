from jwt import encode, decode, exceptions
from datetime import timedelta, datetime
from os import getenv
from fastapi.responses import JSONResponse


def expireToken(days: int):
    date = datetime.now()
    new_date = date + timedelta(days)
    return new_date

def getToken(data: dict):
    try:
        token = encode(payload={**data, "exp": expireToken(2) }, key=getenv("SECRET_KEY"), algorithm=getenv("ALGORITHM"))
        return token
    except Exception as e:
        print(f"Error al generar el token: {e}")
        return None

def validateToken(token):
    try:
        decode_token = decode(token, key=getenv("SECRET_KEY"), algorithms=getenv("ALGORITHM"))
        return dict(decode_token)
    except exceptions.DecodeError:
        return JSONResponse(content={"message": "Invalid token"}, status_code=401)
    except exceptions.ExpiredSignatureError:
        return JSONResponse(content={"message": "Invalid token"}, status_code=401)