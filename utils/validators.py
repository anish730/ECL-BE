from marshmallow import Schema, fields, validate, ValidationError


def validate_phone_number(value):
    """Ensure phone number is a 10-digit integer."""
    if not (1000000000 <= value <= 9999999999):  # Must be within 10-digit range
        raise ValidationError("Phone number must be exactly 10 digits.")


class CustomerSchema(Schema):
    name = fields.String(required=True)
    email = fields.Email(required=False, allow_none=True)  # Built-in email validation
    phone_number = fields.Integer(required=True, validate=validate_phone_number)  # Ensures exactly 10 digits
    estd_date = fields.Date(required=True)
    monthly_income = fields.Decimal(required=True)
    employment_status = fields.String(required=True)
    user_type = fields.String(required=True)
    industry_id = fields.Integer(required=False, allow_none=True)


class LoanSchema(Schema):
    user_id = fields.Integer(required=True)
    loan_term = fields.Integer(required=True)
    loan_amount = fields.Decimal(required=True)
    lending_type = fields.Integer(required=True)
    interest_rate = fields.Decimal(required=True)
    collateral_value = fields.Decimal(required=True)
    outstanding_balance = fields.Decimal(required=True)
    un_drawn_commitment = fields.Decimal(required=False, allow_none=True)