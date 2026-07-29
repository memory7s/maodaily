"""
月视图日历组件 —— 参考「指尖时光」风格
显示完整月份网格，有任务的日期标注橙色圆点，点击日期可筛选任务。
"""

import flet as ft
from datetime import datetime, date, timedelta
from .theme import PRIMARY, PRIMARY_LIGHT, TEXT_PRIMARY, TEXT_SECONDARY, CARD_BG, BG

WEEKDAYS = ["一", "二", "三", "四", "五", "六", "日"]


class CalendarView(ft.Container):
    """月视图日历组件"""

    def __init__(self, on_date_select=None, task_counts: dict = None):
        """
        Args:
            on_date_select: 回调函数 (date_str: 'YYYY-MM-DD') -> None
            task_counts: {'YYYY-MM-DD': count} 各日期任务数
        """
        self._on_date_select = on_date_select
        self._task_counts = task_counts or {}
        self._today = date.today()
        self._view_year = self._today.year
        self._view_month = self._today.month
        self._selected_date = None
        self._theme = {}  # 由外部 update_theme 设置

        # 月份标题 + 导航按钮
        self._month_label = ft.Text("", size=18, weight=ft.FontWeight.BOLD, color=TEXT_PRIMARY)
        self._prev_btn = ft.IconButton(
            icon=ft.Icons.CHEVRON_LEFT,
            icon_color=TEXT_SECONDARY,
            icon_size=20,
            on_click=self._prev_month,
            tooltip="上个月",
        )
        self._next_btn = ft.IconButton(
            icon=ft.Icons.CHEVRON_RIGHT,
            icon_color=TEXT_SECONDARY,
            icon_size=20,
            on_click=self._next_month,
            tooltip="下个月",
        )

        # 星期头
        self._weekday_row = ft.Row(
            controls=[
                ft.Container(
                    content=ft.Text(w, size=12, color=TEXT_SECONDARY, text_align=ft.TextAlign.CENTER),
                    width=40,
                    height=28,
                    alignment=ft.alignment.Alignment(0, 0),
                )
                for w in WEEKDAYS
            ],
            spacing=0,
            alignment=ft.MainAxisAlignment.CENTER,
        )

        # 日期网格容器
        self._grid = ft.Column(spacing=0, horizontal_alignment=ft.CrossAxisAlignment.CENTER)

        self._update_calendar()

        super().__init__(
            content=ft.Column(
                controls=[
                    # 导航栏
                    ft.Container(
                        content=ft.Row(
                            controls=[
                                self._prev_btn,
                                self._month_label,
                                self._next_btn,
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        ),
                        padding=ft.Padding.only(bottom=8),
                    ),
                    ft.Divider(height=1, color="#E0E0E0"),
                    # 星期头
                    ft.Container(
                        content=self._weekday_row,
                        padding=ft.Padding.symmetric(vertical=8),
                    ),
                    # 日期网格
                    self._grid,
                ],
                spacing=0,
            ),
            bgcolor=CARD_BG,
            border_radius=ft.BorderRadius.all(10),
            padding=ft.Padding.all(16),
            shadow=ft.BoxShadow(
                blur_radius=6, color="#1A000000", offset=ft.Offset(0, 2),
            ),
        )

    def update_task_counts(self, task_counts: dict):
        """更新任务计数并刷新日历"""
        self._task_counts = task_counts or {}
        self._update_calendar()

    def _update_calendar(self):
        """重建日期网格"""
        t = self._theme or {}
        text_primary = t.get("TEXT_PRIMARY", TEXT_PRIMARY)
        text_secondary = t.get("TEXT_SECONDARY", TEXT_SECONDARY)
        primary = t.get("PRIMARY", PRIMARY)
        primary_light = t.get("PRIMARY_LIGHT", PRIMARY_LIGHT)

        self._month_label.value = f"{self._view_year}年{self._view_month}月"

        # 计算当月第一天和最后一天
        first_day = date(self._view_year, self._view_month, 1)
        if self._view_month == 12:
            last_day = date(self._view_year, 12, 31)
        else:
            last_day = date(self._view_year, self._view_month + 1, 1) - timedelta(days=1)

        start_weekday = first_day.weekday()

        cells = []
        row_cells = []

        for _ in range(start_weekday):
            row_cells.append(self._empty_cell())

        for day in range(1, last_day.day + 1):
            d = date(self._view_year, self._view_month, day)
            date_str = d.strftime("%Y-%m-%d")
            count = self._task_counts.get(date_str, 0)
            is_today = d == self._today
            is_selected = date_str == self._selected_date

            row_cells.append(self._date_cell(d, day, count, is_today, is_selected, primary, primary_light, text_primary))

            if len(row_cells) == 7:
                cells.append(ft.Row(controls=row_cells, spacing=0, alignment=ft.MainAxisAlignment.CENTER))
                row_cells = []

        if row_cells:
            while len(row_cells) < 7:
                row_cells.append(self._empty_cell())
            cells.append(ft.Row(controls=row_cells, spacing=0, alignment=ft.MainAxisAlignment.CENTER))

        self._grid.controls = cells

    def _empty_cell(self):
        return ft.Container(width=40, height=40)

    def _date_cell(self, d: date, day: int, task_count: int, is_today: bool, is_selected: bool,
                   primary: str, primary_light: str, text_primary: str):
        date_str = d.strftime("%Y-%m-%d")

        dot = ft.Container(
            width=5,
            height=5,
            border_radius=ft.BorderRadius.all(3),
            bgcolor=primary if task_count > 0 else "transparent",
            margin=ft.Margin.only(top=2),
        )

        if is_selected:
            text_color = "#FFFFFF"
        elif is_today:
            text_color = primary
        elif d.month != self._view_month:
            text_color = "#DDDDDD"
        else:
            text_color = text_primary

        if is_selected:
            bg = primary
        elif is_today:
            bg = primary_light
        else:
            bg = "transparent"

        date_text = ft.Text(str(day), size=13, color=text_color, text_align=ft.TextAlign.CENTER)

        return ft.Container(
            content=ft.Column(
                controls=[date_text, dot],
                spacing=2,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                alignment=ft.MainAxisAlignment.CENTER,
            ),
            width=40,
            height=40,
            bgcolor=bg,
            border_radius=ft.BorderRadius.all(6),
            alignment=ft.alignment.Alignment(0, 0),
            on_click=lambda e, ds=date_str: self._on_date_click(ds),
            ink=True,
        )

    def _on_date_click(self, date_str: str):
        self._selected_date = date_str
        self._update_calendar()
        if self._on_date_select:
            self._on_date_select(date_str)

    def _prev_month(self, e):
        if self._view_month == 1:
            self._view_month = 12
            self._view_year -= 1
        else:
            self._view_month -= 1
        self._update_calendar()

    def _next_month(self, e):
        if self._view_month == 12:
            self._view_month = 1
            self._view_year += 1
        else:
            self._view_month += 1
        self._update_calendar()

    def go_to_today(self):
        """跳转到今天"""
        self._view_year = self._today.year
        self._view_month = self._today.month
        self._update_calendar()

    def update_theme(self, theme: dict):
        """更新日历主题颜色"""
        self._theme = theme
        t = theme or {}
        self.bgcolor = t.get("CARD_BG", CARD_BG)
        self._month_label.color = t.get("TEXT_PRIMARY", TEXT_PRIMARY)
        self._prev_btn.icon_color = t.get("TEXT_SECONDARY", TEXT_SECONDARY)
        self._next_btn.icon_color = t.get("TEXT_SECONDARY", TEXT_SECONDARY)

        text_secondary = t.get("TEXT_SECONDARY", TEXT_SECONDARY)
        for control in self._weekday_row.controls:
            text = control.content
            text.color = text_secondary

        divider_color = t.get("DIVIDER", "#E0E0E0")
        shadow_color = t.get("SHADOW", "#1A000000")
        self.shadow = ft.BoxShadow(blur_radius=6, color=shadow_color, offset=ft.Offset(0, 2))

        # 更新日历容器内的分割线
        outer_col = self.content
        if outer_col and outer_col.controls:
            nav_container = outer_col.controls[0]
            # 第一个 divider
            if len(outer_col.controls) > 1 and isinstance(outer_col.controls[1], ft.Divider):
                outer_col.controls[1].color = divider_color

        self._update_calendar()