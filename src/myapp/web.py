"""HTTP interface for the calculator used by the deployment exercise."""
import math
import os

from flask import Flask, jsonify, render_template, request
from flask_wtf.csrf import CSRFError, CSRFProtect, generate_csrf

from myapp.calculator import Calculator


def calculate_value(payload, operations):
    if not isinstance(payload, dict):
        raise ValueError("Request must be a JSON object")
    operation = payload.get("operation")
    if not isinstance(operation, str) or operation not in operations:
        raise ValueError("Unknown operation")
    a, b = payload.get("a"), payload.get("b")
    if any(isinstance(value, bool) or not isinstance(value, (int, float)) for value in (a, b)):
        raise ValueError("a and b must be finite numbers")
    if not all(math.isfinite(value) for value in (a, b)):
        raise ValueError("a and b must be finite numbers")
    result = operations[operation](a, b)
    if not math.isfinite(result):
        raise ValueError("Result is outside the supported numeric range")
    return result


def create_app(test_config=None):
    app = Flask(__name__)
    app.config.from_mapping(SECRET_KEY=os.environ.get("APP_SECRET_KEY"), MAX_CONTENT_LENGTH=16384)
    if test_config:
        app.config.update(test_config)
    if not app.secret_key:
        raise RuntimeError("APP_SECRET_KEY must be configured")
    CSRFProtect(app)
    calculator = Calculator()
    operations = {
        "add": calculator.add,
        "subtract": calculator.subtract,
        "multiply": calculator.multiply,
        "divide": calculator.divide,
    }

    @app.get("/")
    def index():
        return render_template("index.html")

    @app.get("/health")
    def health():
        return jsonify(status="ok")

    @app.get("/api/csrf")
    def csrf_token():
        return jsonify(csrf_token=generate_csrf())

    @app.errorhandler(CSRFError)
    def csrf_error(error):
        return jsonify(error=error.description), 400

    @app.post("/api/calculate")
    def calculate():
        try:
            result = calculate_value(request.get_json(silent=True), operations)
        except (ValueError, OverflowError) as error:
            return jsonify(error=str(error)), 400
        return jsonify(result=result)

    return app
