from celery import Celery

from config import CELERY_BACKEND, CELERY_BROKER

celery_app = Celery(
    "tasks",
    backend=CELERY_BACKEND,
    broker=CELERY_BROKER
)
