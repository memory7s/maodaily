"""
设置面板 —— 数据存储 + 备份恢复 + 风格偏好
仿照「木子工作台」设置页的结构，用 Flet 实现。
"""

import os
import flet as ft
from .ricons import RI, ri
from .theme import (
    PRIMARY, TEXT_PRIMARY, TEXT_SECONDARY, CARD_BG,
    SUCCESS, DANGER, BG,
)

# 风格选项（key -> (图标字形(RemixIcon), 名称, 描述)）
STYLE_OPTIONS = {
    "light": (RI.STYLE_LIGHT, "亮色", "清爽明亮的默认风格"),
    "dark": (RI.STYLE_DARK, "暗色", "适合夜间长时间使用"),
    "neo": (RI.STYLE_NEO, "Neo-Brutalism", "米黄纸·硬边框·硬阴影"),
}

MODE_LABELS = {
    "light": "亮色主题",
    "dark": "暗色主题",
    "neo": "Neo-Brutalism 主题",
}


class Section(ft.Container):
    """设置分区卡片：标题 + 描述 + 内容"""

    def __init__(self, title: str, description: str = "", content=None):
        super().__init__(
            content=ft.Column(
                controls=[
                    ft.Column(
                        controls=[
                            ft.Text(title, size=15, weight=ft.FontWeight.BOLD, color=TEXT_PRIMARY),
                            ft.Text(description, size=12, color=TEXT_SECONDARY) if description else ft.Container(),
                        ],
                        spacing=2,
                    ),
                    content or ft.Container(),
                ],
                spacing=12,
            ),
            padding=ft.Padding.all(16),
            bgcolor=CARD_BG,
            border_radius=ft.BorderRadius.all(10),
        )
        self._theme = {}

    def update_theme(self, theme: dict):
        self._theme = theme
        self.bgcolor = theme.get("CARD_BG", CARD_BG)
        # 边框/圆角跟随主题（Neo 硬边框）
        border_color = theme.get("CARD_BORDER", "transparent")
        border_width = theme.get("CARD_BORDER_WIDTH", 0)
        if border_color in (None, "transparent") or border_width == 0:
            self.border = None
        else:
            side = ft.BorderSide(border_width, border_color)
            self.border = ft.Border(left=side, right=side, top=side, bottom=side)
        self.border_radius = ft.BorderRadius.all(theme.get("RADIUS_CARD", 10))
        # 标题颜色
        col = self.content
        if col and col.controls:
            title_col = col.controls[0]
            if title_col and title_col.controls:
                title_col.controls[0].color = theme.get("TEXT_PRIMARY", TEXT_PRIMARY)
                if len(title_col.controls) > 1:
                    title_col.controls[1].color = theme.get("TEXT_SECONDARY", TEXT_SECONDARY)
        try:
            self.update()
        except RuntimeError:
            pass


