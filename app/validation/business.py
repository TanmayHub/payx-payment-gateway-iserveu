from decimal import Decimal

from app.validation.errors import validation_error


def validate_business_rules(transaction, amount: Decimal):
    payment_method = transaction["payment_method"]
    merchant = transaction["merchant"]

    if amount < payment_method.min_amount:
        return validation_error(
            "RULE_MIN_AMOUNT",
            f"Amount must be at least {payment_method.min_amount}",
            "business_rule",
        )

    if amount > payment_method.max_amount:
        return validation_error(
            "RULE_MAX_AMOUNT",
            f"Amount must not exceed {payment_method.max_amount}",
            "business_rule",
        )

    if amount > merchant.per_transaction_limit:
        return validation_error(
            "RULE_MERCHANT_TRANSACTION_LIMIT",
            "Amount exceeds merchant per-transaction limit",
            "business_rule",
        )

    return None