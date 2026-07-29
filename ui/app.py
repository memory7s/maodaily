"""
主 App 页面 —— 侧栏 + 内容区布局骨架
Phase 2: 使用 TaskCard 组件展示任务列表（假数据）
"""

import flet as ft
from .theme import PRIMARY, BG, TEXT_PRIMARY, TEXT_SECONDARY, CARD_BG, ThemeManager
from .sidebar import Sidebar
from .task_card import TaskCard
from .calendar_view import CalendarView
from datetime import datetime
from task_manager import TaskManager


def build_header(on_calendar_toggle=None, theme_toggle_btn=None) -> ft.Container:
    """顶部标题栏"""
    now = datetime.now()
    weekday_cn = ["一", "二", "三", "四", "五", "六", "日"]
    date_str = f"{now.year}年{now.month}月{now.day}日 周{weekday_cn[now.weekday()]}"

    header_controls = [
        ft.IconButton(
            icon=ft.Icons.CALENDAR_MONTH,
            icon_color=TEXT_SECONDARY,
            tooltip="日历",
            on_click=on_calendar_toggle,
        ),
    ]
    if theme_toggle_btn:
        header_controls.append(theme_toggle_btn)

    return ft.Container(
        content=ft.Row(
            controls=[
                ft.Column(
                    controls=[
                        ft.Text("计划与进展", size=22, weight=ft.FontWeight.BOLD, color=TEXT_PRIMARY),
                        ft.Text(date_str, size=12, color=TEXT_SECONDARY),
                    ],
                    spacing=2,
                ),
                ft.Row(
                    controls=header_controls,
                ),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        ),
        padding=ft.Padding.only(left=4, right=4, bottom=8),
    )


def build_add_bar(on_add) -> ft.Container:
    """底部添加任务栏"""

    field = ft.TextField(
        hint_text="添加新任务...",
        hint_style=ft.TextStyle(color=TEXT_SECONDARY, size=14),
        border=ft.InputBorder.OUTLINE,
        border_color=CARD_BG,
        focused_border_color=PRIMARY,
        border_radius=ft.BorderRadius.all(8),
        filled=True,
        fill_color="#FFFFFF",
        expand=True,
        height=44,
        text_size=14,
        on_submit=lambda e: _do_add(field, on_add),
    )

    def _do_add(tf, callback):
        val = tf.value.strip()
        if val:
            callback(val)
            tf.value = ""
            tf.update()

    btn = ft.FloatingActionButton(
        icon=ft.Icons.ADD,
        bgcolor=PRIMARY,
        foreground_color="#FFFFFF",
        mini=True,
        on_click=lambda e: _do_add(field, on_add),
    )

    return ft.Container(
        content=ft.Row(
            controls=[field, btn],
            spacing=8,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        padding=ft.Padding.only(top=8, bottom=4),
    )


# ── 假数据（Phase 3 将替换为 task_manager.py） ──



class DeskApp(ft.Container):
    """主应用容器"""

    def __init__(self, page: ft.Page):
        super().__init__(expand=True, bgcolor=BG)
        self._page = page
        self._task_card_controls = []  # 所有 TaskCard 控件引用
        self.task_manager = TaskManager()

        # 主题管理
        self.theme_manager = ThemeManager()
        self._theme_toggle_btn = ft.IconButton(
            icon=ft.Icons.DARK_MODE,
            icon_color=TEXT_SECONDARY,
            tooltip="切换暗色主题",
            on_click=self._toggle_theme,
        )

        # 当前 tag 筛选（None=全部，字符串=特定 tag）
        self._current_tag_filter = None

        # 日历模式状态
        self._is_calendar_mode = False
        self._calendar_date_filter = None  # 当前日历选中的日期

        # 详情面板状态
        self._detail_task_id = None
        self._detail_data = None
        self._detail_title_field = None
        self._detail_step_fields = []
        self._detail_steps_col = None

        # 启动提醒通知轮询（主线程检查队列，每 1 秒）
        self._start_notification_checker()

        # 构建任务列表容器（内部是一个 Column + ScrollView）
        self._task_scroll = ft.Column(spacing=0, scroll=ft.ScrollMode.AUTO, expand=True)
        self._task_list_container = ft.Container(
            content=self._task_scroll,
            expand=True,
        )

        # 构建日历视图
        self._calendar_view = CalendarView(
            on_date_select=self._on_calendar_date_select,
            task_counts=self.task_manager.get_task_count_by_date(),
        )
        self._calendar_back_btn = ft.TextButton(
            "← 返回任务列表",
            icon=ft.Icons.ARROW_BACK,
            on_click=lambda e: self._on_navigate("all"),
            style=ft.ButtonStyle(color=TEXT_SECONDARY),
        )
        self._calendar_task_list = ft.Column(spacing=0, scroll=ft.ScrollMode.AUTO, expand=True)
        self._calendar_section = ft.Column(
            controls=[
                self._calendar_view,
                ft.Divider(height=1, color=self._get_theme_color("DIVIDER", "#E0E0E0")),
                ft.Container(
                    content=ft.Row([
                        ft.Text("📋 选中日期的任务", size=13, weight=ft.FontWeight.BOLD, color=self._get_theme_color("TEXT_SECONDARY", TEXT_SECONDARY)),
                        self._calendar_back_btn,
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    padding=ft.Padding.symmetric(vertical=8),
                ),
                ft.Container(
                    content=self._calendar_task_list,
                    expand=True,
                ),
            ],
            spacing=0,
            expand=True,
            visible=False,
        )

        # 构建右侧详情面板（初始隐藏，无内容）
        self._detail_panel = ft.Container(
            content=ft.Text(""),
            bgcolor=CARD_BG,
            border_radius=ft.BorderRadius.all(10),
            padding=ft.Padding.only(left=16, top=16, right=24, bottom=16),
            visible=False,
            expand=True,
        )
        self._detail_divider = ft.VerticalDivider(width=1, color="#E0E0E0", visible=False)

        # 存储 divider 引用以便主题切换时更新
        self._header_divider = ft.Divider(height=1, color="#E0E0E0")
        self._sidebar_divider = ft.VerticalDivider(width=1, color="#E0E0E0")

        # 加载真实任务数据
        self._load_tasks(self._current_tag_filter)

        # 布局: Row(侧栏 | 任务列表 + 可能的分隔线 + 详情面板)
        self.sidebar = Sidebar(on_navigate=self._on_navigate)
        self._task_area = ft.Container(
            content=ft.Column(
                controls=[
                    build_header(on_calendar_toggle=lambda: self._toggle_calendar(), theme_toggle_btn=self._theme_toggle_btn),
                    self._header_divider,
                    self._task_list_container,
                    self._calendar_section,
                    build_add_bar(self._on_add_task),
                ],
                expand=True,
            ),
            expand=True,
            padding=ft.Padding.only(left=24, right=12, top=20, bottom=20),
        )

        # 详情面板区域
        self._detail_area = ft.Container(
            content=self._detail_panel,
            expand=True,
            padding=ft.Padding.only(left=12, right=24, top=20, bottom=20),
            visible=False,
        )

        self.main_area = ft.Container(
            content=ft.Row(
                controls=[self._task_area, self._detail_divider, self._detail_area],
                expand=True,
                spacing=0,
            ),
            expand=True,
        )

        self.content = ft.Row(
            controls=[
                self.sidebar,
                self._sidebar_divider,
                self.main_area,
            ],
            expand=True,
            spacing=0,
        )

    # ── 主题切换 ──

    def _get_theme_color(self, key: str, default: str) -> str:
        """获取当前主题颜色"""
        return self.theme_manager.current.get(key, default)

    def _toggle_theme(self, e=None):
        """切换亮色/暗色主题"""
        new_theme = self.theme_manager.toggle()
        is_dark = self.theme_manager.is_dark
        self._theme_toggle_btn.icon = ft.Icons.LIGHT_MODE if is_dark else ft.Icons.DARK_MODE
        self._theme_toggle_btn.tooltip = "切换亮色主题" if is_dark else "切换暗色主题"
        self._update_ui_colors(new_theme)

    def _update_ui_colors(self, theme: dict):
        """更新所有 UI 元素的颜色"""
        # 更新自身背景
        self.bgcolor = theme["BG"]

        # 更新任务区域背景
        self._task_area.bgcolor = theme["BG"]

        # 更新卡片背景
        self._detail_panel.bgcolor = theme["CARD_BG"]

        # 更新分割线
        divider_color = theme["DIVIDER"]
        self._header_divider.color = divider_color
        self._sidebar_divider.color = divider_color
        self._detail_divider.color = divider_color

        # 更新主题切换按钮图标颜色
        self._theme_toggle_btn.icon_color = theme["TEXT_SECONDARY"]

        # 更新任务卡片
        for card in self._task_card_controls:
            card.update_theme(theme)

        # 更新日历视图
        self._calendar_view.update_theme(theme)

        # 更新侧边栏
        self.sidebar.update_theme(theme)

        # 更新顶部标题栏文本颜色
        self._update_header_colors(theme)

        # 更新添加任务栏
        self._update_add_bar_colors(theme)

        # 更新日历分区
        self._update_calendar_section_colors(theme)

        # 如果详情面板打开，重建以应用新主题色
        if self._detail_panel.visible and self._detail_data is not None:
            self._show_detail_panel(self._detail_data)

        self._page.update()

    def _update_header_colors(self, theme: dict):
        """更新顶部标题栏文本颜色"""
        task_area_col = self._task_area.content
        if task_area_col and task_area_col.controls:
            header = task_area_col.controls[0]  # build_header 返回的 Container
            if header and header.content:
                header_row = header.content
                if header_row.controls:
                    left_col = header_row.controls[0]
                    if isinstance(left_col, ft.Column) and left_col.controls:
                        left_col.controls[0].color = theme["TEXT_PRIMARY"]  # title
                        left_col.controls[1].color = theme["TEXT_SECONDARY"]  # date
                    right_row = header_row.controls[1]
                    if isinstance(right_row, ft.Row) and right_row.controls:
                        for btn in right_row.controls:
                            if isinstance(btn, ft.IconButton):
                                btn.icon_color = theme["TEXT_SECONDARY"]

    def _update_add_bar_colors(self, theme: dict):
        """更新底部添加任务栏颜色"""
        task_area_col = self._task_area.content
        if task_area_col and task_area_col.controls:
            add_bar = task_area_col.controls[-1]  # build_add_bar 返回的 Container
            if add_bar and add_bar.content:
                add_row = add_bar.content
                if add_row.controls:
                    tf = add_row.controls[0]
                    if isinstance(tf, ft.TextField):
                        tf.fill_color = theme["INPUT_BG"]
                        tf.border_color = theme["INPUT_BORDER"]
                        tf.hint_style = ft.TextStyle(color=theme["TEXT_SECONDARY"], size=14)

    def _update_calendar_section_colors(self, theme: dict):
        """更新日历分区颜色"""
        # 更新日历任务列表标题
        if self._calendar_section.controls:
            for ctrl in self._calendar_section.controls:
                if isinstance(ctrl, ft.Divider):
                    ctrl.color = theme["DIVIDER"]
                elif isinstance(ctrl, ft.Container) and ctrl.content:
                    if isinstance(ctrl.content, ft.Row):
                        for child in ctrl.content.controls:
                            if isinstance(child, ft.Text) and child.size == 13:
                                child.color = theme["TEXT_SECONDARY"]
                            elif isinstance(child, ft.TextButton):
                                child.style = ft.ButtonStyle(color=theme["TEXT_SECONDARY"])

    # ── 假数据加载 ──

    def _load_tasks(self, tag_filter: str = None):
        """从 TaskManager 读取任务并填充 UI，可按 tag 筛选"""
        # 如果正在日历模式，刷新日历任务列表
        if self._is_calendar_mode and self._calendar_date_filter:
            self._calendar_view.update_task_counts(self.task_manager.get_task_count_by_date())
            self._on_calendar_date_select(self._calendar_date_filter)
            return

        self._task_scroll.controls.clear()
        self._task_card_controls.clear()
        # 获取任务列表（Task 实例）
        active = self.task_manager.get_active_tasks(tag_filter)
        completed = self.task_manager.get_completed_tasks(tag_filter)
        # 渲染进行中任务
        for task in active:
            card = self._build_card(task.to_dict())
            self._task_scroll.controls.append(card)
            self._task_card_controls.append(card)
        # 渲染已完成任务并插入分隔线
        if completed:
            self._task_scroll.controls.append(
                ft.Container(
                    content=ft.Row(
                        controls=[
                            ft.Container(height=1, bgcolor=self._get_theme_color("DIVIDER", "#E0E0E0"), expand=True),
                            ft.Text(" 已完成 ", size=11, color=self._get_theme_color("TEXT_SECONDARY", TEXT_SECONDARY)),
                            ft.Container(height=1, bgcolor=self._get_theme_color("DIVIDER", "#E0E0E0"), expand=True),
                            ],
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    margin=ft.Margin.symmetric(vertical=12),
                )
            )
            for task in completed:
                card = self._build_card(task.to_dict())
                self._task_scroll.controls.append(card)
                self._task_card_controls.append(card)
        # 刷新页面显示（先注册控件，再应用主题）
        self._page.update()
        if self.theme_manager.is_dark:
            theme = self.theme_manager.current
            for card in self._task_card_controls:
                card.update_theme(theme)
            self._page.update()

    def _build_card(self, task_data: dict) -> TaskCard:
        return TaskCard(
            task_data=task_data,
            page=self._page,
            on_toggle=self._on_card_toggle,
            on_delete=self._on_card_delete,
            on_title_edit=self._on_card_title_edit,
            on_step_toggle=self._on_step_toggle,
            on_step_add=self._on_step_add,
            on_step_edit=self._on_step_edit,
            on_step_delete=self._on_step_delete,
            on_show_detail=self._on_card_show_detail,
            on_star=self._on_card_star,
            on_tag=self._on_card_tag,
        )

    # ── 卡片行内事件回调 ──

    def _on_card_toggle(self, task_data):
        self.task_manager.toggle_task_complete(task_data['id'])
        self._load_tasks(self._current_tag_filter)

    def _on_card_delete(self, task_data):
        self.task_manager.delete_task(task_data['id'])
        self._load_tasks(self._current_tag_filter)

    def _on_card_title_edit(self, task_data, new_title):
        self.task_manager.update_task_title(task_data['id'], new_title)
        self._load_tasks(self._current_tag_filter)

    def _on_step_toggle(self, task_data, step_data):
        self.task_manager.toggle_step_complete(task_data['id'], step_data['id'])
        self._load_tasks(self._current_tag_filter)

    def _on_step_add(self, task_data, desc):
        self.task_manager.add_step(task_data['id'], desc)
        self._load_tasks(self._current_tag_filter)

    def _on_step_edit(self, task_data, step_data):
        self.task_manager.update_step_description(task_data['id'], step_data['id'], step_data.get('description', ''))
        self._load_tasks(self._current_tag_filter)

    def _on_card_star(self, task_data):
        """标星切换：设置/取消高优先级"""
        new_priority = "" if task_data.get('priority') in ('高', 'high') else "高"
        self.task_manager.update_task_priority(task_data['id'], new_priority)
        self._load_tasks(self._current_tag_filter)

    def _on_card_tag(self, task_data, tag: str):
        """分类切换：设置/清除 tag"""
        self.task_manager.update_task_tag(task_data['id'], tag)
        self._load_tasks(self._current_tag_filter)

    def _on_step_delete(self, task_data, step_data):
        print(f"[delete_step] task={task_data['id']}, step={step_data['id']}")

    # ── 右侧详情面板 ──

    def _on_card_show_detail(self, task_data: dict):
        """点击任务标题：切换右侧详情面板"""
        task_id = task_data['id']
        if self._detail_task_id == task_id:
            # 同一任务 → 关闭面板
            self._save_detail()
            self._load_tasks(self._current_tag_filter)
            self._hide_detail_panel()
        else:
            # 不同任务 → 保存前一个 + 显示新任务
            if self._detail_task_id is not None:
                self._save_detail()
                self._load_tasks(self._current_tag_filter)
            self._show_detail_panel(task_data)

    def _show_detail_panel(self, task_data: dict):
        """显示右侧详情面板：统一 70px 标签列网格，标题/步骤/提醒/新增/保存等宽对齐"""
        self._detail_task_id = task_data['id']
        self._detail_data = task_data.copy()

        # 统一行容器：左16右16内边距，内容区起始位置统一
        def row_container(content, expand=False):
            return ft.Container(
                content=content,
                padding=ft.Padding.only(left=16, right=16),
                expand=expand,
            )

        # 标签列固定宽度
        LABEL_W = 70

        # ── 标题行：70px标签列 + 完成圈 + 标题输入框 + 菜单占位 ──
        completed = self._detail_data.get('completed', False)
        self._detail_title_chk = ft.Text(
            "●" if completed else "○", size=16, width=22,
            color=self._get_theme_color("TEXT_DISABLED", "#ADB5BD") if completed else self._get_theme_color("TEXT_PRIMARY", TEXT_PRIMARY),
        )
        self._detail_title_field = ft.TextField(
            value=self._detail_data.get('title', ''),
            hint_text="任务标题",
            hint_style=ft.TextStyle(color=self._get_theme_color("TEXT_SECONDARY", TEXT_SECONDARY)),
            color=self._get_theme_color("TEXT_PRIMARY", TEXT_PRIMARY),
            border=ft.InputBorder.NONE,
            text_size=16,
            dense=True,
            expand=True,
            bgcolor="transparent",
        )
        title_row = ft.Row([
                ft.Text("", width=LABEL_W),
                ft.Container(content=self._detail_title_chk, on_click=lambda e: self._on_detail_toggle_title()),
                self._detail_title_field,
            ], spacing=8, vertical_alignment=ft.CrossAxisAlignment.CENTER)

        # ── 步骤列表容器（标题行作为第一个元素，确保对齐）──
        self._detail_steps_col = ft.Column(
            controls=[title_row],
            spacing=4,
            scroll=ft.ScrollMode.AUTO,
            expand=True,
        )

        # 步骤数据（步骤之间插入细分割线）
        self._detail_step_fields = []
        steps = self._detail_data.get('steps', [])
        for i, step in enumerate(steps):
            if i > 0:
                self._detail_steps_col.controls.append(
                    ft.Divider(height=1, color=self._get_theme_color("STEP_DIVIDER", "#F0F0F0"))
                )
            self._build_step_row(step)

        # ── 添加步骤输入框（放在步骤列表末尾）──
        self._detail_add_step_field = ft.TextField(
            hint_text="添加步骤...",
            hint_style=ft.TextStyle(color=self._get_theme_color("ADD_STEP_HINT", "#4DABF7"), size=13),
            on_submit=self._on_detail_add_step,
            border=ft.InputBorder.NONE,
            color=self._get_theme_color("ADD_STEP_TEXT", "#4DABF7"),
            dense=True,
            expand=True,
        )
        self._detail_add_step_row = ft.Row(
            controls=[
                ft.Text("", width=LABEL_W),
                self._detail_add_step_field,
            ],
            spacing=8,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )
        # 步骤多于 0 条时加分割线
        if len(steps) > 0:
            self._detail_steps_col.controls.append(
                ft.Divider(height=1, color=self._get_theme_color("STEP_DIVIDER", "#F0F0F0"))
            )
        self._detail_steps_col.controls.append(self._detail_add_step_row)

        # 步骤列表整体用 row_container 包裹（标题行已在列内首个元素）
        steps_section = row_container(self._detail_steps_col, expand=True)

        # ── 提醒设置区（按钮触发弹窗）──
        has_reminder = bool(self._detail_data.get('reminder_date', ''))
        self._reminder_display_date = self._detail_data.get('reminder_date', '')
        self._reminder_display_time = self._detail_data.get('reminder_time', '')
        self._reminder_display_advance = self._detail_data.get('reminder_advance', 0)
        self._reminder_display_freq = self._detail_data.get('reminder_frequency', 'once')

        # 状态文字
        self._reminder_status_text = ft.Text("", size=12, color=self._get_theme_color("SUCCESS", "#4CAF50"))
        self._reminder_status_row = ft.Row([
            ft.Text("", width=LABEL_W),
            self._reminder_status_text,
        ], spacing=8)

        if has_reminder:
            freq_label = {"once": "单次", "daily": "每天", "weekly": "每周", "monthly": "每月"}
            freq_text = freq_label.get(self._reminder_display_freq, "单次")
            advance_text = "提前5分钟" if self._reminder_display_advance == 5 else "准时"
            reminder_info = ft.Text(
                f"🔔 {self._reminder_display_date} {self._reminder_display_time} · {advance_text} · {freq_text}",
                size=13, color=self._get_theme_color("TEXT_PRIMARY", TEXT_PRIMARY),
            )
            reminder_action_row = ft.Row([
                ft.Text("", width=LABEL_W),
                ft.TextButton(
                    "编辑提醒", icon=ft.Icons.EDIT,
                    on_click=lambda e: self._show_reminder_dialog(),
                    style=ft.ButtonStyle(color=PRIMARY),
                ),
                ft.TextButton(
                    "删除提醒", icon=ft.Icons.DELETE,
                    on_click=lambda e: self._delete_reminder(),
                    style=ft.ButtonStyle(color=self._get_theme_color("DANGER", "#E4405F")),
                ),
            ], spacing=8)
            reminder_row = row_container(
                ft.Column([
                    ft.Row([
                        ft.Text("🔔 提醒我", size=13, weight=ft.FontWeight.BOLD, color=self._get_theme_color("TEXT_SECONDARY", TEXT_SECONDARY), width=LABEL_W),
                        reminder_info,
                    ], spacing=8, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                    reminder_action_row,
                    self._reminder_status_row,
                ], spacing=6),
            )
        else:
            reminder_row = row_container(
                ft.Column([
                    ft.Row([
                        ft.Text("🔔 提醒我", size=13, weight=ft.FontWeight.BOLD, color=self._get_theme_color("TEXT_SECONDARY", TEXT_SECONDARY), width=LABEL_W),
                        ft.TextButton(
                            "设置提醒", icon=ft.Icons.ADD_ALERT,
                            on_click=lambda e: self._show_reminder_dialog(),
                            style=ft.ButtonStyle(color=PRIMARY),
                        ),
                    ], spacing=8, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                    self._reminder_status_row,
                ], spacing=6),
            )

        # ── 面板主体：标题/步骤/提醒 统一网格对齐 ──
        panel_content = ft.Column(
            controls=[
                steps_section,
                ft.Divider(height=1, color=self._get_theme_color("DIVIDER", "#E0E0E0")),
                reminder_row,
            ],
            spacing=6,
            expand=True,
        )

        self._detail_panel.content = panel_content
        self._detail_panel.visible = True
        self._detail_area.visible = True
        self._detail_divider.visible = True
        self._task_area.expand = 1
        self._page.update()

    def _build_step_row(self, step: dict):
        """构建单条步骤行：70px 标签列 + ○/●勾选圈 + 编辑框 + ⋯菜单"""
        LABEL_W = 70
        sid = step['id']
        completed = step.get('completed', False)

        # 勾选圈
        chk = ft.Text("●" if completed else "○", size=16, width=22,
                      color=self._get_theme_color("TEXT_DISABLED", "#ADB5BD") if completed else self._get_theme_color("TEXT_PRIMARY", TEXT_PRIMARY))

        # 编辑框：已完成 → 灰色 + 删除线；未完成 → 正常
        tf_style = ft.TextStyle(
            color=self._get_theme_color("TEXT_DISABLED", "#ADB5BD") if completed else self._get_theme_color("TEXT_PRIMARY", TEXT_PRIMARY),
            decoration=ft.TextDecoration.LINE_THROUGH if completed else ft.TextDecoration.NONE,
        )
        tf = ft.TextField(
            value=step.get('description', ''),
            hint_text="步骤",
            expand=True,
            text_style=tf_style,
            color=self._get_theme_color("TEXT_DISABLED", "#ADB5BD") if completed else self._get_theme_color("TEXT_PRIMARY", TEXT_PRIMARY),
            border=ft.InputBorder.NONE,
            dense=True,
        )

        # ⋯ 菜单按钮
        menu_btn = ft.PopupMenuButton(
            items=[
                ft.PopupMenuItem(
                    content=ft.Text("标记为未完成" if completed else "标记为已完成"),
                    on_click=lambda e, sid=sid: self._on_detail_toggle_step(sid),
                ),
                ft.PopupMenuItem(
                    content=ft.Text("删除步骤"),
                    on_click=lambda e, sid=sid: self._on_detail_delete_step(sid),
                ),
            ],
        )

        row = ft.Row(
            controls=[
                ft.Text("", width=70),  # 标签列占位，与标题/提醒区对齐
                ft.Container(content=chk, on_click=lambda e, sid=sid: self._on_detail_toggle_step(sid)),
                tf,
                menu_btn,
            ],
            spacing=8,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )

        self._detail_step_fields.append({'chk': chk, 'tf': tf, 'step': step, 'row': row})
        self._detail_steps_col.controls.append(row)

    def _on_detail_toggle_title(self):
        """切换任务标题的完成状态（同步更新标题圈 + 标题样式 + 持久化）"""
        completed = not self._detail_data.get('completed', False)
        self._detail_data['completed'] = completed
        self._detail_title_chk.value = "●" if completed else "○"
        self._detail_title_chk.color = self._get_theme_color("TEXT_DISABLED", "#ADB5BD") if completed else self._get_theme_color("TEXT_PRIMARY", TEXT_PRIMARY)
        self._detail_title_field.color = self._get_theme_color("TEXT_DISABLED", "#ADB5BD") if completed else self._get_theme_color("TEXT_PRIMARY", TEXT_PRIMARY)
        self.task_manager.toggle_task_complete(self._detail_data['id'])
        self._load_tasks(self._current_tag_filter)
        self._detail_panel.update()

    def _on_detail_toggle_step(self, step_id: str):
        """切换步骤完成状态（同步更新勾选圈 + 删除线 + 颜色）"""
        for item in self._detail_step_fields:
            if item['step']['id'] == step_id:
                completed = not item['step']['completed']
                item['step']['completed'] = completed
                # 勾选圈
                item['chk'].value = "●" if completed else "○"
                item['chk'].color = self._get_theme_color("TEXT_DISABLED", "#ADB5BD") if completed else self._get_theme_color("TEXT_PRIMARY", TEXT_PRIMARY)
                # 编辑框：文字样式
                item['tf'].text_style = ft.TextStyle(
                    color=self._get_theme_color("TEXT_DISABLED", "#ADB5BD") if completed else self._get_theme_color("TEXT_PRIMARY", TEXT_PRIMARY),
                    decoration=ft.TextDecoration.LINE_THROUGH if completed else ft.TextDecoration.NONE,
                )
                item['tf'].color = self._get_theme_color("TEXT_DISABLED", "#ADB5BD") if completed else self._get_theme_color("TEXT_PRIMARY", TEXT_PRIMARY)
                # 更新菜单文字
                menu_btn = item['row'].controls[-1]
                menu_btn.items[0].content.value = "标记为未完成" if completed else "标记为已完成"
                break
        self._detail_panel.update()

    def _on_detail_delete_step(self, step_id: str):
        """详情面板中删除步骤"""
        # 从数据中移除
        self._detail_data['steps'] = [
            s for s in self._detail_data['steps'] if s['id'] != step_id
        ]
        # 从 UI 中移除
        self._detail_step_fields = [
            item for item in self._detail_step_fields if item['step']['id'] != step_id
        ]
        self._rebuild_detail_steps_controls()
        self._detail_panel.update()

    def _rebuild_detail_steps_controls(self):
        """重建步骤列表控件，保留标题行(索引0)，在步骤行之间插入分割线，末尾保留添加输入框"""
        controls = [self._detail_steps_col.controls[0]]  # 保留标题行
        for i, item in enumerate(self._detail_step_fields):
            if i > 0:
                controls.append(ft.Divider(height=1, color=self._get_theme_color("STEP_DIVIDER", "#F0F0F0")))
            controls.append(item['row'])
        # 末尾保留添加步骤输入框
        if len(controls) > 0:
            controls.append(ft.Divider(height=1, color=self._get_theme_color("STEP_DIVIDER", "#F0F0F0")))
        if hasattr(self, '_detail_add_step_row') and self._detail_add_step_row is not None:
            controls.append(self._detail_add_step_row)
        self._detail_steps_col.controls = controls

    def _hide_detail_panel(self):
        """隐藏右侧详情面板（不重载，由调用方决定）"""
        self._detail_task_id = None
        self._detail_data = None
        self._detail_panel.visible = False
        self._detail_area.visible = False
        self._detail_divider.visible = False
        self._task_area.expand = True
        self._page.update()

    def _on_detail_add_step(self, e):
        """在详情面板中添加步骤（插入到添加输入框之前）"""
        desc = e.control.value.strip()
        if not desc:
            return
        import time
        new_step = {'id': str(int(time.time() * 1000)), 'description': desc, 'completed': False}
        if 'steps' not in self._detail_data:
            self._detail_data['steps'] = []
        self._detail_data['steps'].append(new_step)
        # 在添加输入框之前插入分割线 + 新步骤行
        idx = len(self._detail_steps_col.controls) - 1  # 添加输入框位置
        if len(self._detail_step_fields) > 0:
            self._detail_steps_col.controls.insert(idx, ft.Divider(height=1, color=self._get_theme_color("STEP_DIVIDER", "#F0F0F0")))
            idx += 1
        self._build_step_row(new_step)
        # 把新步骤行移动到添加输入框之前
        new_row = self._detail_steps_col.controls.pop()
        self._detail_steps_col.controls.insert(idx, new_row)
        e.control.value = ""
        self._detail_panel.update()

    def _save_detail(self):
        """读取面板字段，持久化"""
        if self._detail_data is None:
            return
        self._detail_data['title'] = self._detail_title_field.value.strip()
        for item in self._detail_step_fields:
            item['step']['description'] = item['tf'].value.strip()
        # 提醒字段已在弹窗中保存，此处不再处理
        self.task_manager.update_task(self._detail_data)

    def _start_notification_checker(self):
        """主线程轮询提醒队列，发现到期提醒时弹出 AlertDialog"""
        import asyncio
        from reminder_service import get_pending_notifications

        async def _check():
            while True:
                try:
                    items = get_pending_notifications()
                    for item in items:
                        self._show_notification_dialog(item["title"], item["message"])
                except Exception:
                    pass
                await asyncio.sleep(1)

        self._page.run_task(_check)

    def _show_notification_dialog(self, title: str, message: str):
        """弹出通知：Windows 系统托盘气泡（右下角，窗口最小化也能看到）"""
        # 后台线程发通知，不阻塞 UI
        import threading
        threading.Thread(target=self._send_windows_toast,
                         args=(title, message), daemon=True).start()

    def _send_windows_toast(self, title: str, message: str):
        """后台线程发送 Windows 系统托盘通知（右下角弹出，零依赖）"""
        try:
            import subprocess
            import base64

            safe_title = title.replace("'", "''")
            safe_msg = message.replace("'", "''")

            # 直接调 PowerShell 弹出系统托盘气泡（NotifyIcon）
            ps_code = f'''
Add-Type -AssemblyName System.Windows.Forms
$notify = New-Object System.Windows.Forms.NotifyIcon
$notify.Icon = [System.Drawing.SystemIcons]::Information
$notify.BalloonTipTitle = '{safe_title}'
$notify.BalloonTipText = '{safe_msg}'
$notify.Visible = $true
$notify.ShowBalloonTip(5000)
Start-Sleep -Seconds 5
$notify.Visible = $false
$notify.Dispose()
'''

            encoded = base64.b64encode(ps_code.encode('utf-16le')).decode('ascii')
            r = subprocess.run(
                ["powershell", "-NoProfile", "-EncodedCommand", encoded],
                capture_output=True, timeout=15,
            )
            if r.returncode == 0:
                print(f"[Toast] ✅ 系统托盘通知已发送: {title}")
            else:
                err = r.stderr.decode('utf-8', errors='replace')[:200]
                print(f"[Toast] ⚠ PowerShell 返回 {r.returncode}: {err}")
        except Exception as ex:
            print(f"[Toast] ❌ 发送失败: {ex}")

    # ── 提醒设置弹窗 ──

    def _show_reminder_dialog(self):
        """一级弹窗：日历选择 + 时间修改 + 提前提醒 + 频率"""
        print("[ReminderDialog] _show_reminder_dialog called (new overlay version)")
        self._do_show_reminder_dialog()

    def _do_show_reminder_dialog(self):
        page = self._page
        print("[ReminderDialog] _do_show_reminder_dialog")
        try:
            rd = self._detail_data.get('reminder_date', '') if self._detail_data else ''
            rt = self._detail_data.get('reminder_time', '') if self._detail_data else ''
            advance = self._detail_data.get('reminder_advance', 0) if self._detail_data else 0
            freq = self._detail_data.get('reminder_frequency', 'once') if self._detail_data else 'once'

            dlg_state = {
                'date': rd or datetime.now().strftime('%Y-%m-%d'),
                'time': rt or '09:00',
                'advance': str(advance),
                'freq': freq,
            }

            date_text = ft.Text(dlg_state['date'], size=16, weight=ft.FontWeight.BOLD, color=PRIMARY)
            time_text = ft.Text(dlg_state['time'], size=24, weight=ft.FontWeight.BOLD, color=TEXT_PRIMARY)

            overlay = [None]  # 用 list 引用

            def close_dlg(e=None):
                if overlay[0] and overlay[0] in page.overlay:
                    page.overlay.remove(overlay[0])
                overlay[0] = None
                page.update()

            def on_date_picked(e):
                if e.control.value:
                    d = e.control.value
                    import datetime as _dt
                    if isinstance(d, _dt.datetime):
                        local_tz = _dt.datetime.now().astimezone().tzinfo
                        if d.tzinfo is not None:
                            d = d.astimezone(local_tz)
                        d = d.date()
                    dlg_state['date'] = d.strftime('%Y-%m-%d')
                    date_text.value = dlg_state['date']
                    date_text.update()

            def pick_date(e):
                dp = ft.DatePicker(
                    first_date=datetime.now().date(),
                    last_date=datetime(2030, 12, 31).date(),
                    on_change=on_date_picked,
                )
                page.overlay.append(dp)
                dp.open = True
                page.update()

            def pick_time(e):
                # 通过 run_task 异步打开子弹窗，确保当前事件先处理完
                async def _open():
                    self._show_time_picker_dialog(dlg_state, time_text, close_dlg)
                page.run_task(_open)

            def on_save(e):
                self._detail_data['reminder_date'] = dlg_state['date']
                self._detail_data['reminder_time'] = dlg_state['time']
                self._detail_data['reminder_advance'] = int(dlg_state['advance'])
                self._detail_data['reminder_frequency'] = dlg_state['freq']
                self.task_manager.update_task(self._detail_data)
                close_dlg()
                self._load_tasks(self._current_tag_filter)
                self._show_detail_panel(self._detail_data)
                freq_label = {"once": "单次", "daily": "每天", "weekly": "每周", "monthly": "每月"}
                freq_text = freq_label.get(dlg_state['freq'], "单次")
                self._reminder_status_text.value = (
                    f"✅ 已添加提醒 日期 {dlg_state['date']} "
                    f"时间 {dlg_state['time']}，频率 {freq_text}"
                )
                self._reminder_status_text.color = self._get_theme_color("SUCCESS", "#4CAF50")
                self._reminder_status_row.update()

            advance_radio = ft.RadioGroup(
                value=dlg_state['advance'],
                content=ft.Row([
                    ft.Radio(value="0", label="准时提醒"),
                    ft.Radio(value="5", label="提前5分钟"),
                ], spacing=16),
            )
            advance_radio.on_change = lambda e: dlg_state.update({'advance': e.control.value})

            freq_radio = ft.RadioGroup(
                value=dlg_state['freq'],
                content=ft.Row([
                    ft.Radio(value="once", label="单次"),
                    ft.Radio(value="daily", label="每天"),
                    ft.Radio(value="weekly", label="每周"),
                    ft.Radio(value="monthly", label="每月"),
                ], spacing=12, wrap=True),
            )
            freq_radio.on_change = lambda e: dlg_state.update({'freq': e.control.value})

            # 自定义遮罩弹窗（不用 AlertDialog，用 overlay Container）
            overlay_container = ft.Container(
                content=ft.Container(
                    content=ft.Column([
                        ft.Row([
                            ft.Text("⏰ 设置提醒", size=18, weight=ft.FontWeight.BOLD),
                        ]),
                        ft.Divider(height=1, color=self._get_theme_color("DIVIDER", "#E0E0E0")),
                        ft.Text("日期", size=12, color=self._get_theme_color("TEXT_SECONDARY", TEXT_SECONDARY)),
                        ft.Container(
                            content=ft.Row([
                                ft.Icon(ft.Icons.CALENDAR_MONTH, color=PRIMARY, size=18),
                                date_text,
                                ft.Text("点击修改 →", size=11, color=self._get_theme_color("TEXT_SECONDARY", TEXT_SECONDARY)),
                            ], spacing=8),
                            on_click=pick_date,
                            padding=ft.Padding.symmetric(vertical=12, horizontal=12),
                            border_radius=ft.BorderRadius.all(8),
                            bgcolor=self._get_theme_color("BG", "#F5F5F5"),
                        ),
                        ft.Divider(height=1, color=self._get_theme_color("DIVIDER", "#E0E0E0")),
                        ft.Text("时间", size=12, color=self._get_theme_color("TEXT_SECONDARY", TEXT_SECONDARY)),
                        ft.Container(
                            content=ft.Row([
                                ft.Icon(ft.Icons.ACCESS_TIME, color=PRIMARY, size=18),
                                time_text,
                                ft.Text("点击修改 →", size=11, color=self._get_theme_color("TEXT_SECONDARY", TEXT_SECONDARY)),
                            ], spacing=8),
                            on_click=pick_time,
                            padding=ft.Padding.only(left=12, top=12, right=12, bottom=12),
                            border_radius=ft.BorderRadius.all(8),
                            bgcolor=self._get_theme_color("BG", "#F5F5F5"),
                        ),
                        ft.Divider(height=1, color=self._get_theme_color("DIVIDER", "#E0E0E0")),
                        ft.Text("提前提醒", size=12, color=self._get_theme_color("TEXT_SECONDARY", TEXT_SECONDARY)),
                        advance_radio,
                        ft.Divider(height=1, color=self._get_theme_color("DIVIDER", "#E0E0E0")),
                        ft.Text("重复频率", size=12, color=self._get_theme_color("TEXT_SECONDARY", TEXT_SECONDARY)),
                        freq_radio,
                        ft.Divider(height=1, color=self._get_theme_color("DIVIDER", "#E0E0E0")),
                        ft.Row([
                            ft.TextButton("取消", on_click=lambda e: close_dlg()),
                            ft.TextButton("保存", on_click=on_save, style=ft.ButtonStyle(color=PRIMARY)),
                        ], alignment=ft.MainAxisAlignment.END, spacing=8),
                    ], spacing=8, scroll=ft.ScrollMode.AUTO),
                    bgcolor=self._get_theme_color("DIALOG_BG", ft.Colors.WHITE),
                    border_radius=ft.BorderRadius.all(12),
                    padding=20,
                    width=420,
                    shadow=ft.BoxShadow(blur_radius=20, color="#40000000", offset=ft.Offset(0, 8)),
                    on_click=lambda e: None,  # 阻止事件冒泡到外层遮罩
                ),
                bgcolor=self._get_theme_color("OVERLAY_BG", "#80000000"),  # 半透明遮罩
                alignment=ft.alignment.Alignment(0, 0),
                expand=True,
                on_click=lambda e: close_dlg(),  # 点击遮罩关闭
            )

            overlay[0] = overlay_container
            page.overlay.append(overlay_container)
            page.update()
            print("[ReminderDialog] 自定义遮罩弹窗已显示")
        except Exception as ex:
            import traceback
            traceback.print_exc()
            print(f"[ReminderDialog] ❌ 异常: {ex}")

    def _show_time_picker_dialog(self, dlg_state: dict, time_text: ft.Text, close_parent):
        """二级弹窗：选择时间（小时 + 分钟），用自定义 overlay"""
        page = self._page
        hour, minute = dlg_state['time'].split(':')
        hour = int(hour)
        minute = int(minute)

        hour_display = ft.Text(f"{hour:02d}", size=36, weight=ft.FontWeight.BOLD, color=TEXT_PRIMARY)
        minute_display = ft.Text(f"{minute:02d}", size=36, weight=ft.FontWeight.BOLD, color=TEXT_PRIMARY)

        overlay = [None]

        def close_sub(e=None):
            if overlay[0] and overlay[0] in page.overlay:
                page.overlay.remove(overlay[0])
            overlay[0] = None
            page.update()

        def confirm_time(e):
            nonlocal hour, minute
            dlg_state['time'] = f"{hour:02d}:{minute:02d}"
            time_text.value = dlg_state['time']
            time_text.update()
            close_sub()

        def inc_hour(e):
            nonlocal hour
            hour = (hour + 1) % 24
            hour_display.value = f"{hour:02d}"
            hour_display.update()

        def dec_hour(e):
            nonlocal hour
            hour = (hour - 1) % 24
            hour_display.value = f"{hour:02d}"
            hour_display.update()

        def inc_minute(e):
            nonlocal minute
            minute = (minute + 1) % 60
            minute_display.value = f"{minute:02d}"
            minute_display.update()

        def dec_minute(e):
            nonlocal minute
            minute = (minute - 1) % 60
            minute_display.value = f"{minute:02d}"
            minute_display.update()

        overlay_container = ft.Container(
            content=ft.Container(
                content=ft.Column([
                    ft.Text("选择时间", size=18, weight=ft.FontWeight.BOLD),
                    ft.Divider(height=1, color=self._get_theme_color("DIVIDER", "#E0E0E0")),
                    ft.Row([
                        ft.Column([
                            ft.IconButton(icon=ft.Icons.KEYBOARD_ARROW_UP, on_click=inc_hour, icon_color=PRIMARY),
                            hour_display,
                            ft.IconButton(icon=ft.Icons.KEYBOARD_ARROW_DOWN, on_click=dec_hour, icon_color=PRIMARY),
                        ], spacing=0, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                        ft.Text(":", size=28, weight=ft.FontWeight.BOLD, color=self._get_theme_color("TEXT_SECONDARY", TEXT_SECONDARY)),
                        ft.Column([
                            ft.IconButton(icon=ft.Icons.KEYBOARD_ARROW_UP, on_click=inc_minute, icon_color=PRIMARY),
                            minute_display,
                            ft.IconButton(icon=ft.Icons.KEYBOARD_ARROW_DOWN, on_click=dec_minute, icon_color=PRIMARY),
                        ], spacing=0, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    ], spacing=12, alignment=ft.MainAxisAlignment.CENTER),
                    ft.Divider(height=1, color=self._get_theme_color("DIVIDER", "#E0E0E0")),
                    ft.Row([
                        ft.TextButton("取消", on_click=lambda e: close_sub()),
                        ft.TextButton("确定", on_click=confirm_time, style=ft.ButtonStyle(color=PRIMARY)),
                    ], alignment=ft.MainAxisAlignment.END, spacing=8),
                ], spacing=12, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                bgcolor=self._get_theme_color("DIALOG_BG", ft.Colors.WHITE),
                border_radius=ft.BorderRadius.all(12),
                padding=20,
                width=300,
                shadow=ft.BoxShadow(blur_radius=20, color="#40000000", offset=ft.Offset(0, 8)),
                on_click=lambda e: None,  # 阻止事件冒泡到外层遮罩
            ),
            bgcolor=self._get_theme_color("OVERLAY_BG", "#80000000"),
            alignment=ft.alignment.Alignment(0, 0),
            expand=True,
            on_click=lambda e: close_sub(),  # 点击遮罩关闭
        )

        overlay[0] = overlay_container
        page.overlay.append(overlay_container)
        page.update()

    def _delete_reminder(self):
        """删除提醒：清空所有提醒字段并持久化"""
        if self._detail_data is None:
            return
        self._detail_data['reminder_date'] = ''
        self._detail_data['reminder_time'] = ''
        self._detail_data['reminder_advance'] = 0
        self._detail_data['reminder_frequency'] = 'once'
        self.task_manager.update_task(self._detail_data)
        self._load_tasks(self._current_tag_filter)
        self._show_detail_panel(self._detail_data)
        self._reminder_status_text.value = "🗑 已删除提醒"
        self._reminder_status_text.color = self._get_theme_color("TEXT_SECONDARY", TEXT_SECONDARY)
        self._reminder_status_row.update()

    def _on_navigate(self, key: str):
        """切换页面 / 筛选"""
        print(f"[navigate] -> {key}")
        if key == "calendar":
            self._show_calendar()
            return
        # 非日历页面 → 确保日历隐藏
        if self._is_calendar_mode:
            self._hide_calendar()
        if key == "today" or key == "all":
            self._current_tag_filter = None
        elif key.startswith("tag:"):
            self._current_tag_filter = key[4:]  # 去掉 "tag:"
        else:
            return
        self._load_tasks(self._current_tag_filter)

    def _show_calendar(self):
        """切换到日历视图"""
        self._is_calendar_mode = True
        self._calendar_date_filter = None
        # 更新日历任务计数
        self._calendar_view.update_task_counts(self.task_manager.get_task_count_by_date())
        # 切换可见性
        self._task_list_container.visible = False
        self._calendar_section.visible = True
        # 隐藏添加任务栏
        add_bar = self._task_area.content.controls[-1]
        add_bar.visible = False
        # 清空日历任务列表
        self._calendar_task_list.controls.clear()
        self._page.update()

    def _hide_calendar(self):
        """从日历视图切换回任务列表"""
        self._is_calendar_mode = False
        self._calendar_date_filter = None
        self._task_list_container.visible = True
        self._calendar_section.visible = False
        add_bar = self._task_area.content.controls[-1]
        add_bar.visible = True
        self._page.update()

    def _toggle_calendar(self):
        """顶部日历图标点击：切换日历/任务列表"""
        if self._is_calendar_mode:
            self._on_navigate("all")
        else:
            self._on_navigate("calendar")

    def _on_calendar_date_select(self, date_str: str):
        """日历日期点击回调：筛选该日期的任务"""
        self._calendar_date_filter = date_str
        tasks = self.task_manager.get_tasks_by_date(date_str)
        self._calendar_task_list.controls.clear()
        if tasks:
            for task in tasks:
                card = self._build_card(task.to_dict())
                self._calendar_task_list.controls.append(card)
        else:
            self._calendar_task_list.controls.append(
                ft.Container(
                    content=ft.Text("该日期暂无任务", size=13, color=self._get_theme_color("TEXT_SECONDARY", TEXT_SECONDARY)),
                    padding=ft.Padding.symmetric(vertical=16),
                )
            )
        self._page.update()

    def _on_add_task(self, title: str):
        """添加任务回调 – 带上当前 tag 筛选"""
        self.task_manager.add_task(title, tag=self._current_tag_filter or "")
        self._load_tasks(self._current_tag_filter)
