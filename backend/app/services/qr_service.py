"""
Cryptographic QR Code & Verification Token Service
Implements Section 9 of the Ministry of Health, The Gambia specification.
Guarantees zero PII in QR payload.
"""

import base64
import hashlib
import io
import secrets
from datetime import datetime, timedelta, timezone
from typing import Dict, Optional
import qrcode
from qrcode.image.pil import PilImage


class QRService:
    @staticmethod
    def generate_token() -> str:
        """Generates a high-entropy 192-bit cryptographic opaque token."""
        return secrets.token_hex(24)

    @staticmethod
    def hash_token(token: str) -> str:
        """Generates SHA-256 hash of token to store in database."""
        return hashlib.sha256(token.strip().encode("utf-8")).hexdigest()

    @staticmethod
    def generate_qr_image_base64(payload_url: str) -> str:
        """Generates a high-resolution PNG QR Code as a base64 encoded string."""
        qr = qrcode.QRCode(
            version=None,
            error_correction=qrcode.constants.ERROR_CORRECT_M,
            box_size=10,
            border=3,
        )
        qr.add_data(payload_url)
        qr.make(fit=True)

        img = qr.make_image(fill_color="#0f172a", back_color="#ffffff")
        buffered = io.BytesIO()
        img.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
        return f"data:image/png;base64,{img_str}"

    @staticmethod
    def build_verification_payload(token: str, base_url: str = "http://localhost:8000") -> str:
        """
        Creates verification reference string or URL.
        Contains solely the opaque token, zero PII or clinical status.
        """
        return f"{base_url}/verify?token={token}"

