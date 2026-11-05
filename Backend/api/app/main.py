import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from . import config
from .database import Base, engine
from .routers import auth as auth_router
from .routers import users as users_router
from .routers import sessions as sessions_router
from .routers import onboarding as onboarding_router
from .routers import checkins as checkins_router
from .routers import ask as ask_router


def create_app() -> FastAPI:
    config.validate_secrets()
    app = FastAPI(title="CortexAI Backend API", version="0.1.0")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=config.cors_origins(),
        allow_credentials=True,
        allow_methods=["GET", "POST", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type", onboarding_router.DEVICE_SECRET_HEADER],
    )

    # Create database tables on startup (simple dev default)
    @app.on_event("startup")
    def on_startup() -> None:
        Base.metadata.create_all(bind=engine)

    app.include_router(auth_router.router, prefix="/auth", tags=["auth"]) 
    app.include_router(users_router.router, prefix="/users", tags=["users"]) 
    app.include_router(sessions_router.router, prefix="/sessions", tags=["sessions"]) 
    app.include_router(onboarding_router.router, prefix="/onboarding", tags=["onboarding"]) 
    app.include_router(checkins_router.router, prefix="/checkins", tags=["checkins"]) 
    app.include_router(ask_router.router, prefix="/ask", tags=["ask"]) 

    @app.get("/health")
    def health() -> dict:
        return {"status": "ok"}

    return app


app = create_app()

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))

