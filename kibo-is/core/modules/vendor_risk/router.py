from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from agent_gateway import get_db
from . import models, schemas

router = APIRouter()

@router.post("/vendors", response_model=schemas.VendorRead)
def create_vendor(vendor: schemas.VendorCreate, db: Session = Depends(get_db)):
    db_vendor = models.Vendor(**vendor.dict())
    db.add(db_vendor)
    db.commit()
    db.refresh(db_vendor)
    return db_vendor

@router.get("/vendors/{vendor_id}", response_model=schemas.VendorRead)
def get_vendor(vendor_id: str, db: Session = Depends(get_db)):
    vendor = db.query(models.Vendor).filter(models.Vendor.id == vendor_id).first()
    if not vendor:
        raise HTTPException(status_code=404, detail="Vendor not found")
    return vendor

@router.get("/vendors", response_model=list[schemas.VendorRead])
def list_vendors(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    vendors = db.query(models.Vendor).offset(skip).limit(limit).all()
    return vendors
