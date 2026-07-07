from sqlalchemy import Table, Column, String, ForeignKey
from core.models.base import Base

risk_control = Table(
    'risk_control',
    Base.metadata,
    Column('risk_id', String, ForeignKey('risks.risk_id', ondelete='CASCADE'), primary_key=True),
    Column('control_id', String, ForeignKey('controls.id', ondelete='CASCADE'), primary_key=True)
)

risk_jurisdiction = Table(
    'risk_jurisdiction',
    Base.metadata,
    Column('risk_id', String, ForeignKey('risks.risk_id', ondelete='CASCADE'), primary_key=True),
    Column('jurisdiction_code', String, ForeignKey('jurisdictions.id', ondelete='CASCADE'), primary_key=True)
)

system_control = Table(
    'system_control',
    Base.metadata,
    Column('system_id', String, ForeignKey('assets.id', ondelete='CASCADE'), primary_key=True),
    Column('control_id', String, ForeignKey('controls.id', ondelete='CASCADE'), primary_key=True)
)

process_data_element = Table(
    'process_data_element',
    Base.metadata,
    Column('process_id', String, ForeignKey('assets.id', ondelete='CASCADE'), primary_key=True),
    Column('data_element_id', String, ForeignKey('assets.id', ondelete='CASCADE'), primary_key=True)
)

process_control = Table(
    'process_control',
    Base.metadata,
    Column('process_id', String, ForeignKey('assets.id', ondelete='CASCADE'), primary_key=True),
    Column('control_id', String, ForeignKey('controls.id', ondelete='CASCADE'), primary_key=True)
)
