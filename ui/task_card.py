"""
任务卡片组件 (TaskCard) + 步骤行组件 (StepRow)
"""

import flet as ft
from .theme import (
    PRIMARY, PRIMARY_LIGHT, CARD_BG, TEXT_PRIMARY, TEXT_SECONDARY,
    TEXT_DISABLED, DANGER, TAG_COLORS, PRIORITY_COLORS,
)

# ── 状态图标 ──
ICON_UNCHECKED = "○"
ICON_CHECKED = "●"
ICON_STEP_UNCHECKED = "○"
ICON_STEP_CHECKED = "✓"


class StepRow(ft.Row):
    """单个步骤行：勾选 + 描述 + 删除"""

    def __init__(
        self,
        step_data: dict,
        on_toggle=None,
        on_edit=None,
        on_delete=None,
    ):
        self._data = step_data
        self._on_toggle = on_toggle
        self._on_edit = on_edit
        self._on_delete = on_delete
        completed = step_data.get("completed", False)

        # 勾选图标
        chk_text = ICON_STEP_CHECKED if completed else ICON_STEP_UNCHECKED
        chk_color = TEXT_DISABLED if completed else TEXT_SECONDARY
        self.chk = ft.Text(chk_text, size=14, color=chk_color, width=20)

        # 描述文字
        desc_color = TEXT_DISABLED if completed else TEXT_SECONDARY
        self.desc = ft.TextField(
            value=step_data.get("description", ""),
            text_size=13,
            color=desc_color,
            bgcolor="transparent",
            border=ft.InputBorder.NONE,
            border_width=0,
            height=30,
            dense=True,
            read_only=True,
            expand=True,
        )

        # 删除按钮
        self.del_btn = ft.Text("✕", size=11, color="#CCCCCC")

        super().__init__(
            controls=[
                ft.Container(content=self.chk, on_click=self._handle_toggle),
                self.desc,
                ft.Container(
                    content=self.del_btn,
                    on_click=self._handle_delete,
                    on_hover=self._handle_del_hover,
                ),
            ],
            spacing=4,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )

    def _handle_toggle(self, e):
        if self._on_toggle:
            self._on_toggle(self._data)

    def _handle_delete(self, e):
        if self._on_delete:
            self._on_delete(self._data)

    def _handle_del_hover(self, e):
        self.del_btn.color = DANGER if e.data == "true" else "#CCCCCC"
        self.update()


class TaskCard(ft.Container):
    """任务卡片：标题 + 步骤 + 底栏"""

    def __init__(
        self,
        task_data: dict,
        page=None,
        on_toggle=None,
        on_delete=None,
        on_title_edit=None,
        on_step_toggle=None,
        on_step_add=None,
        on_step_edit=None,
        on_step_delete=None,
        on_show_detail=None,
        on_star=None,
    ):
        self._data = task_data
        self._expanded = False
        self._on_toggle = on_toggle
        self._on_delete = on_delete
        self._on_title_edit = on_title_edit
        self._on_step_toggle = on_step_toggle
        self._on_step_add = on_step_add
        self._on_step_edit = on_step_edit
        self._on_step_delete = on_step_delete
        self._on_show_detail = on_show_detail  # 点击标题时通知 App 切换详情面板
        self._on_star = on_star  # 右键标星回调
        self._page = page

        completed = task_data.get("completed", False)
        steps = task_data.get("steps", [])
        tag = task_data.get("tag", "")
        priority = task_data.get("priority", "")
        created_at = task_data.get("created_at", "")
        done_steps = sum(1 for s in steps if s.get("completed", False))
        total_steps = len(steps)
        pct = done_steps / total_steps if total_steps > 0 else 0

        # ── 顶栏 ──
        # 勾选圈
        chk_text = ICON_CHECKED if completed else ICON_UNCHECKED
        chk_color = TEXT_DISABLED if completed else PRIMARY
        self.chk = ft.Text(chk_text, size=16, color=chk_color)

        # 标题
        title_color = TEXT_DISABLED if completed else TEXT_PRIMARY
        self.title = ft.Text(
            task_data.get("title", ""),
            size=15,
            weight=ft.FontWeight.W_600,
            color=title_color,
            expand=True,
        )
        # GestureDetector 包装标题：点击 → 详情面板，长按/右键 → 菜单
        self.title_container = ft.Container(
            content=ft.GestureDetector(
                content=self.title,
                on_tap=self._show_detail_dialog,
                on_long_press=self._show_card_menu,
            ),
            expand=True,
            padding=ft.Padding.symmetric(horizontal=4),
        )

        # 优先级标记：标星任务 ⭐，未标星 ☆
        self.priority_dot = ft.Text(
            "⭐" if priority in ("高", "high") else "☆",
            size=16, width=20, text_align=ft.TextAlign.CENTER,
            color="#FF8700" if priority in ("高", "high") else "#CCCCCC",
        )

