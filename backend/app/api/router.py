from fastapi import APIRouter

from .events import router as events_router
from .evidence import router as evidence_router
from .exports import router as exports_router
from .reports import router as reports_router
from .research import router as research_router

api_router = APIRouter()
api_router.include_router(research_router)
api_router.include_router(events_router)
api_router.include_router(evidence_router)
api_router.include_router(reports_router)
api_router.include_router(exports_router)
