from fastapi import APIRouter

from .auth import router as auth_router
from .metrics import router as metrics_router
from .user import router as user_router
from .other import router as other_router

router = APIRouter()

router.include_router(auth_router, prefix="/auth", tags=["Auth"])
router.include_router(metrics_router, prefix="/metrics", tags=["Metrics"])
router.include_router(user_router, prefix="/user", tags=["Users"])
router.include_router(other_router, prefix="/other", tags=["Additional"])