from fastapi import APIRouter

from services.api.answers.routes import router as answers_router
from services.api.sources.routes import router as sources_router
from services.api.statistics.routes import router as statistics_router

router = APIRouter(prefix="/api")
router.include_router(answers_router)
router.include_router(sources_router)
router.include_router(statistics_router)
