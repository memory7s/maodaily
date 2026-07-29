"""
侧边导航栏 —— NavigationRail 风格
"""

import flet as ft
from .theme import PRIMARY, TEXT_SECONDARY, CARD_BG


class Sidebar(ft.Container):
    """左侧导航栏组件"""

    NAV_ITEMS = [
        ("📋", "全部", "all"),
        ("💼", "工作", "tag:工作"),
        ("📚", "学习", "tag:学习"),
        ("🏠", "生活", "tag:生活"),
        ("⏸", "暂时不做", "tag:"),
        ("🚫", "就是不做", "tag:就是不做"),
        ("📅", "日历", "calendar"),
    ]

    def __init__(self, on_navigate=None):
        self.on_navigate = on_navigate
        self._active = "all"
        self._nav_controls = []
        self._theme = None  # 由外部 update_theme 设置

        super().__init__(
            width=180,
            bgcolor=CARD_BG,
            padding=ft.Padding.only(top=16, left=8, right=8),
            content=self._build(),
        )

    def _build(self):
        col = ft.Column(spacing=4, controls=[])
        # 标题
        col.controls.append(
            ft.Container(
                content=ft.Text(
                    "AliveDaily",
                    size=18,
                    weight=ft.FontWeight.BOLD,
                    color=PRIMARY,
                ),
                padding=ft.Padding.only(left=12, bottom=16),
            )
        )

        for icon, label, key in self.NAV_ITEMS:
            btn = self._nav_item(icon, label, key)
            col.controls.append(btn)
            self._nav_controls.append(btn)

        return col

    def _nav_item(self, icon, label, key):
        is_active = key == self._active
        return ft.Container(
            data=key,
            content=ft.Row(
                controls=[
                    ft.Text(icon, size=16),
                    ft.Text(label, size=14, weight=ft.FontWeight.W_500),
                ],
            ),
            padding=ft.Padding.symmetric(horizontal=12, vertical=10),
            border_radius=ft.BorderRadius.all(8),
            bgcolor="#FFF7ED" if is_active else "transparent",
            ink=True,
            on_click=lambda e, k=key: self._on_click(k),
        )

    def _on_click(self, key):
        self._active = key
        # 刷新全部导航项的外观
        theme = self._theme or {}
        primary = theme.get("PRIMARY", PRIMARY)
        primary_light = theme.get("PRIMARY_LIGHT", "#FFF7ED")
        text_secondary = theme.get("TEXT_SECONDARY", TEXT_SECONDARY)

        for ctrl in self._nav_controls:
            k = ctrl.data
            is_active = k == key
            ctrl.bgcolor = primary_light if is_active else "transparent"
            row = ctrl.content
            row.controls[1].color = primary if is_active else text_secondary
        self.update()

        if self.on_navigate:
            self.on_navigate(key)

    def set_active(self, key: str):
        """从外部切换页面"""
        self._active = key
        self._on_click(key)

    def update_theme(self, theme: dict):
        """更新侧边栏主题颜色"""
        self._theme = theme
        self.bgcolor = theme.get("CARD_BG", CARD_BG)

        primary = theme.get("PRIMARY", PRIMARY)
        primary_light = theme.get("PRIMARY_LIGHT", "#FFF7ED")
        text_secondary = theme.get("TEXT_SECONDARY", TEXT_SECONDARY)

        for ctrl in self._nav_controls:
            k = ctrl.data
            is_active = k == self._active
            ctrl.bgcolor = primary_light if is_active else "transparent"
            row = ctrl.content
            row.controls[1].color = primary if is_active else text_secondary
        self.update()