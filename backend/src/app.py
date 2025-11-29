from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from db.init_db import create_tables
from routes import auth, users, deliveries, sensors


@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_tables()
    yield


app = FastAPI(
    title="Sensors API",
    description="API для системы мониторинга температурных датчиков и доставок",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключаем роуты
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(users.router, prefix="/api/users", tags=["Users"])
app.include_router(deliveries.router, prefix="/api/deliveries", tags=["Deliveries"])
app.include_router(sensors.router, prefix="/api/sensors", tags=["Sensors"])


@app.get("/")
async def root():
    return {"message": "Sensors API is running"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
