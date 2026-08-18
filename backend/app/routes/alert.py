from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.alert import Alert
from app.models.village import Village
from app.schemas.alert import AlertResponse, AlertCheckResponse
from app.routes.auth import get_current_user
from app.services.prediction_service import run_prediction_for_village


router = APIRouter(
    prefix="/alerts",
    tags=["Alerts"]
)


# ============================================================
# RECOMMENDED ACTION TEXT
# ============================================================

def build_recommended_action(risk_level: str) -> str:
    if risk_level == "HIGH":
        return (
            "Immediate action required: notify health worker, "
            "advise boiling water before consumption, and "
            "arrange a water quality retest."
        )
    if risk_level == "MEDIUM":
        return (
            "Monitor closely and schedule a follow-up sensor "
            "reading within 24 hours."
        )
    return "No action required."


# ============================================================
# CHECK + GENERATE ALERT FOR A VILLAGE
# ============================================================
# This now runs the SAME ML prediction pipeline that
# POST /risk/predict/{village_id} uses (via run_prediction_for_village),
# instead of a separate rule-based check. That guarantees the Alert's
# risk_level can never disagree with the RiskPrediction the dashboard
# is showing for the same village at the same moment.

@router.post(
    "/check/{village_id}",
    response_model=AlertCheckResponse
)
def check_village_alert(
    village_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    prediction, factors, village = run_prediction_for_village(village_id, db)

    risk_level = prediction.risk_level
    reasons = [f.explanation for f in factors]

    if risk_level == "LOW":
        return AlertCheckResponse(
            village_id=village_id,
            alert_created=False,
            alert=None,
            reasons=reasons
        )

    alert = Alert(
        village_id=village_id,
        risk_prediction_id=prediction.id,
        alert_type="WATER_QUALITY",
        risk_level=risk_level,
        message=(
            f"Water quality risk detected in {village.name} "
            f"(model confidence {prediction.risk_probability:.0%}): "
            + " ".join(reasons)
        ),
        recommended_action=build_recommended_action(risk_level),
        is_resolved=False
    )

    db.add(alert)
    db.commit()
    db.refresh(alert)

    return AlertCheckResponse(
        village_id=village_id,
        alert_created=True,
        alert=alert,
        reasons=reasons
    )


# ============================================================
# GET ALL ALERTS
# ============================================================

@router.get(
    "/",
    response_model=list[AlertResponse]
)
def get_alerts(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    return (
        db.query(Alert)
        .order_by(Alert.created_at.desc())
        .limit(100)
        .all()
    )


# ============================================================
# GET ALERTS FOR A VILLAGE
# ============================================================

@router.get(
    "/village/{village_id}",
    response_model=list[AlertResponse]
)
def get_village_alerts(
    village_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    village = (
        db.query(Village)
        .filter(Village.id == village_id)
        .first()
    )

    if not village:
        raise HTTPException(
            status_code=404,
            detail="Village not found"
        )

    return (
        db.query(Alert)
        .filter(Alert.village_id == village_id)
        .order_by(Alert.created_at.desc())
        .all()
    )


# ============================================================
# GET UNRESOLVED ALERTS ONLY
# ============================================================

@router.get(
    "/active",
    response_model=list[AlertResponse]
)
def get_active_alerts(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    return (
        db.query(Alert)
        .filter(Alert.is_resolved == False)  # noqa: E712
        .order_by(Alert.created_at.desc())
        .all()
    )


# ============================================================
# RESOLVE AN ALERT
# ============================================================

@router.patch(
    "/{alert_id}/resolve",
    response_model=AlertResponse
)
def resolve_alert(
    alert_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    alert = (
        db.query(Alert)
        .filter(Alert.id == alert_id)
        .first()
    )

    if not alert:
        raise HTTPException(
            status_code=404,
            detail="Alert not found"
        )

    if alert.is_resolved:
        raise HTTPException(
            status_code=400,
            detail="Alert is already resolved"
        )

    alert.is_resolved = True
    alert.resolved_at = datetime.utcnow()

    db.commit()
    db.refresh(alert)

    return alert