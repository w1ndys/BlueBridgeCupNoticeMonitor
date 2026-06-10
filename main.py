"""蓝桥杯通知监控系统 - 入口"""

import logging
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.fetcher import Fetcher
from src.monitor import Monitor
from src.notifier.factory import create_notifiers
from src.repository.repository import FileRepository

API_URL = (
    "https://www.guoxinlanqiao.com/api/news/find"
    "?status=1&project=dasai&progid=20&pageno=1&pagesize=10"
)
DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "lanqiao_data.json")

BANNER = """\
--------------------------------
蓝桥杯通知监控系统
By W1ndys
开源地址：https://github.com/W1ndys/BlueBridgeCupNoticeMonitor
--------------------------------"""


def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    print(BANNER)

    fetcher = Fetcher(API_URL)
    repository = FileRepository(DATA_FILE)
    notifiers = create_notifiers()

    monitor = Monitor(
        fetcher=fetcher,
        repository=repository,
        notifiers=notifiers,
    )
    monitor.run()


if __name__ == "__main__":
    main()
