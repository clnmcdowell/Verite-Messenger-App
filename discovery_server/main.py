from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone

from . import models
from .database import SessionLocal, engine
from .models import Peer

# Create the database tables if they don't exist
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# CORS middleware to allow cross-origin requests
# Allow all origins, methods, and headers for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"], 
)

# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Define Pydantic request model for registering a peer
class RegisterRequest(BaseModel):
    id: str 
    port: int

@app.post("/register")
def register_peer(request: RegisterRequest, fastapi_request: Request, db: Session = Depends(get_db)):
    """
    Register a peer with the server. The peer's IP address and port are recorded.
    """
    # Get the IP address of the peer from the request
    ip = fastapi_request.client.host

    # Check if the peer already exists in the database
    peer = db.query(Peer).filter(Peer.id == request.id).first()

    # If the peer exists update its IP address and last seen time
    # If it doesn't exist create a new entry
    if peer:
        peer.ip = ip
        peer.port = request.port
        peer.last_seen = datetime.now(timezone.utc)
    else:
        peer = Peer(
            id=request.id,
            ip=ip,
            port=request.port,
            last_seen=datetime.now(timezone.utc)
        )
        db.add(peer)

    db.commit()
    return {"message": "Peer registered", "ip": ip, "port": request.port}

@app.post("/heartbeat")
def heartbeat(peer_id: str, db: Session = Depends(get_db)):
    """
    Update the last seen time of a peer.
    """


    peer = db.query(Peer).filter(Peer.id == peer_id).first()
    if not peer:
        raise HTTPException(status_code=404, detail="Peer not found")
    
    # Update the last seen time to the current time
    peer.last_seen = datetime.now(timezone.utc)
    db.commit()
    return {"message": "Heartbeat received", "timestamp": peer.last_seen}

@app.get("/peers")
def list_peers(db: Session = Depends(get_db)):
    """
    Return a list of peers that have been active in the last 60 seconds.
    """
    # Get the current time and calculate the cutoff time for active peers
    now = datetime.now(timezone.utc)
    cutoff = now - timedelta(seconds=60)

    # Query the database for peers that have been active since the cutoff time
    active_peers = db.query(Peer).filter(Peer.last_seen >= cutoff).all()

    if not active_peers:
        return {"message": "No active peers found"}
    
    # Return a list of active peers with their details
    return [
        {
            "id": peer.id,
            "ip": peer.ip,
            "port": peer.port,
            "last_seen": peer.last_seen.isoformat()
        }
        for peer in active_peers
    ]
