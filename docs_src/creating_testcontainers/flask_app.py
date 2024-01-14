import os

from flask import Flask, Response, jsonify

app = Flask(__name__)


@app.route("/hello")
def hello_api() -> Response:
    greet = os.getenv("GREET", "stranger")
    return jsonify({"message": f"Hello from Flask, {greet}!"})


@app.route("/health")
def healthcheck_api() -> Response:
    return jsonify({"status": "ok"})
