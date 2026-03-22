from fastapi import APIRouter
from fastapi.responses import JSONResponse
from src.helpers.helpers import return_releaseId, return_timestamps


app = APIRouter()


@app.get('')
async def check_health():
    return JSONResponse({'status': 'success', 'description': 'Health check of the backend system', 'connections': {
        'bot': 'active',
        'database': 'active',
        'core': 'active',
        'redis': 'active'
    }, 'releaseId': str(return_releaseId()), 'version': '1.0', 'timestamps': str(return_timestamps())}, status_code=200)