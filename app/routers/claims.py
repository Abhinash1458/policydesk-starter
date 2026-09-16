"""Claims API.   *** LAB 3: YOUR CODE HERE ***

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
    # TODO (Lab 3): look up the policy (404), build Claim.model_validate(payload), run
    #                       claim_rules.validate_claim(...), handle the two kinds of error, save and return.
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED, "TODO Lab 3: implement file_claim in app/routers/claims.py")


@router.get("", response_model=list[ClaimRead])
def list_claims(policy_id: int | None = None, session: Session = Depends(get_session)):
    stmt = select(Claim).order_by(Claim.created_at.desc())
    if policy_id:
        stmt = stmt.where(Claim.policy_id == policy_id)
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
    # TODO (Lab 3): 404 if missing; 409 unless claim_rules.can_transition(...); when approving, 422 if
    #                       claim.amount > claim_rules.remaining_cover(session, claim.policy); then save status + reason.
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED, "TODO Lab 3: implement update_claim_status")
