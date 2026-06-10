import requests
import json
import time
import hmac
import hashlib
import base64
import urllib.parse
import os
import logging
from datetime import datetime


class LanQiaoMonitor:
    def __init__(
        self,
        url,
        data_file="lanqiao_data.json",
        enable_dingtalk=True,
        enable_feishu=True,
        use_github_secrets=False,
    ):
        """
        初始化监控器
        :param url: 要监控的API URL
        :param data_file: 存储历史数据的文件
        :param enable_dingtalk: 是否启用钉钉通知
        :param enable_feishu: 是否启用飞书通知
        :param use_github_secrets: 是否使用GitHub Secrets进行数据持久化
        """
        self.url = url
        self.enable_dingtalk = enable_dingtalk
        self.enable_feishu = enable_feishu
        self.use_github_secrets = use_github_secrets

        script_dir = os.path.dirname(os.path.abspath(__file__))
        self.data_file = os.path.join(script_dir, data_file)

        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }

    def print_welcome(self):
        print("--------------------------------")
        print("蓝桥杯通知监控系统")
        print("By W1ndys")
        print("开源地址：https://github.com/W1ndys/BlueBridgeCupNoticeMonitor")
        print("--------------------------------")

    def fetch_data(self):
        """获取API的JSON数据"""
        try:
            response = requests.get(self.url, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"获取数据失败: {e}")
            return None

    def load_saved_data(self):
        """加载保存的历史数据"""
        if self.use_github_secrets:
            return self._load_from_secrets()
        return self._load_from_file()

    def _load_from_file(self):
        """从文件加载历史数据"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                print(f"加载历史数据失败: {e}")
                return None
        return None

    def _load_from_secrets(self):
        """从GitHub Secrets加载历史数据"""
        encoded_data = os.environ.get("LANQIAO_DATA")
        if encoded_data:
            try:
                decoded_data = base64.b64decode(encoded_data).decode("utf-8")
                return json.loads(decoded_data)
            except Exception as e:
                print(f"从Secrets加载数据失败: {e}")
                return None
        print("Secrets中没有存储历史数据")
        return None

    def save_data(self, data):
        """保存数据"""
        if self.use_github_secrets:
            self._save_to_secrets(data)
        self._save_to_file(data)

    def _save_to_file(self, data):
        """保存数据到文件"""
        try:
            with open(self.data_file, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"数据已保存到 {self.data_file}")
        except Exception as e:
            print(f"保存数据失败: {e}")

    def _save_to_secrets(self, data):
        """保存数据到环境变量（供GitHub Action后续步骤使用）"""
        try:
            json_str = json.dumps(data, ensure_ascii=False)
            encoded_data = base64.b64encode(json_str.encode("utf-8")).decode("utf-8")
            print(f"::set-output name=lanqiao_data::{encoded_data}")
            with open(os.environ.get("GITHUB_OUTPUT", "/dev/null"), "a") as f:
                f.write(f"lanqiao_data={encoded_data}\n")
            print("数据已准备好保存到GitHub Secrets")
        except Exception as e:
            print(f"准备保存数据到Secrets失败: {e}")

    def find_new_content(self, old_data, new_data):
        """
        比较新旧数据，找出新内容
        :return: 新通知列表
        """
        if not old_data:
            # 如果没有旧数据，那么所有内容都是新的
            return new_data.get("datalist", [])

        old_nnids = {item["nnid"] for item in old_data.get("datalist", [])}
        new_items = [
            item
            for item in new_data.get("datalist", [])
            if item["nnid"] not in old_nnids
        ]

        return new_items

    def send_dingtalk_notification(self, new_items):
        """
        发送钉钉通知
        :param new_items: 新通知列表
        """
        if not self.enable_dingtalk:
            print("钉钉通知未启用或未配置")
            return

        if not new_items:
            print("没有新通知")
            return

        dingtalk_token = os.environ.get("DINGTALK_TOKEN")
        dingtalk_secret = os.environ.get("DINGTALK_SECRET")

        if not dingtalk_token or not dingtalk_secret:
            print("钉钉配置未设置，请设置环境变量 DINGTALK_TOKEN 和 DINGTALK_SECRET")
            return

        timestamp = str(round(time.time() * 1000))
        string_to_sign = f"{timestamp}\n{dingtalk_secret}"
        hmac_code = hmac.new(
            dingtalk_secret.encode(),
            string_to_sign.encode(),
            digestmod=hashlib.sha256,
        ).digest()

        sign = urllib.parse.quote_plus(base64.b64encode(hmac_code).decode())

        url = f"https://oapi.dingtalk.com/robot/send?access_token={dingtalk_token}&timestamp={timestamp}&sign={sign}"

        for item in new_items:
            title = item["title"]
            publish_time = item["publishTime"].split("T")[0]
            synopsis = item.get("synopsis", "无摘要")

            message = {
                "msgtype": "markdown",
                "markdown": {
                    "title": "蓝桥杯通知更新",
                    "text": f"## 蓝桥杯大赛通知更新\n\n"
                    f"### {title}\n\n"
                    f"**发布时间**: {publish_time}\n\n"
                    f"**内容摘要**: {synopsis}\n\n"
                    f"[查看详情](https://dasai.lanqiao.cn/notices/{item['nnid']}/)",
                },
            }

            try:
                response = requests.post(
                    url,
                    headers={"Content-Type": "application/json"},
                    data=json.dumps(message),
                )
                result = response.json()
                if result.get("errcode") == 0:
                    print(f"钉钉通知 '{title}' 发送成功")
                else:
                    print(f"钉钉通知发送失败: {result}")
            except Exception as e:
                print(f"发送钉钉通知时出错: {e}")

    def send_feishu_notification(self, new_items):
        """
        发送飞书通知
        :param new_items: 新通知列表
        """
        if not self.enable_feishu:
            print("飞书通知未启用")
            return

        if not new_items:
            print("没有新通知")
            return

        # 检查环境变量
        feishu_webhook = os.environ.get("FEISHU_BOT_URL")
        feishu_secret = os.environ.get("FEISHU_BOT_SECRET")

        if not feishu_webhook or not feishu_secret:
            print("飞书配置未设置，请设置环境变量 FEISHU_BOT_URL 和 FEISHU_BOT_SECRET")
            return

        for item in new_items:
            title = item["title"]
            publish_time = item["publishTime"].split("T")[0]
            synopsis = item.get("synopsis", "无摘要")

            # 使用富文本卡片发送通知
            result = self.feishu_rich_text(
                "蓝桥杯通知更新",
                title,
                publish_time,
                synopsis,
                f"https://dasai.lanqiao.cn/notices/{item['nnid']}/",
            )

            if "error" not in result:
                print(f"飞书通知 '{title}' 发送成功")
            else:
                print(f"飞书通知发送失败: {result}")

    def feishu_rich_text(
        self, card_title, notice_title, publish_time, synopsis, detail_url
    ):
        """
        发送飞书富文本机器人消息

        Args:
            card_title: 卡片标题
            notice_title: 通知标题
            publish_time: 发布时间
            synopsis: 内容摘要
            detail_url: 详情链接

        Returns:
            dict: 接口返回结果
        """
        # 环境变量
        FEISHU_BOT_URL = os.environ.get("FEISHU_BOT_URL")
        FEISHU_BOT_SECRET = os.environ.get("FEISHU_BOT_SECRET")

        feishu_webhook = FEISHU_BOT_URL
        feishu_secret = FEISHU_BOT_SECRET
        timestamp = str(int(time.time()))

        # 计算签名
        string_to_sign = f"{timestamp}\n{feishu_secret}"
        hmac_code = hmac.new(
            string_to_sign.encode("utf-8"), digestmod=hashlib.sha256
        ).digest()
        sign = base64.b64encode(hmac_code).decode("utf-8")

        # 构建请求头
        headers = {"Content-Type": "application/json"}

        # 构建富文本卡片消息
        msg = {
            "timestamp": timestamp,
            "sign": sign,
            "msg_type": "interactive",
            "card": {
                "config": {"wide_screen_mode": True},
                "header": {
                    "title": {"tag": "plain_text", "content": card_title},
                    "template": "blue",
                },
                "elements": [
                    {
                        "tag": "div",
                        "text": {"tag": "lark_md", "content": f"### {notice_title}"},
                    },
                    {
                        "tag": "div",
                        "fields": [
                            {
                                "is_short": True,
                                "text": {
                                    "tag": "lark_md",
                                    "content": f"**发布时间**\n{publish_time}",
                                },
                            }
                        ],
                    },
                    {
                        "tag": "div",
                        "text": {
                            "tag": "lark_md",
                            "content": f"**内容摘要**\n{synopsis}",
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
                                "url": detail_url,
                            }
                        ],
                    },
                ],
            },
        }

        # 发送请求
        try:
            if not isinstance(feishu_webhook, str):
                logging.error(f"飞书webhook未配置")
                return {"error": "飞书webhook未配置"}
            response = requests.post(
                feishu_webhook, headers=headers, data=json.dumps(msg)
            )
            logging.info(f"飞书发送富文本通知消息成功🎉\n{response.json()}")
            return response.json()
        except Exception as e:
            logging.error(f"飞书发送富文本通知消息失败😞\n{e}")
            return {"error": str(e)}

    def test_dingtalk_notification(self):
        """
        测试钉钉通知功能
        """
        if not self.enable_dingtalk:
            print("钉钉通知未启用或未配置")
            return False

        print("开始测试钉钉通知...")

        timestamp = str(round(time.time() * 1000))
        dingtalk_secret = os.environ.get("DINGTALK_SECRET")
        dingtalk_token = os.environ.get("DINGTALK_TOKEN")
        if not dingtalk_secret or not dingtalk_token:
            print("钉钉配置未设置，请设置环境变量 DINGTALK_SECRET 和 DINGTALK_TOKEN")
            return False
        string_to_sign = f"{timestamp}\n{dingtalk_secret}"
        hmac_code = hmac.new(
            dingtalk_secret.encode(),
            string_to_sign.encode(),
            digestmod=hashlib.sha256,
        ).digest()

        sign = urllib.parse.quote_plus(base64.b64encode(hmac_code).decode())

        url = f"https://oapi.dingtalk.com/robot/send?access_token={dingtalk_token}&timestamp={timestamp}&sign={sign}"

        message = {
            "msgtype": "markdown",
            "markdown": {
                "title": "蓝桥杯监控测试",
                "text": f"## 蓝桥杯监控系统测试\n\n"
                f"**测试时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
                f"**测试内容**: 这是一条测试消息，用于验证钉钉通知功能是否正常工作。\n\n"
                f"[查看监控页面]({self.url})",
            },
        }

        try:
            response = requests.post(
                url,
                headers={"Content-Type": "application/json"},
                data=json.dumps(message),
            )
            result = response.json()
            if result.get("errcode") == 0:
                print("钉钉测试通知发送成功")
            else:
                print(f"钉钉测试通知发送失败: {result}")
            return result.get("errcode") == 0
        except Exception as e:
            print(f"发送钉钉测试通知时出错: {e}")
            return False

    def test_feishu_notification(self):
        """
        测试飞书通知功能
        """
        if not self.enable_feishu:
            print("飞书通知未启用")
            return False

        print("开始测试飞书通知...")

        # 检查环境变量
        feishu_webhook = os.environ.get("FEISHU_BOT_URL")
        feishu_secret = os.environ.get("FEISHU_BOT_SECRET")

        if not feishu_webhook or not feishu_secret:
            print("飞书配置未设置，请设置环境变量 FEISHU_BOT_URL 和 FEISHU_BOT_SECRET")
            return False

        test_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # 使用富文本卡片发送测试通知
        result = self.feishu_rich_text(
            "蓝桥杯监控测试",
            "蓝桥杯监控系统测试",
            test_time,
            "这是一条测试消息，用于验证飞书通知功能是否正常工作。",
            self.url,
        )

        if "error" not in result:
            print("飞书测试通知发送成功")
            return True
        else:
            print(f"飞书测试通知发送失败: {result}")
            return False

    def run(self):
        """运行监控器"""
        print(f"蓝桥杯通知监控启动: {datetime.now()}")

        # 获取最新数据
        new_data = self.fetch_data()
        if not new_data:
            print("无法获取新数据，退出")
            return

        # 加载保存的历史数据
        old_data = self.load_saved_data()

        # 找出新内容
        new_items = self.find_new_content(old_data, new_data)

        # 如果有新内容，发送通知
        if new_items:
            print(f"发现 {len(new_items)} 条新通知")
            # 发送钉钉通知
            if self.enable_dingtalk:
                self.send_dingtalk_notification(new_items)
            # 发送飞书通知
            if self.enable_feishu:
                self.send_feishu_notification(new_items)
        else:
            print("没有发现新通知")

        # 保存最新数据
        self.save_data(new_data)

        print(f"蓝桥杯通知监控完成: {datetime.now()}")


if __name__ == "__main__":
    url = "https://www.guoxinlanqiao.com/api/news/find?status=1&project=dasai&progid=20&pageno=1&pagesize=10"

    enable_dingtalk = os.environ.get("ENABLE_DINGTALK", "true").lower() == "true"
    enable_feishu = os.environ.get("ENABLE_FEISHU", "false").lower() == "true"

    monitor = LanQiaoMonitor(
        url,
        enable_dingtalk=enable_dingtalk,
        enable_feishu=enable_feishu,
        use_github_secrets=False,
    )

    monitor.print_welcome()
    monitor.run()
