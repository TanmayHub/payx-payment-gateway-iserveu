from decimal import Decimal


COMPLIANCE_THRESHOLD = Decimal("200000.00")


def check_compliance(amount: Decimal):
    flags = []

    if amount > COMPLIANCE_THRESHOLD:
        flags.append("COMPLIANCE_AMOUNT_REPORTING")

    return flags