from env_secrets import config
from fastapi import FastAPI, HTTPException, status
from routers import endpoints, auth, users, google_api
from db.relational_db import Base, engine

app = FastAPI()

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(google_api.router)
app.include_router(endpoints.router)

@app.on_event("startup")
def startup_event():
    Base.metadata.create_all(bind=engine)