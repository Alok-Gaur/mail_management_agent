from fastapi import FastAPI
import routers.endpoints as endpoints
app = FastAPI()

app.include_router(endpoints.router)