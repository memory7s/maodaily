"""
侧边导航栏 —— NavigationRail 风格
"""

import flet as ft
from .theme import PRIMARY, TEXT_SECONDARY


class Sidebar(ft.Container):
    """左侧导航栏组件"""

    NAV_ITEMS = [
        ("📋", "今日计划", "today"),
        ("📅", "日历视图", "calendar"),
        ("🏷", "分类", "tags"),
    ]

    def __init__(self, on_navigate=None):
        self.on_navigate = on_navigate
        self._active = "today"
        self._nav_controls = []

        super().__init__(
            width=180,
            bgcolor="#FFFFFF",
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
        for ctrl in self._nav_controls:
            k = ctrl.data
            is_active = k == key
            ctrl.bgcolor = "#FFF7ED" if is_active else "transparent"
            # 更新文字颜色
            row = ctrl.content
            row.controls[1].color = PRIMARY if is_active else TEXT_SECONDARY
        self.update()

        if self.on_navigate:
            self.on_navigate(key)

    def set_active(self, key: str):
        """从外部切换页面"""
        self._active = key
        self._on_click(key)
