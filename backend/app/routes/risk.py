from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.village import Village
from app.models.risk_prediction import RiskPrediction
from app.models.risk_factor import RiskFactor
from app.schemas.risk import (
    RiskPredictionResponse,
    RiskPredictionWithFactors,
)
from app.routes.auth import get_current_user
from app.services.prediction_service import run_prediction_for_village


router = APIRouter(
    prefix="/risk",
    tags=["Risk Prediction"]
)


# ============================================================
# RUN A PREDICTION FOR A VILLAGE
# ============================================================

@router.post(
    "/predict/{village_id}",
    response_model=RiskPredictionWithFactors
)
def predict_village_risk(
    village_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    prediction, factors, _village = run_prediction_for_village(village_id, db)

    return RiskPredictionWithFactors(
        prediction=prediction,
        factors=factors
    )


# ============================================================
# GET PREDICTION HISTORY FOR A VILLAGE
# ============================================================

@router.get(
    "/village/{village_id}",
    response_model=list[RiskPredictionResponse]
)
def get_village_risk_history(
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
        db.query(RiskPrediction)
        .filter(RiskPrediction.village_id == village_id)
        .order_by(RiskPrediction.predicted_at.desc())
        .all()
    )


# ============================================================
# GET A SINGLE PREDICTION WITH ITS FACTORS
# ============================================================

@router.get(
    "/{prediction_id}",
    response_model=RiskPredictionWithFactors
)
def get_prediction_with_factors(
    prediction_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    prediction = (
        db.query(RiskPrediction)
        .filter(RiskPrediction.id == prediction_id)
        .first()
    )

    if not prediction:
        raise HTTPException(
            status_code=404,
            detail="Risk prediction not found"
        )

    factors = (
        db.query(RiskFactor)
        .filter(RiskFactor.risk_prediction_id == prediction_id)
        .order_by(RiskFactor.contribution.desc())
        .all()
    )

    return RiskPredictionWithFactors(
        prediction=prediction,
        factors=factors
    )