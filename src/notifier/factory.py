import logging
import os

from .base import BaseNotifier
from .dingtalk import DingTalkNotifier
from .feishu import FeishuNotifier

logger = logging.getLogger(__name__)


def create_notifiers() -> list[BaseNotifier]:
    notifiers: list[BaseNotifier] = []

    token = os.environ.get("DINGTALK_TOKEN")
    secret = os.environ.get("DINGTALK_SECRET")
    if token and secret:
        notifiers.append(DingTalkNotifier(token, secret))
        logger.info("钉钉通知渠道已启用")
    else:
        logger.info("钉钉通知渠道未配置，已跳过")

    webhook = os.environ.get("FEISHU_BOT_URL")
    secret = os.environ.get("FEISHU_BOT_SECRET")
    if webhook and secret:
        notifiers.append(FeishuNotifier(webhook, secret))
        logger.info("飞书通知渠道已启用")
    else:
        logger.info("飞书通知渠道未配置，已跳过")

    return notifiers
