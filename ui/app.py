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

        # 详情面板状态
        self._detail_task_id = None
        self._detail_data = None
        self._detail_title_field = None
        self._detail_step_fields = []
        self._detail_steps_col = None

        # 构建任务列表容器（内部是一个 Column + ScrollView）
        self._task_scroll = ft.Column(spacing=0, scroll=ft.ScrollMode.AUTO, expand=True)
        self._task_list_container = ft.Container(
            content=self._task_scroll,
            expand=True,
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

        # 加载真实任务数据
        self._load_tasks()

        # 布局: Row(侧栏 | 任务列表 + 可能的分隔线 + 详情面板)
        self.sidebar = Sidebar(on_navigate=self._on_navigate)
        self._task_area = ft.Container(
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
        # 刷新页面显示
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
        )

    # ── 卡片行内事件回调 ──

    def _on_card_toggle(self, task_data):
        self.task_manager.toggle_task_complete(task_data['id'])
        self._load_tasks()

    def _on_card_delete(self, task_data):
        self.task_manager.delete_task(task_data['id'])
        self._load_tasks()

    def _on_card_title_edit(self, task_data, new_title):
        self.task_manager.update_task_title(task_data['id'], new_title)
        self._load_tasks()

    def _on_step_toggle(self, task_data, step_data):
        self.task_manager.toggle_step_complete(task_data['id'], step_data['id'])
        self._load_tasks()

    def _on_step_add(self, task_data, desc):
        self.task_manager.add_step(task_data['id'], desc)
        self._load_tasks()

    def _on_step_edit(self, task_data, step_data):
        self.task_manager.update_step_description(task_data['id'], step_data['id'], step_data.get('description', ''))
        self._load_tasks()

    def _on_card_star(self, task_data):
        """标星切换：设置/取消高优先级"""
        new_priority = "" if task_data.get('priority') in ('高', 'high') else "高"
        self.task_manager.update_task_priority(task_data['id'], new_priority)
        self._load_tasks()

    def _on_step_delete(self, task_data, step_data):
        print(f"[delete_step] task={task_data['id']}, step={step_data['id']}")

    # ── 右侧详情面板 ──

    def _on_card_show_detail(self, task_data: dict):
        """点击任务标题：切换右侧详情面板"""
        task_id = task_data['id']
        if self._detail_task_id == task_id:
            # 同一任务 → 关闭面板
            self._save_detail()
            self._load_tasks()
            self._hide_detail_panel()
        else:
            # 不同任务 → 保存前一个 + 显示新任务
            if self._detail_task_id is not None:
                self._save_detail()
                self._load_tasks()
            self._show_detail_panel(task_data)

    def _show_detail_panel(self, task_data: dict):
        """显示右侧详情面板"""
        self._detail_task_id = task_data['id']
        self._detail_data = task_data.copy()  # 复制一份，避免直接修改原数据

        # 标题编辑框
        self._detail_title_field = ft.TextField(
            value=self._detail_data.get('title', ''),
            hint_text="任务标题",
        )

        # 步骤容器
        self._detail_steps_col = ft.Column(
            controls=[],
            scroll=ft.ScrollMode.AUTO,
            expand=True,
        )

        # 步骤列表：每个步骤 = ○/● 勾选圈 + 编辑框 + 删除按钮
        # 存储结构：{'chk': Text, 'tf': TextField, 'step': step_dict, 'row': Row}
        self._detail_step_fields = []
        for step in self._detail_data.get('steps', []):
            self._build_step_row(step)

        # 添加步骤输入框
        self._detail_add_step_field = ft.TextField(
            hint_text="添加步骤...",
            on_submit=self._on_detail_add_step,
        )

        # 面板内容（无"标题""步骤"标签）
        panel_content = ft.Column(
            controls=[
                ft.Row(
                    controls=[
                        ft.Text("任务详情", size=18, weight=ft.FontWeight.BOLD),
                        ft.TextButton("✕", on_click=lambda e: self._on_detail_close()),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
                self._detail_title_field,
                self._detail_steps_col,
                self._detail_add_step_field,
            ],
            spacing=8,
            expand=True,
        )

        self._detail_panel.content = panel_content
        self._detail_panel.visible = True
        self._detail_area.visible = True
        self._detail_divider.visible = True
        self._task_area.expand = 1
        self._page.update()

    def _build_step_row(self, step: dict):
        """构建单条步骤行：○/● 勾选圈 + 编辑框（已完成=灰+删除线） + ⋯ 菜单"""
        sid = step['id']
        completed = step.get('completed', False)

        # 勾选圈
        chk = ft.Text("●" if completed else "○", size=16, width=22,
                      color="#ADB5BD" if completed else TEXT_PRIMARY)

        # 编辑框：已完成 → 灰色 + 删除线；未完成 → 正常
        tf_style = ft.TextStyle(
            color="#ADB5BD" if completed else TEXT_PRIMARY,
            decoration=ft.TextDecoration.LINE_THROUGH if completed else ft.TextDecoration.NONE,
        )
        tf = ft.TextField(
            value=step.get('description', ''),
            hint_text="步骤",
            expand=True,
            text_style=tf_style,
            color="#ADB5BD" if completed else TEXT_PRIMARY,
        )

        # ⋯ 菜单按钮（不占右侧空间，避免被滚动条遮挡）
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
                ft.Container(content=chk, on_click=lambda e, sid=sid: self._on_detail_toggle_step(sid)),
                tf,
                menu_btn,
            ],
            spacing=4,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )

        self._detail_step_fields.append({'chk': chk, 'tf': tf, 'step': step, 'row': row})
        self._detail_steps_col.controls.append(row)

    def _on_detail_toggle_step(self, step_id: str):
        """切换步骤完成状态（同步更新勾选圈 + 删除线 + 颜色）"""
        for item in self._detail_step_fields:
            if item['step']['id'] == step_id:
                completed = not item['step']['completed']
                item['step']['completed'] = completed
                # 勾选圈
                item['chk'].value = "●" if completed else "○"
                item['chk'].color = "#ADB5BD" if completed else TEXT_PRIMARY
                # 编辑框：文字样式
                item['tf'].text_style = ft.TextStyle(
                    color="#ADB5BD" if completed else TEXT_PRIMARY,
                    decoration=ft.TextDecoration.LINE_THROUGH if completed else ft.TextDecoration.NONE,
                )
                item['tf'].color = "#ADB5BD" if completed else TEXT_PRIMARY
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
        self._detail_steps_col.controls = [
            item['row'] for item in self._detail_step_fields
        ]
        self._detail_panel.update()

    def _hide_detail_panel(self):
        """隐藏右侧详情面板（不重载，由调用方决定）"""
        self._detail_task_id = None
        self._detail_data = None
        self._detail_panel.visible = False
        self._detail_area.visible = False
        self._detail_divider.visible = False
        self._task_area.expand = True
        self._page.update()

    def _on_detail_close(self):
        """点击 ✕ 关闭面板"""
        self._save_detail()
        self._load_tasks()
        self._hide_detail_panel()

    def _on_detail_add_step(self, e):
        """在详情面板中添加步骤（带勾选圈 + 删除按钮）"""
        desc = e.control.value.strip()
        if not desc:
            return
        import time
        new_step = {'id': str(int(time.time() * 1000)), 'description': desc, 'completed': False}
        if 'steps' not in self._detail_data:
            self._detail_data['steps'] = []
        self._detail_data['steps'].append(new_step)
        self._build_step_row(new_step)
        e.control.value = ""
        self._detail_panel.update()

    def _save_detail(self):
        """读取面板字段，持久化"""
        if self._detail_data is None:
            return
        self._detail_data['title'] = self._detail_title_field.value.strip()
        for item in self._detail_step_fields:
            item['step']['description'] = item['tf'].value.strip()
        self.task_manager.update_task(self._detail_data)

    def _on_navigate(self, key: str):
        """切换页面"""
        print(f"[navigate] -> {key}")
        # 后续实现: 根据 key 切换 content

    def _on_add_task(self, title: str):
        """添加任务回调 – Phase 4 实现任务新增"""
        # 直接使用 TaskManager 添加任务（默认无 tag、priority）
        self.task_manager.add_task(title)
        self._load_tasks()
