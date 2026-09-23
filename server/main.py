
import uvicorn
from fastapi import FastAPI
from .routers import lobby, users

app = FastAPI()

app.include_router(lobby.router, prefix='/lobby')
app.include_router(users.router, prefix='/users')

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)