import json
import logging
import urllib.parse
from datetime import datetime

import requests

from ..models.notification import Notification
from .base import BaseNotifier, generate_hmac_sign, generate_timestamp

logger = logging.getLogger(__name__)


class DingTalkNotifier(BaseNotifier):
    def __init__(self, token: str, secret: str):
        self.token = token
        self.secret = secret

    def _build_url(self) -> str:
        timestamp = generate_timestamp()
        sign = urllib.parse.quote_plus(generate_hmac_sign(self.secret, timestamp))
        return (
            f"https://oapi.dingtalk.com/robot/send"
            f"?access_token={self.token}&timestamp={timestamp}&sign={sign}"
        )

    def send(self, notification: Notification) -> bool:
        message = {
            "msgtype": "markdown",
            "markdown": {
                "title": "蓝桥杯通知更新",
                "text": (
                    f"## 蓝桥杯大赛通知更新\n\n"
                    f"### {notification.title}\n\n"
                    f"**发布时间**: {notification.publish_date}\n\n"
                    f"**内容摘要**: {notification.synopsis}\n\n"
                    f"[查看详情]({notification.detail_url})"
                ),
            },
        }

        try:
            response = requests.post(
                self._build_url(),
                headers={"Content-Type": "application/json"},
                data=json.dumps(message),
            )
            result = response.json()
            if result.get("errcode") == 0:
                logger.info("钉钉通知 '%s' 发送成功", notification.title)
                return True
            logger.error("钉钉通知发送失败: %s", result)
            return False
        except Exception as e:
            logger.error("发送钉钉通知时出错: %s", e)
            return False

    def send_test(self) -> bool:
        test_notification = Notification(
            nnid="test",
            title="蓝桥杯监控系统测试",
            publish_time=datetime.now().isoformat(),
            synopsis="这是一条测试消息，用于验证钉钉通知功能是否正常工作。",
        )
        return self.send(test_notification)
