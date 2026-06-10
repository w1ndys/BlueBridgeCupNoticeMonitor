import base64
import json
import logging
import os
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class DataRepository(ABC):
    @abstractmethod
    def load(self) -> dict | None: ...

    @abstractmethod
    def save(self, data: dict) -> None: ...


class FileRepository(DataRepository):
    def __init__(self, file_path: str):
        self.file_path = file_path

    def load(self) -> dict | None:
        if not os.path.exists(self.file_path):
            return None
        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.error("加载历史数据失败: %s", e)
            return None

    def save(self, data: dict) -> None:
        try:
            with open(self.file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            logger.info("数据已保存到 %s", self.file_path)
        except Exception as e:
            logger.error("保存数据失败: %s", e)


class GitHubSecretsRepository(DataRepository):
    def load(self) -> dict | None:
        encoded_data = os.environ.get("LANQIAO_DATA")
        if not encoded_data:
            logger.warning("Secrets 中没有存储历史数据")
            return None
        try:
            decoded_data = base64.b64decode(encoded_data).decode("utf-8")
            return json.loads(decoded_data)
        except Exception as e:
            logger.error("从 Secrets 加载数据失败: %s", e)
            return None

    def save(self, data: dict) -> None:
        try:
            json_str = json.dumps(data, ensure_ascii=False)
            encoded_data = base64.b64encode(json_str.encode("utf-8")).decode("utf-8")
            github_output = os.environ.get("GITHUB_OUTPUT", "/dev/null")
            with open(github_output, "a") as f:
                f.write(f"lanqiao_data={encoded_data}\n")
            logger.info("数据已准备好保存到 GitHub Secrets")
        except Exception as e:
            logger.error("准备保存数据到 Secrets 失败: %s", e)
