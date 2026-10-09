from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import Base, engine
from app.routers import auth, controls, integrations, org, questionnaires, trust

Base.metadata.create_all(bind=engine)

app = FastAPI(title=settings.app_name, version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=list(
        dict.fromkeys(
            settings.cors_origins + ["http://localhost:5173", "http://127.0.0.1:5173"]
        )
    ),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api")
app.include_router(org.router, prefix="/api")
app.include_router(integrations.router, prefix="/api")
app.include_router(controls.router, prefix="/api")
app.include_router(questionnaires.router, prefix="/api")
app.include_router(trust.router, prefix="/api")


@app.get("/api/health")
def health():
    return {"status": "ok", "product": settings.app_name}
