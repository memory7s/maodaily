"""
AliveDaily — 桌面每日计划管理工具

使用方法:
  flet run main.py          # 开发模式 (热重载)
  python main.py            # 直接运行
  flet build windows        # 打包成 exe
"""

import flet as ft
from ui.theme import build_theme
from ui.app import DeskApp
from reminder_service import start_reminder_service


def main(page: ft.Page):
    # ── 窗口设置 ──
    page.title = "AliveDaily"
    page.window.width = 820
    page.window.height = 640
    page.window.min_width = 680
    page.window.min_height = 480
    page.padding = 0
    page.spacing = 0
    page.bgcolor = "#F5F5F5"
    page.theme = build_theme()

    # ── 启动后台提醒服务（传入 page 用于弹出 AlertDialog）──
    start_reminder_service(page)

    # ── 挂载主应用 ──
    app = DeskApp(page)
    page.add(app)


if __name__ == "__main__":
    ft.run(main=main)
