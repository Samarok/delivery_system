from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import datetime
from pydantic import BaseModel
from fastapi import FastAPI, HTTPException

app = FastAPI()

class LoginRequest(BaseModel):
    username: str
    password: str

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Заглушки данных
deliveries = [
    {
        "id": 1,
        "status": "pending",
        "driver_name": "Иван Петров",
        "receiver_name": "Мария Сидорова",
        "current_temperature": 5.2,
        "created_at": "2024-01-15T08:00:00Z"
    },
    {
        "id": 2, 
        "status": "in_transit",
        "driver_name": "Петр Сидоров", 
        "receiver_name": "Анна Иванова",
        "current_temperature": 6.1,
        "created_at": "2024-01-15T09:00:00Z"
    },
    {
        "id": 3,
        "status": "delivered",
        "driver_name": "Сергей Козлов",
        "receiver_name": "Ольга Новикова", 
        "current_temperature": 4.8,
        "created_at": "2024-01-15T10:00:00Z"
    },
    {
        "id": 4,
        "status": "completed",
        "driver_name": "Алексей Морозов",
        "receiver_name": "Екатерина Волкова",
        "current_temperature": 5.5,
        "created_at": "2024-01-15T11:00:00Z"
    }
]

sensor_data = [
    {
        "id": 1,
        "temperature": 5.2,
        "timestamp": datetime.datetime.now().isoformat() + "Z",
        "sensor_id": "sensor_001"
    },
    {
        "id": 2,
        "temperature": 7.9,  # Высокая температура для теста алерта
        "timestamp": datetime.datetime.now().isoformat() + "Z", 
        "sensor_id": "sensor_002"
    },
    {
        "id": 3,
        "temperature": 4.5,
        "timestamp": datetime.datetime.now().isoformat() + "Z",
        "sensor_id": "sensor_003"
    }
]

@app.post("/api/auth/login")
async def login(login_data: LoginRequest):
    # Простая проверка логина
    valid_users = {
        "driver1": "password",
        "receiver1": "password", 
        "dispatcher1": "password"
    }
    
    if login_data.username in valid_users and valid_users[login_data.username] == login_data.password:
        return {"access_token": f"fake-token-{login_data.username}", "token_type": "bearer"}
    else:
        raise HTTPException(status_code=401, detail="Invalid credentials")

@app.get("/api/deliveries")
async def get_deliveries():
    return deliveries

@app.get("/api/sensors/temperature") 
async def get_temperature():
    return sensor_data

@app.put("/api/deliveries/{delivery_id}")
async def update_delivery(delivery_id: int, status: str):
    return {"status": "updated"}