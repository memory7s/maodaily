"""
侧边导航栏 —— NavigationRail 风格
支持折叠：点击 MaoDaily 旁的按钮收起为纯图标模式，再点展开恢复原宽度。
"""

import flet as ft
from .ricons import RI, ri
from .theme import PRIMARY, TEXT_SECONDARY, TEXT_PRIMARY, CARD_BG


class Sidebar(ft.Container):
    """左侧导航栏组件（可折叠为纯图标模式）"""

    # 折叠时的宽度（与 App 的 _sidebar_min_width 保持一致）
    COLLAPSED_WIDTH = 52

    # (图标字形(RemixIcon), 标签, key)
    NAV_ITEMS = [
        (RI.LIST_CHECK, "全部", "all"),
        (RI.BRIEFCASE, "工作", "tag:工作"),
        (RI.BOOK_OPEN, "学习", "tag:学习"),
        (RI.HOME, "生活", "tag:生活"),
        (RI.PAUSE_CIRCLE, "暂时不做", "tag:暂时不做"),
        (RI.FORBID, "就是不做", "tag:就是不做"),
        (RI.CALENDAR, "日历", "calendar"),
        (RI.SETTINGS, "设置", "settings"),
    ]

    def __init__(self, on_navigate=None, on_collapse_toggle=None):
        self.on_navigate = on_navigate
        self.on_collapse_toggle = on_collapse_toggle  # 折叠状态变化回调: fn(collapsed: bool)
        self._active = "all"
        self._collapsed = False
        self._nav_controls = []
        self._nav_labels = []  # 与 _nav_controls 一一对应的文字引用
        self._theme = None  # 由外部 update_theme 设置
        self._title_container = None

        super().__init__(
            width=180,
            bgcolor=CARD_BG,
            padding=ft.Padding.only(top=16, left=8, right=8),
            content=self._build(),
        )

    def _build(self):
        col = ft.Column(spacing=4, controls=[])

        # ── 头部：标题 + 伸缩按钮（靠右）──
        self._toggle_btn = ft.Container(
            content=ri(RI.MENU_FOLD, size=18, color=TEXT_SECONDARY),
            width=30,
            height=30,
            border_radius=ft.BorderRadius.all(6),
            alignment=ft.alignment.Alignment.CENTER,
            ink=True,
            tooltip="收起导航栏",
            on_click=lambda e: self.toggle_collapsed(),
        )
        self._title_text = ft.Text(
            "MaoDaily",
            size=18,
            weight=ft.FontWeight.W_600,
            color=TEXT_PRIMARY,
            font_family="Geist",
        )
        self._title_container = ft.Container(
            content=self._title_text,
            padding=ft.Padding.only(left=4),
            expand=True,
        )
        self._header_row = ft.Row(
            controls=[self._title_container, self._toggle_btn],
            spacing=6,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )
        col.controls.append(self._header_row)
        col.controls.append(ft.Container(height=10))

        for icon_glyph, label, key in self.NAV_ITEMS:
            btn = self._nav_item(icon_glyph, label, key)
            col.controls.append(btn)
            self._nav_controls.append(btn)

        return col

    def _nav_color(self) -> str:
        """导航文字/图标颜色（比次级灰深一档，随主题切换）"""
        theme = self._theme or {}
        return theme.get("NAV_TEXT", "#666666")

    def _nav_item(self, icon_glyph, label, key):
        is_active = key == self._active
        color = self._nav_color()
        icon_box = ft.Container(
            content=ri(icon_glyph, size=18, color=color),
            width=22,
        )
        # 中文标签不指定 Geist（其无 CJK 字形，会导致系统逐字回落、粗细不一）
        label_text = ft.Text(label, size=14, weight=ft.FontWeight.W_500, color=color)
        self._nav_labels.append(label_text)
        return ft.Container(
            data=key,
            content=ft.Row(
                controls=[icon_box, label_text],
            ),
            padding=ft.Padding.symmetric(horizontal=12, vertical=10),
            border_radius=ft.BorderRadius.all(8),
            bgcolor="#FFF7ED" if is_active else "transparent",
            ink=True,
            on_click=lambda e, k=key: self._on_click(k),
        )

    def _on_click(self, key):
        self._active = key
        # 激活只通过背景区分，文字/图标颜色保持统一（避免深浅粗细差异）
        theme = self._theme or {}
        primary_light = theme.get("PRIMARY_LIGHT", "#FFF7ED")

        for ctrl in self._nav_controls:
            k = ctrl.data
            is_active = k == key
            ctrl.bgcolor = primary_light if is_active else "transparent"
        try:
            self.update()
        except RuntimeError:
            pass

        if self.on_navigate:
            self.on_navigate(key)

    # ── 折叠/展开 ──

    def toggle_collapsed(self, e=None):
        self.set_collapsed(not self._collapsed)

    def set_collapsed(self, collapsed: bool):
        """切换折叠状态：折叠后只显示图标，并通知外部调整宽度"""
        if collapsed == self._collapsed:
            return
        self._collapsed = collapsed

        # 头部：切换字形、隐藏标题和logo、整体居中
        if isinstance(self._toggle_btn.content, ft.Text):
            self._toggle_btn.content.value = RI.MENU_UNFOLD if collapsed else RI.MENU_FOLD
        self._toggle_btn.tooltip = "展开导航栏" if collapsed else "收起导航栏"
        self._header_row.alignment = (
            ft.MainAxisAlignment.CENTER if collapsed else ft.MainAxisAlignment.START
        )
        if self._title_container:
            self._title_container.visible = not collapsed

        # 导航项：隐藏文字、图标居中、去掉水平内边距
        for ctrl, label in zip(self._nav_controls, self._nav_labels):
            label.visible = not collapsed
            ctrl.content.alignment = (
                ft.MainAxisAlignment.CENTER if collapsed else ft.MainAxisAlignment.START
            )
            ctrl.padding = (
                ft.Padding.symmetric(vertical=10)
                if collapsed
                else ft.Padding.symmetric(horizontal=12, vertical=10)
            )

        try:
            self.update()
        except RuntimeError:
            pass

        if self.on_collapse_toggle:
            self.on_collapse_toggle(collapsed)

    @property
    def is_collapsed(self) -> bool:
        return self._collapsed

    def set_active(self, key: str):
        """从外部切换页面"""
        self._active = key
        self._on_click(key)

    def set_width(self, w: int):
        """设置侧栏宽度，窄于阈值时隐藏标题（折叠状态下标题始终隐藏）"""
        if self._title_container:
            self._title_container.visible = (not self._collapsed) and w > 100

    def update_theme(self, theme: dict):
        """更新侧边栏主题颜色（激活只靠背景，文字/图标统一导航色）"""
        self._theme = theme
        self.bgcolor = theme.get("CARD_BG", CARD_BG)
        primary_light = theme.get("PRIMARY_LIGHT", "#FFF7ED")
        color = self._nav_color()

        # 标题跟随主题主文字色（亮色≈黑、暗色≈浅灰、Neo≈墨黑）
        if self._title_text:
            self._title_text.color = theme.get("TEXT_PRIMARY", TEXT_PRIMARY)

        # 导航项文字与图标统一加深
        for ctrl, label in zip(self._nav_controls, self._nav_labels):
            label.color = color
            icon_text = ctrl.content.controls[0].content if ctrl.content and ctrl.content.controls else None
            if isinstance(icon_text, ft.Text):
                icon_text.color = color

        for ctrl in self._nav_controls:
            k = ctrl.data
            is_active = k == self._active
            ctrl.bgcolor = primary_light if is_active else "transparent"
        try:
            self.update()
        except RuntimeError:
            pass
