import logging
from datetime import datetime

from .fetcher import Fetcher
from .models.notification import Notification
from .notifier.base import BaseNotifier
from .repository.repository import DataRepository

logger = logging.getLogger(__name__)


class Monitor:
    def __init__(
        self,
        fetcher: Fetcher,
        repository: DataRepository,
        notifiers: list[BaseNotifier],
    ):
        self.fetcher = fetcher
        self.repository = repository
        self.notifiers = notifiers

    @staticmethod
    def _find_new_notifications(
        old_data: dict | None, new_data: dict
    ) -> list[Notification]:
        datalist = new_data.get("datalist", [])
        if not old_data:
            return [Notification.from_api_item(item) for item in datalist]

        old_nnids = {str(item["nnid"]) for item in old_data.get("datalist", [])}
        return [
            Notification.from_api_item(item)
            for item in datalist
            if str(item.get("nnid")) not in old_nnids
        ]

    def run(self) -> None:
        logger.info("蓝桥杯通知监控启动: %s", datetime.now())

        new_data = self.fetcher.fetch()
        if not new_data:
            logger.error("无法获取新数据，退出")
            return

        old_data = self.repository.load()
        new_notifications = self._find_new_notifications(old_data, new_data)

        if new_notifications:
            logger.info("发现 %d 条新通知", len(new_notifications))
            for notification in new_notifications:
                for notifier in self.notifiers:
                    notifier.send(notification)
        else:
            logger.info("没有发现新通知")

        self.repository.save(new_data)
        logger.info("蓝桥杯通知监控完成: %s", datetime.now())
