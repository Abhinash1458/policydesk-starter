from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from app.db import get_session
from app.models import Customer, CustomerCreate, CustomerRead

router = APIRouter(prefix="/api/customers", tags=["customers"])


@router.get("", response_model=list[CustomerRead])
def list_customers(session: Session = Depends(get_session)):
    return session.exec(select(Customer).order_by(Customer.name)).all()


@router.post("", response_model=CustomerRead, status_code=status.HTTP_201_CREATED)
def create_customer(payload: CustomerCreate, session: Session = Depends(get_session)):
    exists = session.exec(select(Customer).where(Customer.email == payload.email)).first()
    if exists:
        raise HTTPException(status.HTTP_409_CONFLICT, "A customer with this email already exists")
    customer = Customer.model_validate(payload)
    session.add(customer)
    session.commit()
    session.refresh(customer)
    return customer


@router.get("/{customer_id}", response_model=CustomerRead)
def get_customer(customer_id: int, session: Session = Depends(get_session)):
    customer = session.get(Customer, customer_id)
    if not customer:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Customer not found")
    return customer
