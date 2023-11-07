from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes.auth import auth_route
from routes.order import orders
from routes.current_orders import current_orders
from dotenv import load_dotenv


app = FastAPI()

# Configuro los orígenes permitidos (origins) en el CORS Middleware
origins = [
    "http://localhost:3000", # URL del frontend y se puede agregar mas # URL del frontend y se puede agregar mas
]


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {"message": "TripCode"}

app.include_router(auth_route, prefix="/auth")
app.include_router(orders, prefix="/order")
app.include_router(current_orders, prefix="/order")

load_dotenv()