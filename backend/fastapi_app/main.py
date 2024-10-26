from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import ai, webhook

app = FastAPI(
    title="Zapnium",
    description="AI-powered automation platform API",
    version="1.0.0"
)

#Configure CORS

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

#Including Routers
app.include_router(ai.router, prefix="/api/v1/ai", tags=["AI Processing"])
app.include_router(webhook.router, prefix="/api/v1/webhooks", tags=["Webhooks"])

app.get("/", tags=["Root"])
async def read_root():
    return {
        "message": "Welcome to Zapnium",
        "docs": "/docs",
        "health": "OK"
    }