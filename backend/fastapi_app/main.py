from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .api.v1 import ai, webhook, monitoring, web3
from .api.v1.integrations import slack, gmail, sheets, calendar
from fastapi.openapi.utils import get_openapi
from .core.auth import get_current_user


app = FastAPI(
    title="Zapnium",
    description="AI-powered automation platform API",
    version="1.0.0",
    
)

# OpenAPI security scheme
app.openapi = {
    "components": {
        "securitySchemes": {
            "Bearer": {
                "type": "http",
                "scheme": "bearer",
                "bearerFormat": "JWT",
            }
        }
    },
    "security": [{"Bearer": []}]
}

#Configure CORS

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8000", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

#Including Routers
app.include_router(ai.router, prefix="/api/v1/ai", tags=["AI Processing"])
app.include_router(webhook.router, prefix="/api/v1/webhooks", tags=["Webhooks"])
app.include_router(web3.router, prefix="/api/v1/web3", tags=["Web3"])

app.include_router(monitoring.router, prefix="/api/v1/monitoring", tags=["Monitoring"])
app.include_router(gmail.router, prefix="/api/v1/integrations/gmail", tags=["Gmail"])
app.include_router(sheets.router, prefix="/api/v1/integrations/sheets", tags=["Google Sheets"])
app.include_router(calendar.router, prefix="/api/v1/integrations/calendar", tags=["Google Calendar"])
app.include_router(slack.router, prefix="/api/v1/integrations/slack", tags=["Slack"])




# Custom OpenAPI schema
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title="AI Automation Platform API",
        version="1.0.0",
        description="API documentation for AI Automation Platform",
        routes=app.routes,
    )

    # Custom security scheme
    openapi_schema["components"] = {
        "securitySchemes": {
            "Bearer": {
                "type": "http",
                "scheme": "bearer",
                "bearerFormat": "JWT",
                "description": "Enter the JWT token from your login response"
            }
        }
    }
    
    # Apply security globally
    openapi_schema["security"] = [{"Bearer": []}]

    app.openapi_schema = openapi_schema
    return app.openapi_schema

# Override the default openapi schema
app.openapi = custom_openapi

app.get("/", tags=["Root"])
async def read_root():
    return {
        "message": "Welcome to Zapnium",
        "docs": "/docs",
        "health": "OK",
        "redoc": "/redoc"
    }