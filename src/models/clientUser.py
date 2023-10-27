from pydantic import BaseModel

class User(BaseModel):
    username: str
    password: str
    email: str
    
class loginUser(BaseModel):
    username_or_email: str
    password: str
