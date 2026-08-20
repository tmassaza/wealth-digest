from fastapi import APIRouter

router = APIRouter(prefix="", tags=["health"])


@router.get("/health")
def health() -> dict[str, str]:
    """Controllo rapido di stato del servizio."""

    return {"status": "ok"}
