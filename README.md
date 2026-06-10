# 蓝桥杯通知监控系统

[![GitHub Stars](https://img.shields.io/github/stars/w1ndys/BlueBridgeCupNoticeMonitor?style=for-the-badge)](https://github.com/w1ndys/BlueBridgeCupNoticeMonitor/stargazers)
[![Python Version](https://img.shields.io/badge/Python-3.10+-blue?style=for-the-badge&logo=python)](https://www.python.org/)

> 实时监控蓝桥杯大赛官方通知，通过钉钉 / 飞书机器人自动推送

## 核心功能

- **智能监控** - 定时扫描蓝桥杯官网最新通知，按 `nnid` 增量检测
- **多渠道推送** - 同时支持钉钉机器人 Markdown 消息和飞书机器人交互式卡片
- **状态记忆** - 本地 `lanqiao_data.json` 持久化，避免重复提醒
- **工程化架构** - 基于策略模式、仓储模式拆分为独立模块，可测试可扩展

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
# 创建虚拟环境并同步依赖
uv sync
```

### 配置通知渠道

通过环境变量配置，至少启用一个通知渠道：

| 环境变量 | 说明 | 必填 |
|----------|------|------|
| `ENABLE_DINGTALK` | 启用钉钉通知（默认 `true`） | 否 |
| `ENABLE_FEISHU` | 启用飞书通知（默认 `false`） | 否 |
| `DINGTALK_TOKEN` | 钉钉机器人 Webhook Token | 启用钉钉时必填 |
| `DINGTALK_SECRET` | 钉钉机器人加签密钥 | 启用钉钉时必填 |
| `FEISHU_BOT_URL` | 飞书机器人 Webhook 地址 | 启用飞书时必填 |
| `FEISHU_BOT_SECRET` | 飞书机器人签名密钥 | 启用飞书时必填 |

### 运行

```bash
# 通过 uv 运行
uv run python main.py
```

## 部署

### 方式一：Linux crontab

```bash
# 编辑 crontab
crontab -e

# 每 30 分钟检查一次（使用 uv 虚拟环境中的 Python）
*/30 * * * * cd /path/to/project && .venv/bin/python main.py >> /var/log/lanqiao_monitor.log 2>&1
```

### 方式二：GitHub Actions（推荐）

项目已内置 `.github/workflows/monitor.yml`，每 10 分钟自动执行。部署步骤：

1. Fork 本仓库
2. 在仓库 Settings → Secrets and variables → Actions 中添加 Secrets：
   - `DINGTALK_TOKEN`
   - `DINGTALK_SECRET`
3. Actions 的 schedule 默认 10 分钟运行一次，无需额外配置

## 扩展通知渠道

新增通知渠道只需实现 `BaseNotifier` 抽象类并在工厂中注册：

```python
from src.notifier.base import BaseNotifier

class WebhookNotifier(BaseNotifier):
    def send(self, notification: Notification) -> bool:
        # 实现通知发送逻辑
        ...

    def send_test(self) -> bool:
        # 实现测试发送逻辑
        ...
```

## 注意事项

1. 确保服务器可以访问蓝桥杯官网 `guoxinlanqiao.com`
2. 钉钉机器人需开启加签验证功能
3. 首次运行会将所有历史通知标记为已读（通过清空 `lanqiao_data.json` 重置）

## 开源协议

本项目采用 [GPL-3.0](LICENSE)
