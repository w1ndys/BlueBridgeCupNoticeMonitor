import logging
import os
from typing import Sequence

from .base import BaseNotifier
from .dingtalk import DingTalkNotifier
from .feishu import FeishuNotifier

logger = logging.getLogger(__name__)


def create_notifiers(
    enable_dingtalk: bool = True,
    enable_feishu: bool = False,
) -> list[BaseNotifier]:
    notifiers: list[BaseNotifier] = []

    if enable_dingtalk:
        token = os.environ.get("DINGTALK_TOKEN")
        secret = os.environ.get("DINGTALK_SECRET")
        if token and secret:
            notifiers.append(DingTalkNotifier(token, secret))
        else:
            logger.warning("钉钉已启用但未配置 DINGTALK_TOKEN / DINGTALK_SECRET")

    if enable_feishu:
        webhook = os.environ.get("FEISHU_BOT_URL")
        secret = os.environ.get("FEISHU_BOT_SECRET")
        if webhook and secret:
            notifiers.append(FeishuNotifier(webhook, secret))
        else:
            logger.warning("飞书已启用但未配置 FEISHU_BOT_URL / FEISHU_BOT_SECRET")

    return notifiers
