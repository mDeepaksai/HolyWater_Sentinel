from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models.village import Village
from app.schemas.village import VillageCreate, VillageResponse


router = APIRouter(
    prefix="/villages",
    tags=["Villages"]
)


def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


@router.post("/", response_model=VillageResponse)
def register_village(
    village: VillageCreate,
    db: Session = Depends(get_db)
):

    existing_village = (
        db.query(Village)
        .filter(
            Village.name == village.name,
            Village.district == village.district
        )
        .first()
    )

    if existing_village:
        raise HTTPException(
            status_code=400,
            detail="Village already registered"
        )

    new_village = Village(
        name=village.name,
        district=village.district,
        state=village.state,
        latitude=village.latitude,
        longitude=village.longitude
    )

    db.add(new_village)
    db.commit()
    db.refresh(new_village)

    return new_village


@router.get("/", response_model=list[VillageResponse])
def get_villages(
    db: Session = Depends(get_db)
):

    villages = db.query(Village).all()

    return villages


@router.get("/{village_id}", response_model=VillageResponse)
def get_village(
    village_id: int,
    db: Session = Depends(get_db)
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