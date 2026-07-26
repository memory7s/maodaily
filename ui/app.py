"""
主 App 页面 —— 侧栏 + 内容区布局骨架
Phase 2: 使用 TaskCard 组件展示任务列表（假数据）
"""

import flet as ft
from .theme import PRIMARY, BG, TEXT_PRIMARY, TEXT_SECONDARY, CARD_BG
from .sidebar import Sidebar
from .task_card import TaskCard
from datetime import datetime, timedelta
from task_manager import TaskManager


def build_header(on_calendar_toggle=None) -> ft.Container:
    """顶部标题栏"""
    now = datetime.now()
    weekday_cn = ["一", "二", "三", "四", "五", "六", "日"]
    date_str = f"{now.year}年{now.month}月{now.day}日 周{weekday_cn[now.weekday()]}"

    return ft.Container(
        content=ft.Row(
            controls=[
                ft.Column(
                    controls=[
                        ft.Text("今日计划", size=22, weight=ft.FontWeight.BOLD, color=TEXT_PRIMARY),
                        ft.Text(date_str, size=12, color=TEXT_SECONDARY),
                    ],
                    spacing=2,
                ),
                ft.Row(
                    controls=[
                        ft.IconButton(
                            icon=ft.Icons.CALENDAR_MONTH,
                            icon_color=TEXT_SECONDARY,
                            tooltip="日历",
                            on_click=on_calendar_toggle,
                        ),
                    ],
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

        # 构建任务列表容器（内部是一个 Column + ScrollView）
        self._task_scroll = ft.Column(spacing=0, scroll=ft.ScrollMode.AUTO, expand=True)
        self._task_list_container = ft.Container(
            content=self._task_scroll,
            expand=True,
        )

        # 加载真实任务数据
        self._load_tasks()

        # 布局: Row(侧栏 | 主区域)
        self.sidebar = Sidebar(on_navigate=self._on_navigate)
        self.main_area = ft.Container(
            content=ft.Column(
                controls=[
                    build_header(),
                    ft.Divider(height=1, color="#E0E0E0"),
                    self._task_list_container,
                    build_add_bar(self._on_add_task),
                ],
                expand=True,
            ),
            expand=True,
            padding=ft.Padding.only(left=24, right=24, top=20, bottom=20),
        )

        self.content = ft.Row(
            controls=[
                self.sidebar,
                ft.VerticalDivider(width=1, color="#E0E0E0"),
                self.main_area,
            ],
            expand=True,
            spacing=0,
        )

    # ── 假数据加载 ──

    def _load_tasks(self):
        """从 TaskManager 读取任务并填充 UI"""
        self._task_scroll.controls.clear()
        self._task_card_controls.clear()
        # 获取任务列表（Task 实例）
        active = self.task_manager.get_active_tasks()
        completed = self.task_manager.get_completed_tasks()
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
                            ft.Container(height=1, bgcolor="#E0E0E0", expand=True),
                            ft.Text(" 已完成 ", size=11, color=TEXT_SECONDARY),
                            ft.Container(height=1, bgcolor="#E0E0E0", expand=True),
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

    def _build_card(self, task_data: dict) -> TaskCard:
        return TaskCard(
            task_data=task_data,
            on_toggle=self._on_card_toggle,
            on_delete=self._on_card_delete,
            on_title_edit=self._on_card_title_edit,
            on_step_toggle=self._on_step_toggle,
            on_step_add=self._on_step_add,
            on_step_edit=self._on_step_edit,
            on_step_delete=self._on_step_delete,
        )

    # ── 事件回调（Phase 3 才真正操作数据，现在只打 log） ──

    def _on_card_toggle(self, task_data):
        # 切换任务完成状态
        self.task_manager.toggle_task_complete(task_data['id'])
        self._load_tasks()

    def _on_card_delete(self, task_data):
        # 删除任务
        self.task_manager.delete_task(task_data['id'])
        self._load_tasks()

    def _on_card_title_edit(self, task_data, new_title):
        # 更新任务标题
        self.task_manager.update_task_title(task_data['id'], new_title)
        self._load_tasks()

    def _on_step_toggle(self, task_data, step_data):
        # 切换步骤完成状态
        self.task_manager.toggle_step_complete(task_data['id'], step_data['id'])
        self._load_tasks()

    def _on_step_add(self, task_data, desc):
        # 添加步骤
        self.task_manager.add_step(task_data['id'], desc)
        self._load_tasks()

    def _on_step_edit(self, task_data, step_data):
        # 更新步骤描述
        # step_data 中已经包含最新的 description（通过 TaskCard 编辑后更新）
        self.task_manager.update_step_description(task_data['id'], step_data['id'], step_data.get('description', ''))
        self._load_tasks()

    def _on_step_delete(self, task_data, step_data):
        print(f"[delete_step] task={task_data['id']}, step={step_data['id']}")

    def _on_navigate(self, key: str):
        """切换页面"""
        print(f"[navigate] -> {key}")
        # 后续实现: 根据 key 切换 content

    def _on_add_task(self, title: str):
        """添加任务回调"""
        print(f"[add_task] {title}")
        # 后续 Phase 3 实现
