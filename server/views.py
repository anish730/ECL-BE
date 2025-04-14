from datetime import datetime, date
from operator import and_

from flask.views import MethodView
from flask import request
from marshmallow import ValidationError
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import func
from utils.extensions import db
from server.models import BusinessIndustry, User, RiskDecision, CIBData, Loan, Payment, LendingType, ECLData
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

    def put(self):
        industry_id = request.args.get('id')
        data = request.get_json()
        business_industry = db.session.query(BusinessIndustry).filter_by(id=industry_id).first()
        if not business_industry:
            return not_found_error("Business industry doesn't exists.")
        try:
            for key, value in data.items():
                setattr(business_industry, key, value)
            db.session.commit()
        except SQLAlchemyError as e:
            db.session.rollback()
            return server_error("Error updating data.")
        finally:
            db.session.close()
            return success_response("Business industry updated successfully")


class UserListApi(MethodView):
    def post(self):
        request_data = {
            "name": "John Doe",
            "email": "johndoe@gmail.com",
            "phone_number": 9178356718,
            "estd_date": "2022-10-10",
            "monthly_income": 150000.0,
            "employment_status": "employed",
            "user_type": "Corporate",
            "industry_id": 1
        }
        data = request.get_json()
        customer_schema = CustomerSchema()
        user = db.session.query(User)

        try:
            validated_data = customer_schema.load(data)
        except ValidationError as err:
            return validation_error(err)

        email = data.get('email')
        email_exists = user.filter_by(email=email).first()
        if email_exists:
            return bad_request_error("Email already in use")

        phone_number = data.get('phone_number')
        number_exists = user.filter_by(phone_number=phone_number).first()
        if number_exists:
            return bad_request_error("Phone Number already in use")
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
        # import pdb;pdb.set_trace()
        customers = (
            db.session.query(User)
            .outerjoin(Loan, Loan.user_id == User.id)
            .outerjoin(ECLData, ECLData.loan_id == Loan.id)
            .outerjoin(BusinessIndustry, BusinessIndustry.id == User.industry_id)
            .group_by(User.id).with_entities(User.id,
                User.name.label('name'),
                BusinessIndustry.name.label('business_name'),
                func.count(Loan.id).label("total_loans"),
                func.avg(ECLData.value).label("average_ecl"))
            .all()
        )
        return list_response(customers)

    def put(self):
        user_id = request.args.get('id')
        data = request.get_json()
        user = db.session.query(User).filter_by(id=user_id).first()

        email = data.get('email')
        email_exists = user.filter_by(email=email).first()
        if email_exists:
            return bad_request_error("Email already in use")

        phone_number = data.get('phone_number')
        number_exists = user.filter_by(phone_number=phone_number).first()
        if number_exists:
            return bad_request_error("Phone Number already in use")

        try:
            for key, value in data.items():
                setattr(user, key, value)
            db.session.commit()
        except SQLAlchemyError as e:
            db.session.rollback()
            return server_error("Error updating data.")
        finally:
            db.session.close()
            return success_response("Customer updated successfully")


class RiskDecisionApi(MethodView):
    def post(self):
        request_data = [
            {
                "name": "Low",
                "parameter": 2.5
            },
            {
                "name": "High",
                "parameter": 5.0
            },
            {
                "name": "Medium",
                "parameter": 2.5
            }
        ]
        data = request.get_json()
        try:
            data_objs = []
            for d in data:
                data_obj = RiskDecision(**d)
                data_objs.append(data_obj)
            db.session.bulk_save_objects(data_objs)
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
        data = request.get_json()
        try:
            for d in data:
                risk_id = d.get('id')
                risk_decision = db.session.query(RiskDecision).filter_by(id=risk_id).first()
                if not risk_decision:
                    return not_found_error("Risk Decision parameter doesn't exists.")
                for key, value in d.items():
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
        cib_data = (db.session.query(CIBData)
                    .join(User, User.id == CIBData.user_id)
                    .with_entities(CIBData.id, CIBData.credit_score, User.name, User.id.label('user_id'))).all()
        return list_response(cib_data)

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


