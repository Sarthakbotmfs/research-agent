import logging
import re
import sys

# Regex patterns to sanitize sensitive credentials from log outputs
SENSITIVE_PATTERNS = [
    re.compile(
        r"(?i)(api[_-]?key|bearer|token|secret|password)[\s:=]+['\"]?([a-zA-Z0-9_\-\.]{8,})['\"]?"
    ),
    re.compile(r"(sk-[a-zA-Z0-9_\-]{20,})"),
    re.compile(r"(nvapi-[a-zA-Z0-9_\-]{20,})"),
]


def sanitize_log_message(message: str) -> str:
    sanitized = message
    for pattern in SENSITIVE_PATTERNS:
        sanitized = pattern.sub(r"\1 [REDACTED]", sanitized)
    return sanitized


class SanitizingFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        original = super().format(record)
        return sanitize_log_message(original)


def setup_logging(log_level: str = "INFO") -> None:
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))

    # Remove existing handlers to avoid duplicates
    for handler in list(root_logger.handlers):
        root_logger.removeHandler(handler)

    handler = logging.StreamHandler(sys.stdout)
    formatter = SanitizingFormatter(
        fmt="%(asctime)s [%(levelname)s] %(name)s: %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
    )
    handler.setFormatter(formatter)
    root_logger.addHandler(handler)


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
