from datetime import datetime

from sqlalchemy import func
from utils.extensions import db
from server.models import CIBData, Payment, BusinessIndustry, User, Loan, ECLThreshold


def calculate_pd(user_id, loan_id=None):
    cib_data = db.session.query(CIBData).filter_by(user_id=user_id).first()
    if cib_data:
        credit_score = cib_data.credit_score
    else:
        credit_score = 0

    payment_history = db.session.query(Payment).filter(Payment.user_id == user_id)
    if loan_id:
        payment_history = payment_history.filter(Payment.loan_id == loan_id)

    missed_payment = payment_history.filter(Payment.status == 'late')
    missed_count = missed_payment.count()
    late_payment = payment_history.order_by(Payment.id.desc())
    daysLate = late_payment.daysLate
    history_factor = (missed_count * 0.15) + (daysLate * 0.05)

    past_due_days = missed_payment.with_entites(func.sum(Payment.daysLate)).scalar()
    due_days_factor = past_due_days / 90

    industry = (db.session.query(BusinessIndustry.risk_factor, User.estd_date)
                     .join(User, User.industry_id == BusinessIndustry.id)
                     .filter(User.id == user_id).first())
    industry_risk = industry.risk_factor
    years_in_business = datetime.now() - industry.estd_date
    lending_type_factor = 0

    pd = (credit_score + history_factor + due_days_factor + industry_risk - years_in_business) * lending_type_factor
    return pd


def calculate_lgd(recovery_cost, lending_type, loan_id=None, collateral_amt=None, outstanding_loan_amount=None):
    if loan_id:
        loan = db.session.query(Loan).filter_by(id=loan_id).first()
        collateral_amt = loan.collateral_value
        outstanding_loan_amount = loan.outstanding_balance
    collateral_ratio = collateral_amt / outstanding_loan_amount
    base_lgd = 1 - min(1, collateral_ratio)
    final_lgd = (base_lgd + recovery_cost) * lending_type

    return final_lgd


def calculate_ecl(pd, lgd, ead, loan_amount=None, loan_id=None):
    if loan_id:
        loan = db.session.query(Loan).filter_by(id=loan_id).first()
        loan_amount = loan.loan_amount

    ecl = pd * lgd * ead
    ecl_ratio = ecl / loan_amount

    return ecl_ratio


def get_risk_level(value):
    thresholds = ECLThreshold.query.all()
    for threshold in thresholds:
        if threshold.min_value is None and value < threshold.max_value:
            return threshold.level
        elif threshold.max_value is None and value >= threshold.min_value:
            return threshold.level
        elif threshold.min_value is not None and threshold.max_value is not None:
            if threshold.min_value <= value < threshold.max_value:
                return threshold.level
    return "unknown"