# ⋯ 菜单按钮（标记完成 / 标星 / 删除）
        menu_btn = ft.PopupMenuButton(
            items=[
                ft.PopupMenuItem(
                    content=ft.Text("标记为未完成" if completed else "标记为已完成"),
                    on_click=lambda e: self._do_card_toggle(),
                ),
                ft.PopupMenuItem(
                    content=ft.Text(
                        "取消标星" if priority in ("高", "high") else "标星重要任务"
                    ),
                    on_click=lambda e: self._do_card_star(),
                ),
                ft.PopupMenuItem(
                    content=ft.Text("删除任务"),
                    on_click=lambda e: self._do_card_delete(),
                ),
            ],
        )

        # ---- 任务头栏 ----
        header = ft.Row(
            controls=[
                ft.Container(content=self.chk, on_click=self._toggle_complete),
                self.title_container,          # 可点击的标题 → 详情面板
                ft.Container(
                    content=self.priority_dot,
                    tooltip=priority or "无优先级",
                    on_click=lambda e: self._do_card_star(),
                ),
                menu_btn,
            ],
            spacing=6,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )
        # 移除之前对 title 的点击绑定（已通过 GestureDispatcher）
        # self.title.on_click = ...   # 不再需要

        # ── 步骤容器（初始隐藏） ──
        self._steps_col = ft.Column(spacing=2, visible=False)
        self._add_step_input = ft.Row(
            controls=[
                ft.TextField(
                    hint_text="添加步骤...",
                    hint_style=ft.TextStyle(size=12, color=TEXT_SECONDARY),
                    text_size=12,
                    border=ft.InputBorder.NONE,
                    dense=True,
                    height=28,
                    expand=True,
                    on_submit=self._handle_add_step,
                ),
                ft.Text("+", size=16, color=PRIMARY),
            ],
            spacing=4,
            visible=False,
        )
        self._rebuild_steps(steps)

        # ── 底栏 ──
        bottom_items = []

        # 标签
        if tag:
            tag_color = TAG_COLORS.get(tag, "#868E96")
            tag_badge = ft.Container(
                content=ft.Text(tag, size=10, color="white"),
                bgcolor=tag_color,
                border_radius=ft.BorderRadius.all(4),
                padding=ft.Padding.symmetric(horizontal=6, vertical=2),
            )
            bottom_items.append(tag_badge)

        # 日期
        if created_at:
            bottom_items.append(
                ft.Text(
    self._format_date(created_at),
    size=10,
     color=TEXT_SECONDARY)
            )

        # 进度
        if total_steps > 0:
            progress_bar = ft.Container(
                content=ft.Container(
                    height=6,
                    bgcolor=PRIMARY,
                    border_radius=ft.BorderRadius.all(3),
                ),
                width=80,
                height=6,
                bgcolor="#E0E0E0",
                border_radius=ft.BorderRadius.all(3),
                clip_behavior=ft.ClipBehavior.HARD_EDGE,
            )
            # 设置进度条填充宽度
            progress_bar.content.width = int(80 * pct)

            bottom_items.append(
                ft.Row(
                    controls=[
                        progress_bar,
                        ft.Text(
                            f"{done_steps}/{total_steps}",
                            size=10,
                            color=TEXT_SECONDARY,
                        ),
                    ],
                    spacing=4,
                )
            )

        bottom_row = ft.Row(
            controls=bottom_items,
            spacing=12,
        ) if bottom_items else None

        # ── 组装卡片 ──
        card_content = ft.Column(
            controls=[header],
            spacing=6,
        )

        card_content.controls.append(self._steps_col)
        card_content.controls.append(self._add_step_input)
        if bottom_row:
            card_content.controls.append(bottom_row)

        super().__init__(
            content=card_content,
            bgcolor=CARD_BG,
            border_radius=ft.BorderRadius.all(10),
            padding=ft.Padding.all(14),
            ink=False,
            shadow=ft.BoxShadow(
                blur_radius=6,
                color="#1A000000",
                offset=ft.Offset(0, 2),
            ),
            margin=ft.Margin.only(bottom=8),
        )

        # 标题点击展开/收起 (已改为点击弹出详情编辑框)
        # self.title.on_click = self._toggle_expand
        # self.title.on_hover = self._title_hover

    # ── 公共方法 ──
    def update_data(self, task_data: dict):
        """更新卡片数据并刷新 UI"""
        self._data = task_data
        self._rebuild_steps(task_data.get("steps", []))
        # Update title
        self.title.value = task_data.get("title", "")
        # Update completion
        completed = task_data.get("completed", False)
        self.chk.value = ICON_CHECKED if completed else ICON_UNCHECKED
        self.chk.color = TEXT_DISABLED if completed else PRIMARY
        self.title.color = TEXT_DISABLED if completed else TEXT_PRIMARY
        self.update()

    def set_expanded(self, expanded: bool):
        self._expanded = expanded
        self._steps_col.visible = expanded
        self._add_step_input.visible = expanded
        self.update()

    # ── 内部逻辑 ──
    def _rebuild_steps(self, steps):
        self._steps_col.controls.clear()
        for s in steps:
            row = StepRow(
                s,
                on_toggle=self._handle_step_toggle,
                on_edit=self._handle_step_edit,
                on_delete=self._handle_step_delete,
            )
            self._steps_col.controls.append(row)

    @staticmethod
    def _format_date(iso_str: str) -> str:
        from datetime import datetime, date as date_cls
        try:
            dt = datetime.fromisoformat(iso_str)
        except (ValueError, TypeError):
            return iso_str
        today = date_cls.today()
        task_date = dt.date()
        diff = (today - task_date).days
        if diff == 0:
            return "今天"
        elif diff == 1:
            return "昨天"
        return f"{dt.month}月{dt.day}日"

    def _toggle_complete(self, e):
        if self._on_toggle:
            self._on_toggle(self._data)

    def _delete_task(self, e):
        if self._on_delete:
            self._on_delete(self._data)

    def _del_hover(self, e):
        self.del_btn.color = DANGER if e.data == "true" else TEXT_SECONDARY
        self.update()

    def _title_hover(self, e):
        self.title.color = PRIMARY if e.data == "true" else TEXT_PRIMARY
        self.update()

    def _toggle_expand(self, e):
        self._expanded = not self._expanded
        self._steps_col.visible = self._expanded
        self._add_step_input.visible = self._expanded
        self.update()

    def _handle_step_toggle(self, step_data):
        if self._on_step_toggle:
            self._on_step_toggle(self._data, step_data)

    def _handle_step_edit(self, step_data):
        if self._on_step_edit:
            self._on_step_edit(self._data, step_data)

    def _handle_step_delete(self, step_data):
        if self._on_step_delete:
            self._on_step_delete(self._data, step_data)

    def _handle_add_step(self, e):
        desc = e.control.value.strip()
        if desc and self._on_step_add:
            self._on_step_add(self._data, desc)
            e.control.value = ""
            e.control.update()

    # ----- 点击标题 → 通知 App 切换右侧详情面板 -----
    def _show_detail_dialog(self, e):
        """通知 App：当前任务的详情面板开关"""
        print("_show_detail_dialog called")
        if self._on_show_detail:
            self._on_show_detail(self._data)

    # ----- ⋯ 菜单操作 -----
    def _show_card_menu(self, e=None):
        """长按标题 / 右键 → 弹出菜单"""
        completed = self._data.get('completed', False)
        is_starred = self._data.get('priority') in ('高', 'high')

        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text("任务操作"),
            actions=[
                ft.TextButton(
                    "标记为未完成" if completed else "标记为已完成",
                    on_click=lambda ev: self._do_rc_toggle(dlg),
                ),
                ft.TextButton(
                    "取消标星" if is_starred else "标星重要任务",
                    on_click=lambda ev: self._do_rc_star(dlg),
                ),
                ft.TextButton(
                    "删除任务",
                    on_click=lambda ev: self._do_rc_delete(dlg),
                ),
                ft.TextButton("取消", on_click=lambda ev: self._dismiss_dlg(dlg)),
            ],
        )
        self._page.dialog = dlg
        dlg.open = True
        self._page.update()

    def _dismiss_dlg(self, dlg):
        dlg.open = False
        self._page.update()

    def _do_rc_toggle(self, dlg):
        self._dismiss_dlg(dlg)
        if self._on_toggle:
            self._on_toggle(self._data)

    def _do_rc_star(self, dlg):
        self._dismiss_dlg(dlg)
        if self._on_star:
            self._on_star(self._data)

    def _do_rc_delete(self, dlg):
        self._dismiss_dlg(dlg)
        if self._on_delete:
            self._on_delete(self._data)

    def _do_card_toggle(self):
        """⋯ 菜单按钮：标记完成/未完成"""
        if self._on_toggle:
            self._on_toggle(self._data)

    def _do_card_star(self):
        """⋯ 菜单按钮：标星/取消标星"""
        if self._on_star:
            self._on_star(self._data)

    def _do_card_delete(self):
        """⋯ 菜单按钮：删除任务"""
        if self._on_delete:
            self._on_delete(self._data)
