from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Notification:
    nnid: str
    title: str
    publish_time: str
    synopsis: str = "无摘要"

    @property
    def publish_date(self) -> str:
        return self.publish_time.split("T")[0]

    @property
    def detail_url(self) -> str:
        return f"https://dasai.lanqiao.cn/notices/{self.nnid}/"

    @classmethod
    def from_api_item(cls, item: dict) -> "Notification":
        return cls(
            nnid=str(item["nnid"]),
            title=item["title"],
            publish_time=item["publishTime"],
            synopsis=item.get("synopsis", "无摘要"),
        )
