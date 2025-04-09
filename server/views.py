from flask.views import MethodView
from flask import request
from marshmallow import ValidationError
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import func
from utils.extensions import db
from server.models import BusinessIndustry, User, RiskDecision, CIBData, Loan, Payment
from utils.response import success_response, server_error, list_response, validation_error, not_found_error, \
    detail_response, bad_request_error
from utils.validators import CustomerSchema, LoanSchema


class BusinessIndustryApi(MethodView):
    def post(self):
        data = request.get_json()
        try:
            data_obj = BusinessIndustry(**data)
            db.session.add(data_obj)
            db.session.commit()
        except SQLAlchemyError as e:
            db.session.rollback()
            return server_error("Error creating data.")
        finally:
            db.session.close()
            return success_response("Data uploaded successfully")

    def get(self):
        data = db.session.query(BusinessIndustry).all()
        return list_response(data)


class UserListApi(MethodView):
    def post(self):
        request_data = {
            "name": "John Doe",
            "email": "johndoe@gmail.com",
            "phone_number": 9178356718,
            "estd_date": "2022-10-10",
            "monthly_income": 150000.0,
            "employment_status": "employed",
            "user_type": "Corporate"
        }
        data = request.get_json()
        customer_schema = CustomerSchema()
        try:
            validated_data = customer_schema.load(data)
        except ValidationError as err:
            return validation_error(err)

        try:
            data_obj = User(**validated_data)
            db.session.add(data_obj)
            db.session.commit()
        except SQLAlchemyError as e:
            db.session.rollback()
            return server_error("Error creating new customer.")
        finally:
            db.session.close()
            return success_response("New Customer created successfully")

    def get(self):
        customers = db.session.query(User).all()
        return list_response(customers)


class RiskDecisionApi(MethodView):
    def post(self):
        request_data = {
            "name": "High",
            "parameter": 2.5
        }
        data = request.get_json()
        try:
            data_obj = RiskDecision(**data)
            db.session.add(data_obj)
            db.session.commit()
        except SQLAlchemyError as e:
            db.session.rollback()
            return server_error("Error creating data.")
        finally:
            db.session.close()
            return success_response("Risk decision parameter added successfully")

    def get(self):
        risk_decision = db.session.query(RiskDecision).all()
        return list_response(risk_decision)

    def put(self):
        risk_id = request.args.get('risk_id')
        data = request.get_json()
        risk_decision = db.session.query(RiskDecision).filter_by(id=risk_id).first()
        if not risk_decision:
            return not_found_error("Risk Decision parameter doesn't exists.")
        try:
            for key, value in data.items():
                setattr(risk_decision, key, value)
            db.session.commit()
        except SQLAlchemyError as e:
            db.session.rollback()
            return server_error("Error updating data.")
        finally:
            db.session.close()
            return success_response("Risk decision parameter updated successfully")


class FetchCIBData(MethodView):
    def get(self):
        user_id = request.args.get('user_id')
        cib_data = db.session.query(CIBData).filter_by(user_id=user_id).first()
        return detail_response(cib_data)

    def post(self):
        data = request.get_json()
        credit_score = data.get('credit_score')
        user_id = data.get('user_id')
        try:
            data_obj = CIBData(
                user_id=user_id,
                credit_score=credit_score
            )
            db.session.add(data_obj)
            db.session.commit()
        except SQLAlchemyError as e:
            db.session.rollback()
            return server_error("Error creating data.")
        finally:
            db.session.close()
            return success_response("CIB data posted successfully")

    def put(self):
        data = request.get_json()
        credit_score = data.get('credit_score')
        user_id = data.get('user_id')
        cib_id = request.args.get('id')
        cib_data = db.session.query(CIBData).filter_by(id=cib_id, user_id=user_id).first()
        if not cib_data:
            return not_found_error("CIB data not found for the user.")
        try:
            cib_data.credit_score = credit_score
            db.session.commit()
        except SQLAlchemyError as e:
            db.session.rollback()
            return server_error("Error updating data.")
        finally:
            db.session.close()
            return success_response("CIB data updated successfully")


class CustomerLoanApi(MethodView):
    def post(self):
        request_data = {
            "user_id": 1,
            "loan_term": 60,
            "loan_amount": 1000000,
            "lending_type": "type",
            "interest_rate": 1.2,
            "collateral_value": 2000000,
            "outstanding_balance": 1000000,
            "lending_type_factor": 3.7
        }
        #TODO: calculate lending_type_factor based on lending_type.
        data = request.get_json()
        loan_schema = LoanSchema()
        try:
            validated_data = loan_schema.load(data)
        except ValidationError as err:
            return validation_error(err)

        if validated_data.get('collateral_value') <= validated_data.get('loan_amount'):
            return bad_request_error("Collateral amount must be greater than the loan amount.")

        try:
            data_obj = Loan(**validated_data)
            db.session.add(data_obj)
            db.session.commit()
        except SQLAlchemyError as e:
            db.session.rollback()
            return server_error("Error creating loan data.")
        finally:
            db.session.close()
            return success_response("Loan created successfully")

    def get(self):
        loan_data = db.session.query(Loan).all()
        return list_response(loan_data)


