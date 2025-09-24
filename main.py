from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from typing import List
import asyncio

# Cria a aplicação FastAPI
app = FastAPI()

# Uma classe simples para gerenciar todas as conexões WebSocket ativas
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: bytes):
        for connection in self.active_connections:
            await connection.send_bytes(message)

# Instancia o gerenciador
manager = ConnectionManager()

# Define o endpoint do WebSocket em /ws
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    print(f"Novo cliente conectado. Total: {len(manager.active_connections)}")
    
    try:
        # Loop principal: fica ouvindo por mensagens do cliente
        while True:
            # Espera por um chunk de áudio (em bytes)
            data = await websocket.receive_bytes()
            
            # Retransmite o chunk para todos os outros clientes
            await manager.broadcast(data)
            
    except WebSocketDisconnect:
        # Isso acontece quando o cliente se desconecta (fecha o app, etc.)
        manager.disconnect(websocket)
        print(f"Cliente desconectado. Total: {len(manager.active_connections)}")

# Endpoint de health check para o Render saber que o app está vivo
@app.get("/")
def read_root():
    return {"status": "Servidor Shiba Sync está no ar!"}
