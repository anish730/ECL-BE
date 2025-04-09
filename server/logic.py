from flask import Flask, request, jsonify
import datetime

app = Flask(__name__)

# In-memory storage for borrowers and loan data (replace with DB in production)
borrowers = {}
loan_data = {}


# Mock external API data (replace with real API calls in production)
def fetch_mock_credit_score(borrower_id):
    return 680  # Example credit score


def fetch_mock_bank_data(borrower_id):
    return {
        "monthly_income": 6500,
        "transaction_history": ["paid", "paid", "late", "paid", "paid", "paid"]
    }


def fetch_mock_lms_history(borrower_id):
    return {
        "past_due_days": 5,
        "outstanding_balance": 45000,
        "collateral_value": 20000
    }


# Step 1: Data Collection
def collect_borrower_data(borrower_id, loan_application):
    credit_score = fetch_mock_credit_score(borrower_id)
    bank_data = fetch_mock_bank_data(borrower_id)
    lms_data = fetch_mock_lms_history(borrower_id)

    borrower_data = {
        "id": borrower_id,
        "name": loan_application.get("name"),
        "credit_score": credit_score,
        "loan_amount": loan_application.get("loan_amount"),
        "outstanding_balance": lms_data["outstanding_balance"],
        "collateral_value": lms_data["collateral_value"],
        "past_due_days": lms_data["past_due_days"],
        "monthly_income": bank_data["monthly_income"],
        "payment_history": bank_data["transaction_history"]
    }
    borrowers[borrower_id] = borrower_data
    return borrower_data


# Step 2: ECL Computation
def calculate_ecl(borrower_data):
    # Probability of Default (PD)
    credit_factor = 0.05 if borrower_data["credit_score"] > 700 else 0.072
    payment_factor = 0.01 * sum(1 for p in borrower_data["payment_history"] if p == "late")
    pd = min(credit_factor + payment_factor, 1.0)  # Cap at 100%

    # Loss Given Default (LGD)
    collateral_ratio = borrower_data["collateral_value"] / borrower_data["outstanding_balance"]
    base_lgd = 1 - collateral_ratio
    lgd = max(base_lgd + 0.1, 0.3)  # Add recovery cost, minimum 30%

    # Exposure at Default (EAD)
    ead = borrower_data["outstanding_balance"]

    # ECL Calculation
    ecl = pd * lgd * ead
    ecl_percentage = (ecl / borrower_data["loan_amount"]) * 100

    return {"ecl": ecl, "ecl_percentage": ecl_percentage, "pd": pd, "lgd": lgd, "ead": ead}


# Step 3: Loan Decisioning
def get_risk_level_and_recommendation(ecl_percentage):
    if ecl_percentage < 2:
        return "low", "Auto-approve at standard interest rates."
    elif ecl_percentage <= 5:
        return "medium", "Additional verification required or consider higher interest rates."
    else:
        return "high", "Suggest rejection or consider alternative loan structure."


# Step 4: Loan Monitoring (Simplified EWS)
def monitor_loan(borrower_id):
    borrower = borrowers.get(borrower_id)
    if not borrower:
        return {"error": "Borrower not found"}

    # Mock new data fetch
    new_past_due_days = borrower["past_due_days"] + 5  # Simulate worsening
    ecl_data = calculate_ecl(borrower)
    risk_level, recommendation = get_risk_level_and_recommendation(ecl_data["ecl_percentage"])

    alert = "No alert"
    if new_past_due_days > 10 or ecl_data["ecl_percentage"] > 5:
        alert = "Early warning: Increased risk detected."

    return {
        "borrower_id": borrower_id,
        "updated_ecl_percentage": ecl_data["ecl_percentage"],
        "risk_level": risk_level,
        "recommendation": recommendation,
        "alert": alert
    }


# API Endpoints
@app.route("/api/loan/apply", methods=["POST"])
def apply_loan():
    data = request.get_json()
    borrower_id = data.get("borrower_id", f"B{len(borrowers) + 1}")
    loan_application = {
        "name": data.get("name"),
        "loan_amount": data.get("loan_amount")
    }

    # Collect data and calculate ECL
    borrower_data = collect_borrower_data(borrower_id, loan_application)
    ecl_data = calculate_ecl(borrower_data)
    risk_level, recommendation = get_risk_level_and_recommendation(ecl_data["ecl_percentage"])

    # Store loan decision
    loan_data[borrower_id] = {
        "ecl": ecl_data["ecl"],
        "ecl_percentage": ecl_data["ecl_percentage"],
        "risk_level": risk_level,
        "recommendation": recommendation,
        "timestamp": datetime.datetime.now().isoformat()
    }

    return jsonify({
        "borrower_id": borrower_id,
        "ecl": ecl_data["ecl"],
        "ecl_percentage": ecl_data["ecl_percentage"],
        "risk_level": risk_level,
        "recommendation": recommendation
    })


@app.route("/api/loan/monitor/<borrower_id>", methods=["GET"])
def monitor_loan_endpoint(borrower_id):
    result = monitor_loan(borrower_id)
    return jsonify(result)


@app.route("/api/loan/status/<borrower_id>", methods=["GET"])
def get_loan_status(borrower_id):
    loan = loan_data.get(borrower_id)
    if not loan:
        return jsonify({"error": "Loan not found"}), 404
    return jsonify(loan)


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8000)