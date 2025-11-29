# core/websocket_manager.py

from typing import List, Dict, Any
from fastapi import WebSocket


class WebSocketManager:
    """
    Класс для управления активными WebSocket-соединениями
    """

    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        """Подключает новое соединение"""
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        """Отключает соединение"""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: Dict[str, Any]):
        """Рассылает сообщение всем активным клиентам"""
        disconnected_connections = []

        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except RuntimeError:
                disconnected_connections.append(connection)
            except Exception as e:
                disconnected_connections.append(connection)

        for connection in disconnected_connections:
            self.disconnect(connection)


manager = WebSocketManager()
