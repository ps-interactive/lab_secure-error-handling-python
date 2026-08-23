import copy
import logging
from flask import Flask, jsonify, request

app = Flask(__name__)


# 1. Define PII Filter First (Prevents NameError)
class PIIFilter(logging.Filter):
    SENSITIVE_KEYS = {"password", "api_key", "secret", "ssn", "credit_card"}

    def filter(self, record):
        # Handle dict payloads
        if isinstance(record.msg, dict):
            record.msg = self._sanitize_dict(record.msg)
        # Handle string messages
        elif isinstance(record.msg, str):
            record.msg = self._sanitize_string(record.msg)

        # Handle formatted exception tracebacks if attached
        if record.exc_text:
            record.exc_text = self._sanitize_string(record.exc_text)

        return True

    def _sanitize_string(self, text):
        for key in self.SENSITIVE_KEYS:
            if key in text.lower():
                return "[REDACTED PII CONTENT]"
        return text

    def _sanitize_dict(self, data):
        cleaned_data = copy.deepcopy(data)
        for key, value in cleaned_data.items():
            if key.lower() in self.SENSITIVE_KEYS:
                cleaned_data[key] = "[REDACTED]"
            elif isinstance(value, dict):
                cleaned_data[key] = self._sanitize_dict(value)
        return cleaned_data


# 2. Attach Filter to Logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("AppLogger")
logger.addFilter(PIIFilter())


# 3. Secure Global Error Handler (Hides Tracebacks from Client)
@app.errorhandler(Exception)
def handle_unexpected_error(error):
    # Log internal error safely
    logger.error(
        f"An unexpected internal error occurred: {error}", exc_info=True
    )

    # Return sanitized generic response to user
    response = {
        "error": "Internal Server Error",
        "message": "An unexpected error occurred. Please try again later.",
    }
    return jsonify(response), 500


# 4. Route Implementation
@app.route("/user/update", methods=["POST"])
def update_user():
    data = request.get_json()

    # Log payload safely (Dict payload will be sanitized by PIIFilter)
    logger.info(data)

    if "trigger_error" in data:
        # SECURE: Generic exception message without credentials
        raise RuntimeError("Database connection failed!")

    return jsonify({"status": "success"}), 200


if __name__ == "__main__":
    # SECURE: Disable debug mode to prevent Werkzeug traceback pages
    app.run(debug=False)