class ECLCalculationApi(MethodView):
    def post(self):
        request_data = {
            "user_id": "P12345",
            "loan_id": "id" or None,
            "name": "John Smith",
            "creditScore": 680,
            "industry": "N/A",
            "yearInBusiness": 0,
            "pastDueDays": 5,
            "loanAmount": 50000,
            "outstandingBalance": 45000,
            "collateralValue": 20000,
            "interestRate": 8.5,
            "loanTerm": 60,  # 5years
            "lendingType": "personal",
            "employmentStatus": "employed",
            "monthlyIncome": 6500,
        }
        data = request.get_json()
        credit_score = data.get('credit_score')
        user_id = data.get('user_id')
        loan_id = data.get('loan_id')
        industry = data.get('industry')
        yearInBusiness = data.get('yearInBusiness')
        recovery_cost = data.get('recovery_cost')
        collateral_value = data.get('collateralValue')
        outstanding_loan_amount = data.get('outstandingBalance')
        loan_amount = data.get('loanAmount')
        payment_history = db.session.query(Payment).filter(Payment.user_id == user_id)
        if loan_id:
            payment_history = payment_history.filter(Payment.loan_id == loan_id)

        # pd calculation part.
        missed_payment = payment_history.filter(Payment.status == 'late')
        missed_count = missed_payment.count()
        late_payment = payment_history.order_by(Payment.id.desc())
        daysLate = late_payment.daysLate
        history_factor = (missed_count * 0.15) + (daysLate * 0.05)

        past_due_days = missed_payment.with_entites(func.sum(Payment.daysLate)).scalar()
        due_days_factor = past_due_days / 90
        industry_risk = db.session.query(BusinessIndustry).filter_by(name=industry).first().risk_factor
        lending_type_factor = 0
        pd = (credit_score + history_factor + due_days_factor + industry_risk - yearInBusiness) * lending_type_factor

        # lgd calculation part
        collateral_ratio = collateral_value / outstanding_loan_amount
        base_lgd = 1 - min(1, collateral_ratio)
        final_lgd = (base_lgd + recovery_cost) * lending_type_factor

        # ead part
        ead = outstanding_loan_amount

        # ecl calculation part
        ecl = pd * final_lgd * ead
        ecl_ratio = ecl / loan_amount
        if ecl_ratio < 2:
            risk = "Low risk"
        elif ecl_ratio in range(2, 6):
            risk = "Medium risk"
        else:
            risk = "High risk"

        data = {
            "ecl_amount": ecl,
            "ecl_percentage": ecl_ratio,
            "risk": risk,
            "pd": pd,
            "lgd": final_lgd,
            "ead": ead
        }
        return success_response("Success", data)

    def get(self):
        user_id = request.args.get('user_id')
        user_data = db.session.query(User).filter_by(id=user_id).first()
        industry = db.session.query(BusinessIndustry).filter_by(id=user_data.industry_id).first()
        if industry:
            industry_name = industry.name
            industry_risk = industry.risk_factor
        else:
            industry_name = "N/A"
            industry_risk = 0

        cib_data = db.session.query(CIBData).filter_by(user_id=user_id).first()
        credit_score = cib_data.credit_score

        payments = (db.session.query(Payment)
                    .filter(Payment.user_id == user_id))
        missed_payments = payments.filter(Payment.status == 'late').count()
        late_payment = payments.order_by(Payment.id.desc()).first()
        days_late = late_payment.daysLate
        history_factor = (missed_payments * 0.15) + (days_late * 0.05)

        loan = db.session.query(Loan).filter_by(user_id=user_id).order_by(Loan.id.desc()).first()
        loan_amount = loan.loan_amount
        collateral_value = loan.collateral_value
        outstanding_value = loan.outstanding_balance
        undrawn_commitment = 0  # TODO: check its real value.
        data = {
            "name": user_data.name,
            "estd_date": user_data.estd_date,
            "industry_name": industry_name,
            "industry_risk": industry_risk,
            "credit_score": credit_score,
            "missed_payments": missed_payments,
            "historical_default_rate": history_factor,
            "loan_amount": loan_amount,
            "collateral_value": collateral_value,
            "outstanding_value": outstanding_value,
            "undrawn_commitment": undrawn_commitment
        }
        return detail_response(data)

