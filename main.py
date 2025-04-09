from flask import Flask
from server import views
from utils.encoder import DobatoEncoder
from utils.extensions import db


def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///../instance/app.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    with app.app_context():
        db.create_all()

    return app


app = create_app()
app.json = DobatoEncoder(app)
app.add_url_rule('/api/v1/users', view_func=views.UserListApi.as_view('ecl-users-api'))
app.add_url_rule('/api/v1/business-industry', view_func=views.BusinessIndustryApi.as_view('business-industry-api'))
app.add_url_rule('/api/v1/risk-decisions', view_func=views.RiskDecisionApi.as_view('risk-decisions'))
app.add_url_rule('/api/v1/cib-data', view_func=views.FetchCIBData.as_view('cib-data'))
app.add_url_rule('/api/v1/loans', view_func=views.CustomerLoanApi.as_view('customer-loans'))
app.add_url_rule('/api/v1/ecl-calculation', view_func=views.ECLCalculationApi.as_view('ecl-calculations'))


if __name__ == '__main__':
    app.run(debug=True)