from decimal import Decimal

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class CustomerRequest(BaseModel):
    email: EmailStr
    phone: str


class TransactionRequest(BaseModel):
    amount: Decimal = Field(gt=0)
    currency: str
    payment_method: str
    reference_id: str
    customer: CustomerRequest

    model_config = ConfigDict(extra="forbid")

    @field_validator("amount")
    @classmethod
    def validate_amount_precision(cls, value: Decimal):
        if value.as_tuple().exponent < -2:
            raise ValueError("amount must have at most 2 decimal places")
        return value

    @field_validator("currency")
    @classmethod
    def validate_currency(cls, value: str):
        if value != "INR":
            raise ValueError("only INR currency is supported")
        return value