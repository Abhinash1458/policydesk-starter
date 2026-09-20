# Phase 3 — reference implementation (instructors)

What a good answer to the Phase 3 prompt looks like when the rules live in `app/routers/claims.py` (the single-file shape
students have after Phase 2, Example 2). Verified end to end: starter + Examples 1-4 + this + Day 2 labs = **80 passed**.

Also add `ClaimStatusUpdate` to the `from app.models import ...` line.

```python
# --------------------------------------------------------------------------- #
# Phase 3 — admin approval workflow
# --------------------------------------------------------------------------- #
ALLOWED_TRANSITIONS: dict[ClaimStatus, set[ClaimStatus]] = {
    ClaimStatus.FILED: {ClaimStatus.UNDER_REVIEW, ClaimStatus.REJECTED},
    ClaimStatus.UNDER_REVIEW: {ClaimStatus.APPROVED, ClaimStatus.REJECTED},
    ClaimStatus.APPROVED: set(),
    ClaimStatus.REJECTED: set(),
}


@router.patch("/{claim_id}/status", response_model=ClaimRead)
def update_claim_status(claim_id: int, payload: ClaimStatusUpdate, session: Session = Depends(get_session)):
    claim = session.get(Claim, claim_id)
    if not claim:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Claim not found")
    if payload.status not in ALLOWED_TRANSITIONS[claim.status]:
        raise HTTPException(
            status.HTTP_409_CONFLICT, f"Cannot move a claim from {claim.status.value} to {payload.status.value}"
        )
    if payload.status == ClaimStatus.APPROVED:
        remaining = remaining_cover(session, claim.policy)
        if claim.amount > remaining:
            raise HTTPException(422, f"Claim amount exceeds remaining cover of {remaining:,.2f}")
    claim.status = payload.status
    if payload.reason:
        claim.reason = payload.reason
    session.add(claim)
    session.commit()
    session.refresh(claim)
    return claim
```

A prompt that reliably produces it:

```
ROLE: senior FastAPI engineer. CONTEXT: #file:app/routers/claims.py #file:app/models.py — ClaimStatusUpdate exists; remaining_cover() exists in this router.
TASK: add PATCH "/{claim_id}/status" -> ClaimRead to the existing router in app/routers/claims.py.
CONSTRAINTS, checked in this order:
 1. session.get(Claim, claim_id) -> 404 "Claim not found"
 2. define ALLOWED_TRANSITIONS: dict[ClaimStatus, set[ClaimStatus]] at module level:
    FILED -> {UNDER_REVIEW, REJECTED}; UNDER_REVIEW -> {APPROVED, REJECTED}; APPROVED -> set(); REJECTED -> set()
    if payload.status not in ALLOWED_TRANSITIONS[claim.status] -> 409 f"Cannot move a claim from {claim.status.value} to {payload.status.value}"
 3. only when payload.status == APPROVED: remaining = remaining_cover(session, claim.policy); if claim.amount > remaining -> 422 f"Claim amount exceeds remaining cover of {remaining:,.2f}"
 4. claim.status = payload.status; if payload.reason: claim.reason = payload.reason  (do not overwrite with None)
 5. add / commit / refresh / return
No new imports beyond adding ClaimStatusUpdate to the existing models import. Do not change file_claim or remaining_cover.
FORMAT: only the new code (the dict and the endpoint).
```

In this branch the same logic lives in `app/services/claims.py` (`ALLOWED_TRANSITIONS`, `can_transition`) and the router
calls it — the layered version. Either passes the tests; show the layered one when asked "where should business rules live?".
