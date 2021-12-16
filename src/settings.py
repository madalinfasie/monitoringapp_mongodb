import os
import sys

BASE_DIR = os.path.dirname(__file__)
sys.path.insert(0, BASE_DIR)

# MongoDB
MONGO_URL = os.getenv('MONGO_URL')
MONGO_DB_NAME = os.getenv('MONGO_DB_NAME')
MONGO_METRICS_COLLECTION = os.getenv('MONGO_METRICS_COLLECTION')

# Celery
CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL')
CELERY_IMPORTS = ("tasks.tasks", )
