from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import date

class VendorBase(BaseModel):
    name: str = Field(..., example="Acme Corp")
    service: str = Field(..., example="Cloud Storage")
    risk_rating: str = Field(..., example="high")
    dpa_status: str = Field(..., example="draft")
    dpa_expiration_date: Optional[date] = None
    sccs_in_place: bool = False
    soc2_type: str = Field(..., example="type_i")
    cross_border: bool = False
    status: str = Field(..., example="active")
    next_review_date: Optional[date] = None

class VendorCreate(VendorBase):
    pass

class VendorUpdate(VendorBase):
    pass

class VendorRead(VendorBase):
    vendor_id: str = Field(..., alias="id")
    class Config:
        orm_mode = True
        allow_population_by_field_name = True

class VendorAssessmentBase(BaseModel):
    vendor_id: str
    score: int
    notes: Optional[str] = None

class VendorAssessmentCreate(VendorAssessmentBase):
    pass

class VendorAssessmentRead(VendorAssessmentBase):
    assessment_id: str = Field(..., alias="id")
    class Config:
        orm_mode = True
        allow_population_by_field_name = True

class SubprocessorBase(BaseModel):
    vendor_id: str
    name: str
    service: str
    risk_rating: str

class SubprocessorCreate(SubprocessorBase):
    pass

class SubprocessorRead(SubprocessorBase):
    subprocessor_id: str = Field(..., alias="id")
    class Config:
        orm_mode = True
        allow_population_by_field_name = True
