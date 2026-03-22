from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import json
import time


def returnResponseTime(app: FastAPI):
    @app.middleware('http')
    async def add_process_time_header(request: Request, call_next):
        start_time = time.perf_counter()
        response = await call_next(request)
        end_time = time.perf_counter()
        process_time_ms = round((end_time - start_time) * 1000, 4)

        if response.headers.get('content-type', '').startswith('application/json'):
            body = b''
            async for chunk in response.body_iterator:
                body += chunk
            data = json.loads(body)
            data['responseMs'] = process_time_ms
            headers = {k: v for k, v in response.headers.items() if k.lower() != 'content-length'}
            return JSONResponse(content=data, status_code=response.status_code, headers=headers)

        return response