class SettingsView(ft.Column):
    """设置页面：数据文件 / 备份与恢复 / 使用偏好"""

    def __init__(
        self,
        task_manager,
        theme_manager,
        on_open_data_dir=None,
        on_style_select=None,
        on_backup_created=None,
        page=None,
    ):
        self._task_manager = task_manager
        self._theme_manager = theme_manager
        self._on_open_data_dir = on_open_data_dir
        self._on_style_select = on_style_select
        self._on_backup_created = on_backup_created
        self._page = page
        self._backup_rows = []

        # ── 数据文件区 ──
        self._file_path_text = ft.Text("—", size=12, color=TEXT_SECONDARY, selectable=True)
        self._file_size_text = ft.Text("", size=12, color=TEXT_SECONDARY)
        self._file_modified_text = ft.Text("", size=12, color=TEXT_SECONDARY)
        self._file_writable_badge = ft.Container(
            content=ft.Text("可读写", size=11, weight=ft.FontWeight.W_600, color="#FFFFFF"),
            padding=ft.Padding.symmetric(horizontal=8, vertical=3),
            border_radius=ft.BorderRadius.all(4),
            bgcolor=SUCCESS,
        )
        self._task_count_text = ft.Text("", size=12, color=TEXT_SECONDARY)
        open_dir_btn = ft.ElevatedButton(
            "打开数据目录",
            icon=ri(RI.FOLDER_OPEN, size=16),
            on_click=lambda e: self._open_data_dir(),
        )

        file_section = Section(
            title="数据文件",
            description="业务数据保存在项目目录之外的 JSON 文件中",
            content=ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            ft.Container(
                                content=ri(RI.FILE_TEXT, size=24, color=PRIMARY),
                                width=48,
                                height=48,
                                bgcolor=BG,
                                border_radius=ft.BorderRadius.all(8),
                                alignment=ft.alignment.Alignment.CENTER,
                            ),
                            ft.Column(
                                controls=[
                                    ft.Text("tasks.json", size=14, weight=ft.FontWeight.W_600, color=TEXT_PRIMARY),
                                    self._file_path_text,
                                    ft.Row(
                                        controls=[
                                            self._file_size_text,
                                            self._file_modified_text,
                                            self._task_count_text,
                                        ],
                                        spacing=12,
                                    ),
                                    ft.Row(
                                        controls=[self._file_writable_badge],
                                        spacing=8,
                                    ),
                                ],
                                spacing=4,
                            ),
                            ft.Container(expand=True),
                            open_dir_btn,
                        ],
                        vertical_alignment=ft.CrossAxisAlignment.START,
                    ),
                ],
            ),
        )
        self._file_section = file_section

        # ── 备份与恢复区 ──
        self._backup_list = ft.Column(spacing=8)
        self._backup_empty_hint = ft.Text(
            "还没有备份。每日首次启动会自动创建一份，也可以点下方按钮立即备份。",
            size=12,
            color=TEXT_SECONDARY,
        )
        backup_section = Section(
            title="备份与恢复",
            description="每次恢复前会自动创建一份“恢复前安全备份”；自动备份保留最近 3 份",
            content=ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            ft.ElevatedButton(
                                "立即备份",
                                icon=ri(RI.SHIELD_CHECK, size=16),
                                on_click=lambda e: self._create_backup(),
                            ),
                        ],
                        spacing=8,
                    ),
                    self._backup_list,
                    self._backup_empty_hint,
                ],
                spacing=12,
            ),
        )
        self._backup_section = backup_section

        # ── 使用偏好区：界面风格 ──
        style_btn_col = ft.Row(spacing=10)
        self._style_buttons = {}
        for key, (icon, name, desc) in STYLE_OPTIONS.items():
            btn = self._build_style_card(key, icon, name, desc)
            self._style_buttons[key] = btn
            style_btn_col.controls.append(btn)
        self._style_btn_col = style_btn_col

        prefs_section = Section(
            title="使用偏好",
            description="选择界面风格，业务数据完全一致，只改变视觉",
            content=ft.Column(
                controls=[
                    ft.Column(
                        controls=[
                            ft.Text("界面风格", size=13, weight=ft.FontWeight.W_600, color=TEXT_PRIMARY),
                            ft.Text("三种外观，业务数据完全一致，只改变视觉", size=12, color=TEXT_SECONDARY),
                            self._style_btn_col,
                        ],
                        spacing=8,
                    ),
                ],
                spacing=16,
            ),
        )
        self._prefs_section = prefs_section

        super().__init__(
            controls=[
                ft.Row(
                    controls=[
                        ri(RI.SETTINGS_FILL, size=22, color=PRIMARY),
                        ft.Text("设置", size=22, weight=ft.FontWeight.BOLD, color=TEXT_PRIMARY),
                    ],
                    spacing=8,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                ft.Text("数据存储、备份恢复与界面偏好", size=12, color=TEXT_SECONDARY),
                file_section,
                backup_section,
                prefs_section,
            ],
            spacing=14,
            scroll=ft.ScrollMode.AUTO,
            expand=True,
        )

    # ── 构建风格卡片按钮 ──

    def _build_style_card(self, key: str, icon: str, name: str, desc: str):
        return ft.Container(
            data=key,
            content=ft.Column(
                controls=[
                    ft.Text(icon, size=22, font_family=RI.FONT),
                    ft.Text(name, size=13, weight=ft.FontWeight.W_600, color=TEXT_PRIMARY),
                    ft.Text(desc, size=11, color=TEXT_SECONDARY),
                ],
                spacing=3,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            width=150,
            padding=ft.Padding.all(12),
            border_radius=ft.BorderRadius.all(8),
            bgcolor=BG,
            border=ft.Border.all(2, "transparent"),
            ink=True,
            on_click=lambda e, k=key: self._select_style(k),
        )

    def _select_style(self, key: str):
        if self._on_style_select:
            self._on_style_select(key)
        self._refresh_style_buttons()

    # ── 刷新选中态 ──

    def _refresh_style_buttons(self):
        current = self._theme_manager.mode
        theme = self._theme_manager.current
        primary = theme.get("PRIMARY", PRIMARY)
        primary_light = theme.get("PRIMARY_LIGHT", "#FFF7ED")
        border_color = theme.get("INPUT_BORDER", "#E0E0E0")
        for key, ctrl in self._style_buttons.items():
            active = key == current
            ctrl.bgcolor = primary_light if active else theme.get("BG", BG)
            ctrl.border = ft.Border.all(2, primary if active else "transparent")
            col = ctrl.content
            if col and col.controls:
                col.controls[1].color = primary if active else theme.get("TEXT_PRIMARY", TEXT_PRIMARY)
        try:
            self.update()
        except RuntimeError:
            pass

    def _refresh_theme_buttons(self):
        """（已移除浅/深主题选择，保留空实现以兼容调用）"""
        pass

    # ── 数据文件区 ──

    def _open_data_dir(self):
        if self._on_open_data_dir:
            self._on_open_data_dir()

    def refresh_data_file(self):
        """刷新数据文件信息"""
        status = self._task_manager.get_data_file_status()
        self._file_path_text.value = status["path"]
        self._file_size_text.value = f"大小 {status['size']}"
        self._file_modified_text.value = f"修改于 {status['modified']}"
        self._task_count_text.value = f"{status['task_count']} 个任务"
        badge = self._file_writable_badge
        badge.bgcolor = SUCCESS if status["writable"] else DANGER
        badge.content.value = "可读写" if status["writable"] else "只读"
        try:
            self.update()
        except RuntimeError:
            pass

    # ── 备份区 ──

    def refresh_backups(self):
        """刷新备份列表"""
        backups = self._task_manager.list_backups(include_missing=False)
        self._backup_list.controls.clear()
        self._backup_empty_hint.visible = not backups
        for b in backups[:15]:
            row = self._build_backup_row(b)
            self._backup_list.controls.append(row)
        try:
            self.update()
        except RuntimeError:
            pass

    def _build_backup_row(self, record: dict) -> ft.Container:
        theme = self._theme_manager.current
        primary = theme.get("PRIMARY", PRIMARY)
        text_secondary = theme.get("TEXT_SECONDARY", TEXT_SECONDARY)
        type_badge_map = {
            "manual": ("手动", "accent"),
            "automatic": ("自动", "neutral"),
            "safety": ("安全", "warning"),
        }
        label, _ = type_badge_map.get(record.get("type", "manual"), ("手动", "accent"))
        created = record.get("created_at", "")[:16].replace("T", " ")
        return ft.Container(
            content=ft.Row(
                controls=[
                    ft.Container(
                        content=ft.Text(label, size=11, weight=ft.FontWeight.W_600, color="#FFFFFF"),
                        padding=ft.Padding.symmetric(horizontal=8, vertical=3),
                        border_radius=ft.BorderRadius.all(4),
                        bgcolor=primary,
                    ),
                    ft.Column(
                        controls=[
                            ft.Text(record.get("label", ""), size=13, color=theme.get("TEXT_PRIMARY", TEXT_PRIMARY)),
                            ft.Text(f"{created} · {record.get('size', '')}", size=11, color=text_secondary),
                        ],
                        spacing=2,
                        expand=True,
                    ),
                    ft.OutlinedButton(
                        "恢复",
                        icon=ri(RI.HISTORY, size=16, color=text_secondary),
                        on_click=lambda e, bid=record.get("id"): self._restore_backup(bid),
                    ),
                    ft.IconButton(
                        icon=ri(RI.DELETE, size=18, color=text_secondary),
                        tooltip="删除这份备份",
                        on_click=lambda e, bid=record.get("id"): self._delete_backup(bid),
                    ),
                ],
                spacing=8,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=ft.Padding.symmetric(horizontal=12, vertical=8),
            border_radius=ft.BorderRadius.all(6),
            bgcolor=theme.get("STEP_BOX_BG", "#F8F9FA"),
            border=ft.Border.all(1, theme.get("STEP_BOX_BORDER", "#E0E0E0")),
        )

    def _create_backup(self):
        try:
            self._task_manager.create_backup("manual", "手动备份")
            self.refresh_backups()
            if self._on_backup_created:
                self._on_backup_created("备份创建成功")
        except OSError as exc:
            if self._on_backup_created:
                self._on_backup_created(f"备份失败: {exc}")

    def _restore_backup(self, backup_id: str):
        if not self._page:
            return
        ok = self._task_manager.restore_backup(backup_id)
        if self._on_backup_created:
            self._on_backup_created("已恢复" if ok else "恢复失败：备份文件不可读")
        if ok:
            self.refresh_backups()
            self.refresh_data_file()

    def _delete_backup(self, backup_id: str):
        if not self._page:
            return
        self._task_manager.delete_backup(backup_id)
        self.refresh_backups()

    # ── 主题刷新 ──

    def update_theme(self, theme: dict):
        for section in (self._file_section, self._backup_section, self._prefs_section):
            section.update_theme(theme)
        self._refresh_style_buttons()
        # 内容文字随主题
        try:
            self.update()
        except RuntimeError:
            pass