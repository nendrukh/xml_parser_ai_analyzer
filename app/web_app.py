import xml.etree.ElementTree as ET
import logging
import traceback

from celery.result import AsyncResult
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from status import HTTP_400_BAD_REQUEST

from celery_app import celery_app
from executor import executor

app = FastAPI()

logger = logging.getLogger()


@app.post("/schedule_task")
async def schedule_task(request: Request):
    body = await request.body()
    body = body.decode()
    try:
        ET.fromstring(body)
    except ET.ParseError:
        logger.error("Xml parse error:", traceback.format_exc())
        return JSONResponse({"status": "Xml parse error"}, status_code=HTTP_400_BAD_REQUEST)

    task = executor.apply_async((body,))
    return JSONResponse({"status": "Task scheduled", "task_id": task.id})


@app.get("/result/{task_id}")
async def get_result(task_id: str):
    result = AsyncResult(task_id, app=celery_app)
    if result.state == "SUCCESS":
        return JSONResponse({"task_id": task_id, "status": result.state, "result": result.result})

    return JSONResponse({"task_id": task_id, "status": result.state})