class LendingTypeAPI(MethodView):
    def post(self):
        request_data = {
            "type": "personal",
            "pd_value": 2.6,
            "lgd_value": 4.9
        }
        data = request.get_json()
        try:
            data_obj = LendingType(**data)
            db.session.add(data_obj)
            db.session.commit()
        except SQLAlchemyError as e:
            db.session.rollback()
            return server_error("Error creating data.")
        finally:
            db.session.close()
            return success_response("Lending type created successfully")

    def get(self):
        lending_types = db.session.query(LendingType).all()
        return list_response(lending_types)

    def put(self):
        type_id = request.args.get('id')
        data = request.get_json()
        lending_type = db.session.query(LendingType).filter_by(id=type_id).first()
        if not lending_type:
            return not_found_error("Lending type doesn't exists.")
        try:
            for key, value in data.items():
                setattr(lending_type, key, value)
            db.session.commit()
        except SQLAlchemyError as e:
            db.session.rollback()
            return server_error("Error updating data.")
        finally:
            db.session.close()
            return success_response("Lending type updated successfully")


class CustomerLoanApi(MethodView):
    def post(self):
        request_data = {
            "user_id": 1,
            "loan_term": 60,
            "loan_amount": 1000000,
            "lending_type": 1,
            "interest_rate": 1.2,
            "collateral_value": 2000000,
            "outstanding_balance": 1000000,
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
        loan_data = (db.session.query(Loan)
                     .outerjoin(User, User.id == Loan.user_id)
                     .outerjoin(ECLData, Loan.id == ECLData.loan_id)
                     .with_entities(Loan.id, Loan.user_id, Loan.loan_amount, Loan.outstanding_balance, User.name,
                                    ECLData.value, ECLData.ecl_amount, ECLData.updated_at)).all()
        return list_response(loan_data)


class ECLCalculationApi(MethodView):
    def post(self):
        request_data = {
            "user_id": "P12345",
            "loan_id": "id" or None,
            "name": "John Smith",
            "credit_score": 680,
            "industry_name": "N/A",
            "yearInBusiness": 0,
            "daysLate": 15,
            "missed_payments": 1,
            "latePayment": 0,
            "loan_amount": 50000,
            "outstanding_value": 45000,
            "collateralAmount": 700000,
            "collateral_value": 20000,
            "recovery_cost": 0,
            "lendingType": "personal"
        }
        data = request.get_json()
        credit_score = data.get('credit_score')
        user_id = data.get('user_id')
        loan_id = data.get('loan_id')
        industry = data.get('industry_name')
        yearInBusiness = data.get('yearInBusiness')
        recovery_cost = data.get('recovery_cost')
        collateral_value = data.get('collateral_value')
        missed_payments = data.get('missed_payments')
        late_payment = data.get('latePayment')
        collateral_amount = data.get('collateralAmount')
        outstanding_loan_amount = data.get('outstanding_value')
        loan_amount = data.get('loan_amount')
        lending_type = data.get('lendingType')
        #payment_history = db.session.query(Payment).filter(Payment.user_id == user_id)
        # if loan_id:
        #     payment_history = payment_history.filter(Payment.loan_id == loan_id)

        # pd calculation part.
        # missed_payment = payment_history.filter(Payment.status == 'late')
        # missed_count = missed_payment.count()
        daysLate = data.get('daysLate')
        # late_payment = payment_history.order_by(Payment.id.desc())
        # if late_payment:
        #     daysLate = late_payment.daysLate
        # else:
        #     daysLate = 0
        history_factor = (missed_payments * 0.15) + (late_payment * 0.05)

        # past_due_days = missed_payment.with_entities(func.sum(Payment.daysLate)).scalar()

        due_days_factor = (daysLate / 90) * 0.3

        industry_risk = db.session.query(BusinessIndustry).filter_by(name=industry).first().risk_factor
        lending_type_factor = db.session.query(LendingType).filter_by(type=lending_type).first()
        base_score = (850 - credit_score) / 550
        experience_factor = max(0, (0.1 - (yearInBusiness / 100)))
        pd = (base_score + history_factor + due_days_factor + industry_risk - experience_factor) * lending_type_factor.pd_value

        # lgd calculation part
        collateral_ratio = collateral_value / outstanding_loan_amount
        base_lgd = 1 - min(1, collateral_ratio)
        recovery_ratio = recovery_cost / outstanding_loan_amount

        final_lgd = (base_lgd + recovery_ratio) * lending_type_factor.lgd_value #TODO: validate between 0 and 1

        # ead part
        ead = outstanding_loan_amount

        # ecl calculation part
        ecl = pd * final_lgd * ead
        ecl_ratio = ecl / ead
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

        from dateutil.relativedelta import relativedelta
        today = date.today()

        # Calculate the difference
        diff = relativedelta(today, user_data.estd_date)

        # Get the number of full years
        years_diff = diff.years

        if not user_data:
            return not_found_error("User doesn't exists.")
        industry = db.session.query(BusinessIndustry).filter_by(id=user_data.industry_id).first()
        if industry:
            industry_name = industry.name
            industry_risk = industry.risk_factor
        else:
            industry_name = "N/A"
            industry_risk = 0

        cib_data = db.session.query(CIBData).filter_by(user_id=user_id).first()
        if not cib_data:
            credit_score = 0
        else:
            credit_score = cib_data.credit_score

        late_payments = (db.session.query(Payment)
                    .filter(and_(Payment.user_id == user_id, Payment.status == 'late')))
        num_late_payments = late_payments.count()
        # daysLate = late_payments.with_entities(func.sum(Payment.daysLate).label('days_late')).first()
        # if daysLate:
        #     days_late = daysLate.days_late
        # else:
        #     days_late = 0

        missed_payments = late_payments.filter(Payment.daysLate > 90).count()
        daysLate = late_payments.with_entities(func.sum(Payment.daysLate)).scalar()
        if not daysLate:
            daysLate = 0
        # import pdb;
        # pdb.set_trace()
        history_factor = (missed_payments * 0.15) + (daysLate * 0.05)

        loan = db.session.query(Loan).filter_by(user_id=user_id).order_by(Loan.id.desc()).first()
        if loan:
            loan_amount = loan.loan_amount
            collateral_value = loan.collateral_value
            outstanding_value = loan.outstanding_balance
        else:
            loan_amount = 0
            collateral_value = 0
            outstanding_value = 0

        undrawn_commitment = 0  # TODO: change its real value.
        data = {
            "name": user_data.name,
            "estd_date": user_data.estd_date,
            "yearInBusiness": years_diff,
            "industry_name": industry_name,
            "industry_risk": industry_risk,
            "credit_score": credit_score,
            "missed_payments": missed_payments,
            "daysLate": daysLate,
            "latePayment": num_late_payments,
            "historical_default_rate": history_factor,
            "loan_amount": loan_amount,
            "collateral_value": collateral_value,
            "outstanding_value": outstanding_value,
            "undrawn_commitment": undrawn_commitment
        }
        return detail_response(data)


class LoanPaymentsApi(MethodView):
    def post(self):
        request_data = {
            "user_id": 1,
            "loan_id": 1,
            "date": "2022-10-10",
            "amount": 10000,
            "status": "paid",
            "daysLate": 0
        }
        data = request.get_json()
        date = datetime.now()
        data['date'] = date
        # try:
        #     validated_data = loan_schema.load(data)
        # except ValidationError as err:
        #     return validation_error(err)

        # if validated_data.get('collateral_value') <= validated_data.get('loan_amount'):
        #     return bad_request_error("Collateral amount must be greater than the loan amount.")
        try:
            data_obj = Payment(**data)
            db.session.add(data_obj)
            db.session.commit()
        except SQLAlchemyError as e:
            db.session.rollback()
            return server_error("Error creating payment data.")
        finally:
            db.session.close()
            return success_response("Payment added successfully")

    def get(self):
        user_id = request.args.get('user_id')
        loan_id = request.args.get('loan_id')
        payments = db.session.query(Payment).filter_by(user_id=user_id).all()
        return list_response(payments)