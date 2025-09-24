from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import asyncio

# Cria a aplicação FastAPI
app = FastAPI()

# --- ADIÇÃO CRÍTICA: CONFIGURAÇÃO DE CORS ---
# Isso permite que seu aplicativo Android se conecte ao servidor.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permite todas as origens
    allow_credentials=True,
    allow_methods=["*"],  # Permite todos os métodos (GET, POST, etc.)
    allow_headers=["*"],  # Permite todos os cabeçalhos
)
# --- FIM DA ADIÇÃO ---

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
        while True:
            data = await websocket.receive_bytes()
            await manager.broadcast(data)
            
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        print(f"Cliente desconectado. Total: {len(manager.active_connections)}")

# Endpoint de health check
@app.get("/")
def read_root():
    return {"status": "Servidor Shiba Sync está no ar!"}
