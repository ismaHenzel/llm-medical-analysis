from fastapi import FastAPI
from src.routers import auth, medical_agent, users

app = FastAPI()

app.include_router(users.router)
app.include_router(auth.router)
app.include_router(medical_agent.router)

@app.get("/")
async def root():
    return {"message": "Access one for the described routes"}
