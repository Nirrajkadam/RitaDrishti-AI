"""
RitaDrishti-AI — In-Memory Rate Limiter for Public Endpoints
Prevents brute-force credential stuffing and registration spam.
"""

import time
from typing import Dict, List
from fastapi import Request
from backend.app.config import settings
from backend.app.core.exceptions import RitaDrishtiException


class RateLimiter:
    def __init__(self, requests_limit: int = 10, window_seconds: int = 60):
        self.requests_limit = requests_limit
        self.window_seconds = window_seconds
        self.history: Dict[str, List[float]] = {}

    def __call__(self, request: Request):
        if settings.APP_ENV == "testing":
            return

        client_ip = request.client.host if request.client else "127.0.0.1"
        now = time.time()

        if client_ip not in self.history:
            self.history[client_ip] = []

        # Filter out requests older than window_seconds
        self.history[client_ip] = [t for t in self.history[client_ip] if now - t < self.window_seconds]

        if len(self.history[client_ip]) >= self.requests_limit:
            raise RitaDrishtiException(
                code="RATE_LIMIT_EXCEEDED",
                message=f"Rate limit exceeded. Maximum {self.requests_limit} requests allowed per {self.window_seconds} seconds.",
                status_code=429,
                retryable=True
            )

        self.history[client_ip].append(now)


auth_rate_limiter = RateLimiter(requests_limit=10, window_seconds=60)
