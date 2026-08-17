from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.village import Village
from app.schemas.village import VillageCreate, VillageResponse
from app.routes.auth import get_current_user


router = APIRouter(
    prefix="/villages",
    tags=["Villages"]
)


# ============================================================
# CREATE VILLAGE
# ============================================================

@router.post(
    "/",
    response_model=VillageResponse
)
def create_village(
    village_data: VillageCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    village = Village(
        name=village_data.name,
        district=village_data.district,
        state=village_data.state,
        population=village_data.population,
        latitude=village_data.latitude,
        longitude=village_data.longitude
    )

    db.add(village)
    db.commit()
    db.refresh(village)

    return village


# ============================================================
# GET ALL VILLAGES
# ============================================================

@router.get(
    "/",
    response_model=list[VillageResponse]
)
def get_villages(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    return db.query(Village).all()


# ============================================================
# GET ONE VILLAGE
# ============================================================

@router.get(
    "/{village_id}",
    response_model=VillageResponse
)
def get_village(
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

    return village


# ============================================================
# DELETE VILLAGE
# ============================================================

@router.delete("/{village_id}")
def delete_village(
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

    db.delete(village)
    db.commit()

    return {
        "message": "Village deleted successfully"
    }