"""Claims API.

POST  /api/claims               -> file a claim (201). Runs services.claims.validate_claim:
                                     ClaimValidationError with auto_reject  -> save the claim as Rejected, reason = message
                                     ClaimValidationError otherwise         -> 422 with the message
                                     404 if the policy does not exist
PATCH /api/claims/{id}/status   -> move a claim through the workflow:
                                     409 if the transition is not allowed (services.claims.can_transition)
                                     422 when approving more than the remaining cover
                                     reason is stored alongside the status
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from app.db import get_session
from app.models import Claim, ClaimCreate, ClaimRead, ClaimStatus, ClaimStatusUpdate, Policy
from app.services import claims as claim_rules

router = APIRouter(prefix="/api/claims", tags=["claims"])


def file_claim(payload: ClaimCreate, session: Session) -> Claim:
    """Shared by the API and the HTML form."""
    policy = session.get(Policy, payload.policy_id)
    if not policy:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Policy not found")

    claim = Claim.model_validate(payload)
    try:
        claim_rules.validate_claim(
            session,
            policy,
            amount=payload.amount,
            incident_date=payload.incident_date,
            vehicle_registration=payload.vehicle_registration,
        )
    except claim_rules.ClaimValidationError as exc:
        if not exc.auto_reject:
            raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, str(exc)) from exc
        claim.status = ClaimStatus.REJECTED
        claim.reason = str(exc)

    session.add(claim)
    session.commit()
    session.refresh(claim)
    return claim


@router.get("", response_model=list[ClaimRead])
def list_claims(
    policy_id: int | None = None,
    status: ClaimStatus | None = None,
    session: Session = Depends(get_session),
):
    """List claims, newest first. `?status=Filed` is the admin's review queue."""
    stmt = select(Claim).order_by(Claim.created_at.desc())
    if policy_id:
        stmt = stmt.where(Claim.policy_id == policy_id)
    if status:
        stmt = stmt.where(Claim.status == status)
    return session.exec(stmt).all()


@router.post("", response_model=ClaimRead, status_code=status.HTTP_201_CREATED)
def create_claim(payload: ClaimCreate, session: Session = Depends(get_session)):
    return file_claim(payload, session)


@router.get("/{claim_id}", response_model=ClaimRead)
def get_claim(claim_id: int, session: Session = Depends(get_session)):
    claim = session.get(Claim, claim_id)
    if not claim:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Claim not found")
    return claim


@router.patch("/{claim_id}/status", response_model=ClaimRead)
def update_claim_status(claim_id: int, payload: ClaimStatusUpdate, session: Session = Depends(get_session)):
    claim = session.get(Claim, claim_id)
    if not claim:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Claim not found")
    if not claim_rules.can_transition(claim.status, payload.status):
        raise HTTPException(
            status.HTTP_409_CONFLICT, f"Cannot move a claim from {claim.status.value} to {payload.status.value}"
        )
    if payload.status == ClaimStatus.APPROVED:
        remaining = claim_rules.remaining_cover(session, claim.policy)
        if claim.amount > remaining:
            raise HTTPException(
                status.HTTP_422_UNPROCESSABLE_ENTITY,
                f"Claim amount exceeds remaining cover of {remaining:,.2f}",
            )
    claim.status = payload.status
    if payload.reason:
        claim.reason = payload.reason
    session.add(claim)
    session.commit()
    session.refresh(claim)
    return claim
