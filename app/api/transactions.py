import hashlib
import json
from datetime import datetime, timezone
from decimal import Decimal
from uuid import uuid4

from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Transaction
from app.schemas import TransactionRequest
from app.validation.entity import validate_entity
from app.validation.business import validate_business_rules
from app.validation.compliance import check_compliance
from app.validation.risk import check_velocity
from app.services.events import event_bus



router = APIRouter(prefix="/api/v1", tags=["Transactions"])


def error_response(
    code: str,
    message: str,
    layer: str,
    http_status: int,
):
    raise HTTPException(
        status_code=http_status,
        detail={
            "success": False,
            "error": {
                "code": code,
                "message": message,
                "layer": layer,
                "details": [],
            },
        },
    )


@router.post("/transactions", status_code=201)
def create_transaction(
    request: TransactionRequest,
    x_api_key: str | None = Header(default=None),
    idempotency_key: str | None = Header(default=None),
    db: Session = Depends(get_db),
):
    # -------------------------------------------------
    # AUTHENTICATION
    # -------------------------------------------------

    if not x_api_key:
        error_response(
            "AUTH_API_KEY_MISSING",
            "X-Api-Key header is required",
            "authentication",
            401,
        )

    if not idempotency_key:
        error_response(
            "IDEMPOTENCY_KEY_MISSING",
            "Idempotency-Key header is required",
            "authentication",
            400,
        )

    # -------------------------------------------------
    # ENTITY VALIDATION
    # -------------------------------------------------

    entity, entity_error = validate_entity(
        db,
        x_api_key,
        request.payment_method,
    )

    if entity_error:
        raise HTTPException(
            status_code=403,
            detail=entity_error,
        )
    # -------------------------------------------------
    # REQUEST FINGERPRINT
    # -------------------------------------------------

    request_payload = request.model_dump(mode="json")

    request_fingerprint = hashlib.sha256(
        json.dumps(
            request_payload,
            sort_keys=True,
        ).encode()
    ).hexdigest()

    # -------------------------------------------------
    # IDEMPOTENCY CHECK
    # -------------------------------------------------

    existing = (
        db.query(Transaction)
        .filter(
            Transaction.merchant_id == entity["merchant"].id,
            Transaction.idempotency_key == idempotency_key,
        )
        .first()
    )

    if existing:
        if existing.request_fingerprint != request_fingerprint:
            error_response(
                "IDEMPOTENCY_CONFLICT",
                "Idempotency-Key was already used with a different request",
                "idempotency",
                409,
            )

        return {
            "success": True,
            "data": {
                "transaction_id": existing.transaction_id,
                "status": existing.status,
                "amount": float(existing.amount),
                "currency": existing.currency,
            },
            "metadata": {
                "request_id": str(uuid4()),
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "idempotent": True,
            },
        }
    # -------------------------------------------------
    # BUSINESS RULE VALIDATION
    # -------------------------------------------------

    transaction_context = {
        "merchant": entity["merchant"],
        "payment_method": entity["payment_method"],
        "association": entity["association"],
    }

    business_error = validate_business_rules(
        transaction_context,
        request.amount,
    )

    if business_error:
        raise HTTPException(
            status_code=422,
            detail=business_error,
        )

    # -------------------------------------------------
    # COMPLIANCE
    # -------------------------------------------------

    compliance_flags = check_compliance(request.amount)

    # Compliance does NOT reject the transaction.
    # It only marks the transaction for review.

    # -------------------------------------------------
    # RISK / VELOCITY
    # -------------------------------------------------

    if not check_velocity(entity["merchant"].id):
        error_response(
            "RISK_VELOCITY_LIMIT",
            "Transaction velocity limit exceeded",
            "risk",
            429,
        )

    # -------------------------------------------------
    # CREATE TRANSACTION
    # -------------------------------------------------

    transaction_id = f"txn_{uuid4().hex[:12]}"

    transaction = Transaction(
        transaction_id=transaction_id,
        merchant_id=entity["merchant"].id,
        payment_method_id=entity["payment_method"].id,
        amount=request.amount,
        currency=request.currency,
        status="processing",
        reference_id=request.reference_id,
        customer_email=request.customer.email,
        customer_phone=request.customer.phone,
        idempotency_key=idempotency_key,
        request_fingerprint=request_fingerprint,
        compliance_flag=bool(compliance_flags),
    )

    db.add(transaction)

    try:
        db.commit()
        db.refresh(transaction)

    except Exception:
        db.rollback()

        error_response(
            "TRANSACTION_CREATION_FAILED",
            "Transaction could not be created",
            "transaction",
            500,
        )

    # Publish event after successful transaction creation
    event_bus.publish(
                    "txn:transaction:processing",
                    transaction.transaction_id,
                    transaction.merchant_id,
                    transaction.amount,
                    {
                        "status": transaction.status,
                        "reference_id": transaction.reference_id,
                    },
                )

    return {
        "success": True,
        "data": {
            "transaction_id": transaction.transaction_id,
            "status": transaction.status,
            "amount": float(transaction.amount),
            "currency": transaction.currency,
            "compliance_flag": transaction.compliance_flag,
        },
        "metadata": {
            "request_id": str(uuid4()),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        },
    }
    