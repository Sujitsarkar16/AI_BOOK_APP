"""
WebSocket routes for real-time updates
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Dict
import json
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

# Store active connections - maps book_id to list of WebSockets
active_connections: Dict[int, list] = {}


@router.websocket("/ws/books/{book_id}")
async def websocket_endpoint(websocket: WebSocket, book_id: int):
    """WebSocket endpoint for real-time book generation updates"""
    
    await websocket.accept()
    
    # Store connection
    if book_id not in active_connections:
        active_connections[book_id] = []
    active_connections[book_id].append(websocket)
    
    logger.info(f"WebSocket connected for book {book_id}")
    
    try:
        while True:
            data = await websocket.receive_text()
            # Echo back for now
            await websocket.send_text(f"Echo: {data}")
            
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for book {book_id}")
        # Cleanup connection
        if book_id in active_connections:
            if websocket in active_connections[book_id]:
                active_connections[book_id].remove(websocket)
            # Remove entry if no connections left
            if not active_connections[book_id]:
                del active_connections[book_id]
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        # Cleanup connection
        if book_id in active_connections:
            if websocket in active_connections[book_id]:
                active_connections[book_id].remove(websocket)
            # Remove entry if no connections left
            if not active_connections[book_id]:
                del active_connections[book_id]


async def broadcast_to_book(book_id: int, message_type: str, data: dict):
    """Broadcast message to all WebSocket connections for a book"""
    
    if book_id in active_connections:
        message = {
            'type': message_type,
            'data': data
        }
        
        disconnected = []
        for websocket in active_connections[book_id]:
            try:
                await websocket.send_text(json.dumps(message))
            except:
                disconnected.append(websocket)
        
        # Remove disconnected sockets
        for ws in disconnected:
            active_connections[book_id].remove(ws)

