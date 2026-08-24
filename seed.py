from decimal import Decimal

from sqlalchemy import delete

from app.database import Base, SessionLocal, engine
from app.models import (
    Merchant,
    PaymentMethod,
    MerchantPaymentMethod,
    Transaction,
)


def seed_database():
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()

    try:
        # Clear existing data
        db.execute(delete(MerchantPaymentMethod))
        db.execute(delete(Transaction))
        db.execute(delete(Merchant))
        db.execute(delete(PaymentMethod))
        db.commit()

        # -------------------------
        # Payment Methods
        # -------------------------

        payment_methods = [
            PaymentMethod(
                method_id="upi",
                name="UPI",
                min_amount=Decimal("1.00"),
                max_amount=Decimal("200000.00"),
                processing_fee_percent=Decimal("0.00"),
                is_active=True,
            ),
            PaymentMethod(
                method_id="credit_card",
                name="Credit Card",
                min_amount=Decimal("100.00"),
                max_amount=Decimal("500000.00"),
                processing_fee_percent=Decimal("2.50"),
                is_active=True,
            ),
            PaymentMethod(
                method_id="debit_card",
                name="Debit Card",
                min_amount=Decimal("100.00"),
                max_amount=Decimal("200000.00"),
                processing_fee_percent=Decimal("1.80"),
                is_active=True,
            ),
            PaymentMethod(
                method_id="netbanking",
                name="Net Banking",
                min_amount=Decimal("10.00"),
                max_amount=Decimal("1000000.00"),
                processing_fee_percent=Decimal("1.20"),
                is_active=True,
            ),
            PaymentMethod(
                method_id="wallet",
                name="Digital Wallet",
                min_amount=Decimal("10.00"),
                max_amount=Decimal("100000.00"),
                processing_fee_percent=Decimal("1.50"),
                is_active=True,
            ),
        ]

        db.add_all(payment_methods)
        db.flush()

        # -------------------------
        # Merchants
        # -------------------------

        merchants = [
            Merchant(
                merchant_id="test_merchant_001",
                api_key="test_key_merchant_001",
                name="Active Test Merchant",
                email="merchant001@example.com",
                onboarding_status="activated",
                kyc_status="approved",
                daily_transaction_limit=Decimal("1000000.00"),
                per_transaction_limit=Decimal("500000.00"),
                is_active=True,
            ),
            Merchant(
                merchant_id="test_merchant_002",
                api_key="test_key_merchant_002",
                name="Active Merchant #2",
                email="merchant002@example.com",
                onboarding_status="activated",
                kyc_status="verified",
                daily_transaction_limit=Decimal("500000.00"),
                per_transaction_limit=Decimal("200000.00"),
                is_active=True,
            ),
            Merchant(
                merchant_id="inactive_merchant",
                api_key="test_key_inactive_merchant",
                name="Inactive Test Merchant",
                email="inactive@example.com",
                onboarding_status="review",
                kyc_status="approved",
                daily_transaction_limit=Decimal("100000.00"),
                per_transaction_limit=Decimal("50000.00"),
                is_active=False,
            ),
            Merchant(
                merchant_id="pending_kyc_merchant",
                api_key="test_key_pending_kyc",
                name="Pending KYC Merchant",
                email="pendingkyc@example.com",
                onboarding_status="activated",
                kyc_status="pending",
                daily_transaction_limit=Decimal("50000.00"),
                per_transaction_limit=Decimal("10000.00"),
                is_active=True,
            ),
            Merchant(
                merchant_id="not_started_kyc",
                api_key="test_key_not_started",
                name="Not Started KYC",
                email="notstarted@example.com",
                onboarding_status="activated",
                kyc_status="not_started",
                daily_transaction_limit=Decimal("10000.00"),
                per_transaction_limit=Decimal("5000.00"),
                is_active=True,
            ),
        ]

        db.add_all(merchants)
        db.flush()

        # -------------------------
        # Merchant-Payment Methods
        # -------------------------

        active_merchant = merchants[0]

        upi = payment_methods[0]
        credit_card = payment_methods[1]
        netbanking = payment_methods[3]

        associations = [
            MerchantPaymentMethod(
                merchant_id=active_merchant.id,
                payment_method_id=upi.id,
                custom_fee_percent=Decimal("0.00"),
                is_enabled=True,
                priority=1,
            ),
            MerchantPaymentMethod(
                merchant_id=active_merchant.id,
                payment_method_id=credit_card.id,
                custom_fee_percent=Decimal("2.50"),
                is_enabled=True,
                priority=2,
            ),
            MerchantPaymentMethod(
                merchant_id=active_merchant.id,
                payment_method_id=netbanking.id,
                custom_fee_percent=Decimal("1.20"),
                is_enabled=True,
                priority=3,
            ),
        ]

        db.add_all(associations)
        db.flush()

        # -------------------------
        # Historical transactions
        # -------------------------

        historical_transactions = [
            Transaction(
                transaction_id="txn_test_001",
                merchant_id=active_merchant.id,
                payment_method_id=upi.id,
                amount=Decimal("1500.00"),
                currency="INR",
                status="settled",
                reference_id="ORDER-SEED-001",
                customer_email="customer1@example.com",
                customer_phone="+919876543210",
                idempotency_key="seed-idem-001",
                compliance_flag=False,
            ),
            Transaction(
                transaction_id="txn_test_002",
                merchant_id=active_merchant.id,
                payment_method_id=credit_card.id,
                amount=Decimal("5000.00"),
                currency="INR",
                status="processing",
                reference_id="ORDER-SEED-002",
                customer_email="customer2@example.com",
                customer_phone=None,
                idempotency_key="seed-idem-002",
                compliance_flag=False,
            ),
        ]

        db.add_all(historical_transactions)

        db.commit()

        print("✅ Database seeded successfully")
        print(f"Payment methods: {len(payment_methods)}")
        print(f"Merchants: {len(merchants)}")
        print(f"Associations: {len(associations)}")
        print(f"Historical transactions: {len(historical_transactions)}")

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    seed_database()