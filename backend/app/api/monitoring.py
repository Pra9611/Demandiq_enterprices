from fastapi import APIRouter
from app.services.monitoring_service import drift_report, anomaly_report
router = APIRouter()

@router.get('/drift')
def drift():
    return drift_report()

@router.get('/anomalies')
def anomalies():
    return anomaly_report()
