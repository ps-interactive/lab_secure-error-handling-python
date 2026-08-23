import logging
import copy

class PIIFilter(logging.Filter):
    SENSITIVE_KEYS = {"password", "api_key", "secret", "ssn", "credit_card"}

    def filter(self, record):
        # 1. Scrub dictionary payloads
        if isinstance(record.msg, dict):
            record.msg = self._sanitize_dict(record.msg)
        # 2. Scrub string messages
        elif isinstance(record.msg, str):
            record.msg = self._sanitize_string(record.msg)
            
        # 3. Scrub exception message/tracebacks if present
        if record.exc_text:
            record.exc_text = self._sanitize_string(record.exc_text)

        return True

    def _sanitize_string(self, text):
        # Basic check to redact sensitive strings or keys
        for key in self.SENSITIVE_KEYS:
            if key in text.lower():
                return "[REDACTED SENSITIVE CONTENT]"
        return text

    def _sanitize_dict(self, data):
        cleaned_data = copy.deepcopy(data)
        for key, value in cleaned_data.items():
            if key.lower() in self.SENSITIVE_KEYS:
                cleaned_data[key] = "[REDACTED]"
            elif isinstance(value, dict):
                cleaned_data[key] = self._sanitize_dict(value)
        return cleaned_data
