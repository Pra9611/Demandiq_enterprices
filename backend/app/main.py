from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import forecast, monitoring
import os
import subprocess
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATASET_PATH = os.path.join(BASE_DIR, "datasets", "retail_demand_dataset.csv")
SCRIPT_PATH = os.path.join(BASE_DIR, "scripts", "generate_dataset.py")

app = FastAPI(title='DemandIQ Enterprise API', version='1.0.0')
app.add_middleware(CORSMiddleware, allow_origins=['*'], allow_credentials=True, allow_methods=['*'], allow_headers=['*'])
app.include_router(forecast.router, prefix='/api/forecast', tags=['Forecast'])
app.include_router(monitoring.router, prefix='/api/monitoring', tags=['Monitoring'])

@app.get("/")
def home():
    return {"message": "DemandIQ Enterprise API running"}

@app.get('/health')
def health():
    return {'status': 'healthy', 'service': 'DemandIQ Enterprise API'}

@app.post('/api/retrain')
def retrain():
    return {'status': 'accepted', 'message': 'Retraining job placeholder. Run scripts/train_tensorflow_forecaster.py in production scheduler.'}
