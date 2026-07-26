"""
主 App 页面 —— 侧栏 + 内容区布局骨架
Phase 2: 使用 TaskCard 组件展示任务列表（假数据）
"""

import flet as ft
from .theme import PRIMARY, BG, TEXT_PRIMARY, TEXT_SECONDARY, CARD_BG
from .sidebar import Sidebar
from .task_card import TaskCard
from datetime import datetime, timedelta


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

SAMPLE_TASKS = [
    {
        "id": "demo_1",
        "title": "学习 Python Flet 框架",
        "completed": False,
        "tag": "学习",
        "priority": "高",
        "created_at": (datetime.now() - timedelta(hours=2)).isoformat(),
        "steps": [
            {"id": "s1", "description": "理解 Flet 控件树结构", "completed": True},
            {"id": "s2", "description": "掌握 Container/Column/Row 布局", "completed": True},
            {"id": "s3", "description": "实现自定义组件 (TaskCard)", "completed": False},
            {"id": "s4", "description": "对接数据层 task_manager.py", "completed": False},
        ],
    },
    {
        "id": "demo_2",
        "title": "完成 AliveDaily Phase 2",
        "completed": False,
        "tag": "工作",
        "priority": "中",
        "created_at": datetime.now().isoformat(),
        "steps": [
            {"id": "s5", "description": "创建 task_card.py 组件", "completed": True},
            {"id": "s6", "description": "卡片交互事件绑定", "completed": False},
            {"id": "s7", "description": "编译验证", "completed": False},
        ],
    },
    {
        "id": "demo_3",
        "title": "超市采购清单",
        "completed": False,
        "tag": "生活",
        "priority": "低",
        "created_at": (datetime.now() - timedelta(days=1)).isoformat(),
        "steps": [
            {"id": "s8", "description": "鸡蛋、牛奶", "completed": False},
            {"id": "s9", "description": "蔬菜水果", "completed": False},
        ],
    },
    {
        "id": "demo_4",
        "title": "已完成的任务示例",
        "completed": True,
        "tag": "工作",
        "priority": "高",
        "created_at": (datetime.now() - timedelta(days=2)).isoformat(),
        "steps": [
            {"id": "s10", "description": "搭建 Python 环境", "completed": True},
            {"id": "s11", "description": "安装依赖包", "completed": True},
        ],
    },
]


class DeskApp(ft.Container):
    """主应用容器"""

    def __init__(self, page: ft.Page):
        super().__init__(expand=True, bgcolor=BG)
        self._page = page
        self._task_card_controls = []  # 所有 TaskCard 控件引用

        # 构建任务列表容器（内部是一个 Column + ScrollView）
        self._task_scroll = ft.Column(spacing=0, scroll=ft.ScrollMode.AUTO, expand=True)
        self._task_list_container = ft.Container(
            content=self._task_scroll,
            expand=True,
        )

        # 填入假数据
        self._load_sample_tasks()

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

    def _load_sample_tasks(self):
        """用 SAMPLE_TASKS 填充任务列表"""
        self._task_scroll.controls.clear()
        self._task_card_controls.clear()

        # 分离进行中和已完成
        active = [t for t in SAMPLE_TASKS if not t["completed"]]
        completed = [t for t in SAMPLE_TASKS if t["completed"]]

        for t in active:
            card = self._build_card(t)
            self._task_scroll.controls.append(card)
            self._task_card_controls.append(card)

        if completed:
            # 已完成区域分隔线
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
            for t in completed:
                card = self._build_card(t)
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
        print(f"[toggle_task] {task_data['id']}")

    def _on_card_delete(self, task_data):
        print(f"[delete_task] {task_data['id']}")

    def _on_card_title_edit(self, task_data, new_title):
        print(f"[edit_title] {task_data['id']} -> {new_title}")

    def _on_step_toggle(self, task_data, step_data):
        print(f"[toggle_step] task={task_data['id']}, step={step_data['id']}")

    def _on_step_add(self, task_data, desc):
        print(f"[add_step] task={task_data['id']}, desc={desc}")

    def _on_step_edit(self, task_data, step_data):
        print(f"[edit_step] task={task_data['id']}, step={step_data['id']}")

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
