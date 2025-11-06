# customers routes (placeholder)
# In future, move route logic from main.py to modular routes and include dependency injection for auth & tenant

from fastapi import APIRouter

router = APIRouter()

@router.get("/test")
def test():
    return {"message": "customers router placeholder"}
