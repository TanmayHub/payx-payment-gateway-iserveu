from sqlalchemy.orm import Session

from app.models import Merchant, PaymentMethod, MerchantPaymentMethod
from app.validation.errors import validation_error


def validate_entity(
    db: Session,
    api_key: str,
    payment_method_id: str,
):
    merchant = db.query(Merchant).filter(
        Merchant.api_key == api_key
    ).first()

    if not merchant:
        return None, validation_error(
            "ENTITY_MERCHANT_NOT_FOUND",
            "Merchant does not exist",
            "entity",
        )

    if not merchant.is_active:
        return None, validation_error(
            "ENTITY_MERCHANT_INACTIVE",
            "Merchant is inactive",
            "entity",
        )

    if merchant.kyc_status not in ("approved", "verified"):
        return None, validation_error(
            "ENTITY_KYC_NOT_APPROVED",
            "Merchant KYC is not approved",
            "entity",
        )

    payment_method = db.query(PaymentMethod).filter(
        PaymentMethod.method_id == payment_method_id,
        PaymentMethod.is_active == True,
    ).first()

    if not payment_method:
        return None, validation_error(
            "ENTITY_PAYMENT_METHOD_NOT_FOUND",
            "Payment method does not exist or is inactive",
            "entity",
        )

    association = db.query(MerchantPaymentMethod).filter(
        MerchantPaymentMethod.merchant_id == merchant.id,
        MerchantPaymentMethod.payment_method_id == payment_method.id,
        MerchantPaymentMethod.is_enabled == True,
    ).first()

    if not association:
        return None, validation_error(
            "ENTITY_PAYMENT_METHOD_NOT_ENABLED",
            "Payment method is not enabled for this merchant",
            "entity",
        )

    return {
        "merchant": merchant,
        "payment_method": payment_method,
        "association": association,
    }, None