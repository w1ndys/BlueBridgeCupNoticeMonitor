import json
import logging
import time
from datetime import datetime

import requests

from ..models.notification import Notification
from .base import BaseNotifier, generate_hmac_sign

logger = logging.getLogger(__name__)


class FeishuNotifier(BaseNotifier):
    def __init__(self, webhook_url: str, secret: str):
        self.webhook_url = webhook_url
        self.secret = secret

    def _build_card(self, notification: Notification) -> dict:
        return {
            "msg_type": "interactive",
            "card": {
                "config": {"wide_screen_mode": True},
                "header": {
                    "title": {"tag": "plain_text", "content": "蓝桥杯通知更新"},
                    "template": "blue",
                },
                "elements": [
                    {
                        "tag": "div",
                        "text": {
                            "tag": "lark_md",
                            "content": f"### {notification.title}",
                        },
                    },
                    {
                        "tag": "div",
                        "fields": [
                            {
                                "is_short": True,
                                "text": {
                                    "tag": "lark_md",
                                    "content": f"**发布时间**\n{notification.publish_date}",
                                },
                            }
                        ],
                    },
                    {
                        "tag": "div",
                        "text": {
                            "tag": "lark_md",
                            "content": f"**内容摘要**\n{notification.synopsis}",
                        },
                    },
                    {"tag": "hr"},
                    {
                        "tag": "action",
                        "actions": [
                            {
                                "tag": "button",
                                "text": {"tag": "plain_text", "content": "查看详情"},
                                "type": "primary",
                                "url": notification.detail_url,
                            }
                        ],
                    },
                ],
            },
        }

    def _post(self, payload: dict) -> dict:
        timestamp = str(int(time.time()))
        sign = generate_hmac_sign(self.secret, timestamp)
        payload["timestamp"] = timestamp
        payload["sign"] = sign

        try:
            response = requests.post(
                self.webhook_url,
                headers={"Content-Type": "application/json"},
                data=json.dumps(payload),
            )
            result = response.json()
            logger.info("飞书发送通知消息成功: %s", result)
            return result
        except Exception as e:
            logger.error("飞书发送通知消息失败: %s", e)
            return {"error": str(e)}

    def send(self, notification: Notification) -> bool:
        card = self._build_card(notification)
        result = self._post(card)
        if "error" not in result:
            logger.info("飞书通知 '%s' 发送成功", notification.title)
            return True
        logger.error("飞书通知发送失败: %s", result)
        return False

    def send_test(self) -> bool:
        test_notification = Notification(
            nnid="test",
            title="蓝桥杯监控系统测试",
            publish_time=datetime.now().isoformat(),
            synopsis="这是一条测试消息，用于验证飞书通知功能是否正常工作。",
        )
        return self.send(test_notification)
