from datetime import datetime

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    UniqueConstraint,
)

from .database import Base


class Merchant(Base):
    __tablename__ = "merchants"

    id = Column(Integer, primary_key=True, index=True)
    merchant_id = Column(String(50), unique=True, nullable=False, index=True)
    api_key = Column(String(100), unique=True, nullable=False, index=True)

    name = Column(String(150), nullable=False)
    email = Column(String(255), nullable=False)

    onboarding_status = Column(String(50), nullable=False)
    kyc_status = Column(String(50), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

    daily_transaction_limit = Column(Numeric(15, 2), nullable=False)
    per_transaction_limit = Column(Numeric(15, 2), nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class PaymentMethod(Base):
    __tablename__ = "payment_methods"

    id = Column(Integer, primary_key=True, index=True)
    method_id = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=False)

    min_amount = Column(Numeric(15, 2), nullable=False)
    max_amount = Column(Numeric(15, 2), nullable=False)
    processing_fee_percent = Column(Numeric(5, 2), nullable=False)

    is_active = Column(Boolean, default=True, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class MerchantPaymentMethod(Base):
    __tablename__ = "merchant_payment_methods"

    id = Column(Integer, primary_key=True, index=True)

    merchant_id = Column(
        Integer,
        ForeignKey("merchants.id"),
        nullable=False,
    )

    payment_method_id = Column(
        Integer,
        ForeignKey("payment_methods.id"),
        nullable=False,
    )

    custom_fee_percent = Column(Numeric(5, 2), nullable=False)
    is_enabled = Column(Boolean, default=True, nullable=False)
    priority = Column(Integer, nullable=False)

    __table_args__ = (
        UniqueConstraint(
            "merchant_id",
            "payment_method_id",
            name="uq_merchant_payment_method",
        ),
    )


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)

    transaction_id = Column(
        String(100),
        unique=True,
        nullable=False,
        index=True,
    )

    merchant_id = Column(
        Integer,
        ForeignKey("merchants.id"),
        nullable=False,
    )

    payment_method_id = Column(
        Integer,
        ForeignKey("payment_methods.id"),
        nullable=False,
    )

    amount = Column(Numeric(15, 2), nullable=False)
    currency = Column(String(3), nullable=False)

    status = Column(String(50), nullable=False)

    reference_id = Column(String(255), nullable=False)

    customer_email = Column(String(255), nullable=False)
    customer_phone = Column(String(30), nullable=True)

    idempotency_key = Column(
        String(255),
        nullable=False,
        index=True,
    )

    compliance_flag = Column(Boolean, default=False, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    __table_args__ = (
        UniqueConstraint(
            "merchant_id",
            "idempotency_key",
            name="uq_merchant_idempotency_key",
        ),
    )