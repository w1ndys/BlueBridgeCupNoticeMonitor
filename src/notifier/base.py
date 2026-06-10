import base64
import hashlib
import hmac
import time
from abc import ABC, abstractmethod

from ..models.notification import Notification


def generate_hmac_sign(secret: str, timestamp: str) -> str:
    """生成 HMAC-SHA256 签名"""
    string_to_sign = f"{timestamp}\n{secret}"
    hmac_code = hmac.new(
        secret.encode(), string_to_sign.encode(), digestmod=hashlib.sha256
    ).digest()
    return base64.b64encode(hmac_code).decode()


def generate_timestamp() -> str:
    return str(round(time.time() * 1000))


class BaseNotifier(ABC):
    @abstractmethod
    def send(self, notification: Notification) -> bool: ...

    @abstractmethod
    def send_test(self) -> bool: ...
