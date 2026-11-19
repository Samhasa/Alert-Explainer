from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from database import get_db
from models import Alert
from schemas import AlertCreate, AlertOut, ExplainResponse
from services.explainer import generate_explanation

router = APIRouter(prefix="/alerts", tags=["alerts"])


@router.post("/", response_model=AlertOut, status_code=status.HTTP_201_CREATED)
def create_alert(alert: AlertCreate, db: Session = Depends(get_db)) -> Alert:
    db_alert = Alert(**alert.model_dump())
    db.add(db_alert)
    db.commit()
    db.refresh(db_alert)
    return db_alert


@router.get("/", response_model=list[AlertOut])
def list_alerts(db: Session = Depends(get_db)) -> list[Alert]:
    return list(db.scalars(select(Alert).order_by(Alert.id)).all())


def get_alert_or_404(alert_id: int, db: Session) -> Alert:
    alert = db.get(Alert, alert_id)
    if alert is None:
        raise HTTPException(status_code=404, detail="Alert not found")
    return alert


@router.get("/{alert_id}", response_model=AlertOut)
def read_alert(alert_id: int, db: Session = Depends(get_db)) -> Alert:
    return get_alert_or_404(alert_id, db)


@router.post("/{alert_id}/explain", response_model=ExplainResponse)
def explain_alert(alert_id: int, db: Session = Depends(get_db)) -> ExplainResponse:
    """Return a rule-based explanation for a specific alert.

    Args:
        alert_id: ID of the alert to explain.
        db: Database session supplied by dependency injection.

    Returns:
        The alert ID, explanation text, and UTC generation timestamp.

    Raises:
        HTTPException: With status 404 and detail "Alert not found" when the
            alert does not exist.
    """
    alert = get_alert_or_404(alert_id, db)
    return ExplainResponse(
        alert_id=alert.id,
        explanation=generate_explanation(alert),
        generated_at=datetime.now(timezone.utc),
    )