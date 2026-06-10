# 蓝桥杯通知监控系统

[![GitHub Stars](https://img.shields.io/github/stars/w1ndys/BlueBridgeCupNoticeMonitor?style=for-the-badge)](https://github.com/w1ndys/BlueBridgeCupNoticeMonitor/stargazers)
[![Python Version](https://img.shields.io/badge/Python-3.10+-blue?style=for-the-badge&logo=python)](https://www.python.org/)
[![License](https://img.shields.io/github/license/w1ndys/BlueBridgeCupNoticeMonitor?style=for-the-badge)](LICENSE)

> 实时监控蓝桥杯大赛官方通知，通过钉钉 / 飞书机器人自动推送

---

## 核心功能

- **智能监控** - 定时扫描蓝桥杯官网最新通知，按 `nnid` 增量检测
- **多渠道推送** - 同时支持钉钉机器人 Markdown 消息和飞书机器人交互式卡片
- **状态记忆** - 本地 `lanqiao_data.json` 持久化，避免重复提醒
- **工程化架构** - 基于策略模式、仓储模式拆分为独立模块，可测试可扩展
- **免服务器部署** - 内置 GitHub Actions 工作流，无需自备服务器

---

## 项目结构

```
├── main.py                  # 入口
├── pyproject.toml           # 项目元数据与依赖
├── requirements.txt         # 依赖清单
├── src/
│   ├── fetcher.py           # 数据获取（蓝桥杯 API）
│   ├── monitor.py           # 核心编排（取数据 → 比较 → 通知 → 保存）
│   ├── models/
│   │   └── notification.py  # 通知数据模型
│   ├── notifier/
│   │   ├── base.py          # 通知器抽象基类 + HMAC 签名工具
│   │   ├── dingtalk.py      # 钉钉通知器
│   │   ├── feishu.py        # 飞书通知器
│   │   └── factory.py       # 通知器工厂
│   └── repository/
│       └── repository.py    # 数据持久化（文件 / GitHub Secrets）
├── lanqiao_data.json        # 历史数据缓存
└── .github/workflows/       # CI/CD
```

---

## 快速开始

### 环境准备

```bash
# 克隆仓库
git clone https://github.com/w1ndys/BlueBridgeCupNoticeMonitor.git
cd BlueBridgeCupNoticeMonitor
```

### 安装 uv

```bash
# macOS / Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# 或通过 pip
pip install uv
```

### 创建虚拟环境并安装依赖

```bash
uv sync
```

### 配置环境变量

本项目通过环境变量读取配置，运行前设置以下变量：

| 变量名 | 是否必需 | 说明 |
|--------|----------|------|
| `DINGTALK_TOKEN` | 启用钉钉时 | 钉钉机器人 Webhook 的 `access_token` |
| `DINGTALK_SECRET` | 启用钉钉时 | 钉钉机器人的加签密钥 |
| `FEISHU_BOT_URL` | 启用飞书时 | 飞书自定义机器人 Webhook 完整地址 |
| `FEISHU_BOT_SECRET` | 启用飞书时 | 飞书机器人的签名密钥 |

> 系统会自动检测：只要某渠道的 webhook 地址和签名密钥均存在，即视为已启用该渠道，无需额外开关。

### 运行

```bash
# 示例：Linux / macOS
export DINGTALK_TOKEN="your_token"
export DINGTALK_SECRET="your_secret"

uv run python main.py
```

---

## 部署方式一：GitHub Actions（推荐，免服务器）

仓库已内置工作流 `.github/workflows/monitor.yml`，默认每 10 分钟运行一次。

### 配置步骤

1. Fork 本仓库到你的 GitHub 账号

2. 在仓库 **Settings → Secrets and variables → Actions** 中添加 Secrets：

   | Name | Value |
   |------|-------|
   | `DINGTALK_TOKEN` | 钉钉机器人 `access_token` |
   | `DINGTALK_SECRET` | 钉钉机器人加签密钥 |

3. 在 **Settings → Actions → General** 中，将 **Workflow permissions** 设置为 **Read and write permissions**，以便工作流可以提交并推送 `lanqiao_data.json`

4. 手动触发一次测试：进入 **Actions → 蓝桥杯通知监控 → Run workflow**

5. 完成，GitHub 会自动每 10 分钟检查一次，有新通知即推送

### 自定义运行频率

编辑 `.github/workflows/monitor.yml` 中的 `cron` 表达式：

```yaml
on:
  schedule:
    - cron: '*/30 * * * *'  # 每 30 分钟一次
```

---

## 部署方式二：自建服务器（Crontab）

```bash
# 编辑 crontab
crontab -e

# 每 30 分钟检查一次
*/30 * * * * DINGTALK_TOKEN="your_token" DINGTALK_SECRET="your_secret" /path/to/project/.venv/bin/python /path/to/project/main.py >> /var/log/lanqiao_monitor.log 2>&1
```

---

## 钉钉机器人配置指南

1. 打开钉钉 → 目标群 → **群设置 → 机器人 → 添加机器人 → 自定义**
2. **安全设置**选择**加签**，复制密钥即为 `DINGTALK_SECRET`
3. 创建完成后，复制 Webhook 地址中 `access_token=` 之后的部分作为 `DINGTALK_TOKEN`
4. 参考 [钉钉开放平台文档](https://developers.dingtalk.com/document/robots/custom-robot-access) 了解更多

---

## 飞书机器人配置指南

1. 在飞书群中添加**自定义机器人**，选择签名校验
2. 将 Webhook 完整地址填入 `FEISHU_BOT_URL`
3. 将签名密钥填入 `FEISHU_BOT_SECRET`
4. 参考 [飞书开放平台文档](https://open.feishu.cn/document/ukTMukTMukTM/ucTM5YjL3ETO24yNxkjN) 了解更多

---

## 测试通知通道

修改 `main.py` 临时测试：

```python
from src.notifier.factory import create_notifiers

notifiers = create_notifiers()
for n in notifiers:
    n.send_test()
```

---

## 扩展通知渠道

新增通知渠道只需实现 `BaseNotifier` 抽象类并在工厂中注册：

```python
from src.notifier.base import BaseNotifier
from src.models.notification import Notification

class WebhookNotifier(BaseNotifier):
    def send(self, notification: Notification) -> bool:
        ...

    def send_test(self) -> bool:
        ...
```

---

## 注意事项

1. 运行环境需能访问蓝桥杯官网 API (`www.guoxinlanqiao.com`)
2. 钉钉 / 飞书机器人必须开启加签模式，否则无法推送
3. 首次运行时没有历史数据，会将当前所有通知视为新通知并推送；可通过删除 `lanqiao_data.json` 重置
4. GitHub Actions 部署时需确保工作流有写权限，否则无法保存去重记录

---

## 开源协议

本项目采用 [GPL-3.0](LICENSE) 协议开源。
