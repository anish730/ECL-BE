from datetime import datetime

from utils.extensions import db


class BusinessIndustry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    risk_factor = db.Column(db.Float)
    created_at = db.Column(db.DateTime)

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "risk_factor": self.risk_factor,
            "created_at": self.created_at
        }


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=False, nullable=False)
    phone_number = db.Column(db.Integer, unique=False, nullable=False)
    estd_date = db.Column(db.Date, nullable=False)  # can be nullable for non-business users.
    monthly_income = db.Column(db.Float)
    employment_status = db.Column(db.String)
    user_type = db.Column(db.String)  #
    industry_id = db.Column(db.Integer, db.ForeignKey(BusinessIndustry.id), nullable=True)


class LendingType(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String)
    pd_value = db.Column(db.Float)
    lgd_value = db.Column(db.Float)


class Loan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    loan_name = db.Column(db.String)
    user_id = db.Column(db.Integer, db.ForeignKey(User.id), nullable=False)
    loan_term = db.Column(db.Integer, nullable=False)
    loan_amount = db.Column(db.Float)
    lending_type = db.Column(db.Integer, db.ForeignKey(LendingType.id), nullable=False)
    interest_rate = db.Column(db.Float)
    collateral_value = db.Column(db.Float)
    outstanding_balance = db.Column(db.Float)
    un_drawn_commitment = db.Column(db.Float)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now())


class Payment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey(User.id), nullable=False)
    loan_id = db.Column(db.Integer, db.ForeignKey(Loan.id), nullable=False)
    date = db.Column(db.Date, nullable=False)
    amount = db.Column(db.Float)
    status = db.Column(db.String)
    daysLate = db.Column(db.Integer, nullable=True, default=0)  # only if late payment.


class CIBData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey(User.id), nullable=False)
    credit_score = db.Column(db.Float)


# class RiskDecision(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String)
#     parameter = db.Column(db.Float)
#

class ECLThreshold(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    min_value = db.Column(db.Float, nullable=True)  # nullable for open ranges like "<2"
    max_value = db.Column(db.Float, nullable=True)  # nullable for open ranges like ">5"
    level = db.Column(db.String(20))  # "low", "medium", "high"


class PDData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    loan_id = db.Column(db.Integer, db.ForeignKey(Loan.id), nullable=False)
    value = db.Column(db.Float)
    credit_score = db.Column(db.Float)
    history_factor = db.Column(db.Float)
    due_days = db.Column(db.Float)
    industry_risk = db.Column(db.Float)
    year_in_business = db.Column(db.Float)
    lending_type_factor = db.Column(db.Float)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now())


class LGDData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    loan_id = db.Column(db.Integer, db.ForeignKey(Loan.id), nullable=False)
    value = db.Column(db.Float)
    coll_value_impact = db.Column(db.Float)
    recovery_cost = db.Column(db.Float)
    lending_type = db.Column(db.String)
    lending_type_factor = db.Column(db.Float)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now())


class EADData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    loan_id = db.Column(db.Integer, db.ForeignKey(Loan.id), nullable=False)
    value = db.Column(db.Float)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now())


class ECLData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    loan_id = db.Column(db.Integer, db.ForeignKey(Loan.id), nullable=False)
    value = db.Column(db.Float)
    ecl_amount = db.Column(db.Float)
    pd_value = db.Column(db.Float)
    lgd_value = db.Column(db.Float)
    ead_value = db.Column(db.Float)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now())
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.now())
