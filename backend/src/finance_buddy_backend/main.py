from fastapi import FastAPI
from finance_buddy_backend.api.routes.health import health_router
from finance_buddy_backend.api.routes.chat import chat_router
from fastapi.middleware.cors import CORSMiddleware



app= FastAPI()

# Configure CORS to allow requests from the frontend development server
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include the health router
app.include_router(health_router)
# Include the chat router
app.include_router(chat_router)



