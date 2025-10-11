"""
Simple backend for testing the Obsidian plugin without ML dependencies
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Obsidian AI Assistant - Simple Backend", version="1.0.0")

# Add CORS middleware to allow requests from Obsidian
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Obsidian AI Assistant Backend is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "Backend is operational"}

@app.get("/status")
async def status():
    return {
        "status": "online",
        "backend_url": "http://127.0.0.1:8000",
        "features": {
            "basic": True,
            "ml": False,
            "embeddings": False,
            "voice": False
        }
    }

@app.post("/api/config/reload")
async def reload_config():
    return {"message": "Configuration reloaded", "status": "success"}

# Placeholder endpoints for the plugin
@app.post("/api/ask")
async def ask_question(question: dict):
    return {
        "response": "This is a placeholder response. ML features are not available in simple mode.",
        "status": "success"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)