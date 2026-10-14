"""HTTP interface for the calculator used by the deployment exercise."""
import math

from flask import Flask, jsonify, render_template, request

from myapp.calculator import Calculator


def create_app():
    app = Flask(__name__)
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

    @app.post("/api/calculate")
    def calculate():
        payload = request.get_json(silent=True)
        if not isinstance(payload, dict):
            return jsonify(error="Request must be a JSON object"), 400
        operation = payload.get("operation")
        if not isinstance(operation, str) or operation not in operations:
            return jsonify(error="Unknown operation"), 400
        a, b = payload.get("a"), payload.get("b")
        if any(isinstance(value, bool) or not isinstance(value, (int, float)) for value in (a, b)):
            return jsonify(error="a and b must be finite numbers"), 400
        try:
            if not all(math.isfinite(value) for value in (a, b)):
                raise ValueError("a and b must be finite numbers")
            result = operations[operation](a, b)
            if not math.isfinite(result):
                raise ValueError("Result is outside the supported numeric range")
        except (ValueError, OverflowError) as error:
            return jsonify(error=str(error)), 400
        return jsonify(result=result)

    return app
