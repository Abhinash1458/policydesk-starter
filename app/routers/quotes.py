"""Quotes API.   *** LAB 4: YOUR CODE HERE ***

POST /api/quotes  -> look up the customer and product, run the premium calculator, save the quote.
    404 if customer or product does not exist
    422 if the pricing rules reject the request (PricingError)
    201 with the saved QuoteRead on success
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from app.db import get_session
from app.models import Customer, Product, Quote, QuoteCreate, QuoteRead
from app.services import pricing

router = APIRouter(prefix="/api/quotes", tags=["quotes"])


def price_quote(payload: QuoteCreate, session: Session) -> tuple[float, Customer, Product]:
    """Shared by the API and the HTML form: look up customer/product, run the calculator.

    Returns (premium, customer, product). Raise HTTPException with the right status code on failure.
    """
    # TODO (Lab 4):
    #   1. session.get(Customer, ...) and session.get(Product, ...) -> 404 if missing
    #   2. age = pricing.age_on(customer.date_of_birth)
    #   3. premium = pricing.calculate_premium(...)  (pass the product's base_rate, code, min/max)
    #   4. catch pricing.PricingError -> HTTPException(422, str(exc))
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED, "TODO Lab 4: implement price_quote in app/routers/quotes.py")


@router.get("", response_model=list[QuoteRead])
def list_quotes(session: Session = Depends(get_session)):
    return session.exec(select(Quote).order_by(Quote.created_at.desc())).all()


@router.post("", response_model=QuoteRead, status_code=status.HTTP_201_CREATED)
def create_quote(payload: QuoteCreate, session: Session = Depends(get_session)):
    # TODO (Lab 4): premium, _, _ = price_quote(payload, session); build a Quote(**payload.model_dump(), premium=...),
    #               add / commit / refresh, return it.
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED, "TODO Lab 4: implement create_quote")


@router.get("/{quote_id}", response_model=QuoteRead)
def get_quote(quote_id: int, session: Session = Depends(get_session)):
    quote = session.get(Quote, quote_id)
    if not quote:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Quote not found")
    return quote
