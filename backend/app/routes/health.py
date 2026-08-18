from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.health_data import HealthData
from app.routes.auth import get_current_user

router = APIRouter(
    prefix="/health",
    tags=["Health Data"]
)


@router.get("/")
def get_health_data(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    return (
        db.query(HealthData)
        .order_by(HealthData.report_date.desc())
        .limit(100)
        .all()
    )


@router.get("/district/{district}")
def get_district_health_data(
    district: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    data = (
        db.query(HealthData)
        .filter(HealthData.district == district)
        .order_by(HealthData.report_date.desc())
        .all()
    )

    if not data:
        raise HTTPException(
            status_code=404,
            detail="No health data found for this district"
        )

    return data


@router.get("/summary")
def health_summary(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    total_records = db.query(HealthData).count()

    return {
        "total_records": total_records,
        "message": "Health data API is working"
    }