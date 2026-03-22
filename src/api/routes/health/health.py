from fastapi import APIRouter
from fastapi.responses import JSONResponse
from helpers.helpers import return_releaseId


app = APIRouter()


@app.get('/')
async def check_health():
    return JSONResponse({'status': 'success', 'description': 'Health check of the backend system', 'releaseId': str(return_releaseId()), 'version': '1.0'}, status_code=200)