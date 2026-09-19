"""
RitaDrishti-AI — PII Sanitization Module
Redacts sensitive personally identifiable information (emails, credit cards, SSN, phone numbers)
prior to review persistence and downstream analysis.
"""

import re

# Regex patterns for common PII
EMAIL_REGEX = re.compile(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', re.IGNORECASE)
CREDIT_CARD_REGEX = re.compile(r'\b(?:\d[ -]*?){13,16}\b')
SSN_REGEX = re.compile(r'\b\d{3}-\d{2}-\d{4}\b')
PHONE_REGEX = re.compile(r'(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}')


def sanitize_text(text: str) -> str:
    """
    Sanitizes review text by masking email addresses, credit cards, SSN, and phone numbers.
    Returns sanitized text.
    """
    if not text:
        return text

    sanitized = text
    sanitized = EMAIL_REGEX.sub("[EMAIL REDACTED]", sanitized)
    sanitized = CREDIT_CARD_REGEX.sub("[CARD REDACTED]", sanitized)
    sanitized = SSN_REGEX.sub("[SSN REDACTED]", sanitized)
    sanitized = PHONE_REGEX.sub("[PHONE REDACTED]", sanitized)

    return sanitized
