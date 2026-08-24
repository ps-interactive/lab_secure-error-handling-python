import copy
import logging
from flask import Flask, jsonify, request

app = Flask(__name__)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("AppLogger")

# 4. Route Implementation
@app.route("/user/update", methods=["POST"])
def update_user():
    data = request.get_json()

    # Log payload safely (Dict payload will be sanitized by PIIFilter)
    logger.info(data)

    if "trigger_error" in data:
        # SECURE: Generic exception message without credentials
        # raise RuntimeError("Database connection failed!")
        raise RuntimeError("Database connection failed! Secret API Key: secret_api_key_12345")

    return jsonify({"status": "success"}), 200


if __name__ == "__main__":
    # SECURE: Disable debug mode to prevent Werkzeug traceback pages
    app.run(debug=True)