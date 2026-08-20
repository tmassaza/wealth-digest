from fastapi import FastAPI

from app.api.routes.health import router as health_router
from app.api.routes.news import router as news_router
from app.api.routes.recommendations import router as recommendations_router
from app.api.routes.users import router as users_router

app = FastAPI(title="Wealth Digest POC", version="0.1.0")

# Registriamo qui tutte le route principali dell'app.
app.include_router(health_router)
app.include_router(users_router)
app.include_router(news_router)
app.include_router(recommendations_router)


@app.get("/")
def root() -> dict[str, str]:
    """Endpoint base utile per verificare che l'app sia in esecuzione."""

    return {"message": "Wealth Digest POC is running."}
