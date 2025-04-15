from flask import Flask
from flask_cors import CORS
from flasgger import Swagger
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
swagger = Swagger(app, template_file='swagger.yaml')
CORS(app, resources={r"/*": {"origins": "*", "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
                             "headers": ["Content-Type", "Authorization", "ngrok-skip-browser-warning"]}})
app.json = DobatoEncoder(app)
app.add_url_rule('/api/v1/users', view_func=views.UserListApi.as_view('ecl-users-api'))
app.add_url_rule('/api/v1/business-industry', view_func=views.BusinessIndustryApi.as_view('business-industry-api'))
app.add_url_rule('/api/v1/risk-decisions', view_func=views.RiskThresholdApi.as_view('risk-decisions'))
app.add_url_rule('/api/v1/cib-data', view_func=views.FetchCIBData.as_view('cib-data'))
app.add_url_rule('/api/v1/loans', view_func=views.CustomerLoanApi.as_view('customer-loans'))
app.add_url_rule('/api/v1/payments', view_func=views.LoanPaymentsApi.as_view('loan-payments'))
app.add_url_rule('/api/v1/ecl-calculation', view_func=views.ECLCalculationApi.as_view('ecl-calculations'))
app.add_url_rule('/api/v1/lending-types', view_func=views.LendingTypeAPI.as_view('lending-types-api'))


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)