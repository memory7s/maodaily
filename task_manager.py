"""
任务数据管理模块
提供 Task、TaskStep 数据模型，以及 TaskManager 负责 JSON 持久化。
"""

import json
import os
from datetime import datetime
from typing import List, Optional

# 数据文件路径
DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
DATA_FILE = os.path.join(DATA_DIR, "tasks.json")


class TaskStep:
    """任务的单个步骤/子任务"""

    def __init__(self, description: str, completed: bool = False, step_id: str = None):
        self.id = step_id or datetime.now().strftime("%f")
        self.description = description
        self.completed = completed

    def to_dict(self) -> dict:
        return {"id": self.id, "description": self.description, "completed": self.completed}

    @classmethod
    def from_dict(cls, data: dict) -> "TaskStep":
        return cls(
            description=data["description"],
            completed=data.get("completed", False),
            step_id=data.get("id"),
        )


class Task:
    """一个完整的任务，包含标题和多个步骤"""

    def __init__(
        self,
        title: str,
        steps: List[TaskStep] = None,
        completed: bool = False,
        task_id: str = None,
        created_at: str = None,
        completed_at: str = None,
        tag: str = "",
        priority: str = "",
        reminder_date: str = "",
        reminder_time: str = "",
        reminder_advance: int = 0,
        reminder_frequency: str = "once",
    ):
        self.id = task_id or datetime.now().strftime("%Y%m%d%H%M%S%f")
        self.title = title
        self.steps = steps or []
        self.completed = completed
        self.created_at = created_at or datetime.now().isoformat()
        self.completed_at = completed_at
        self.tag = tag
        self.priority = priority
        self.reminder_date = reminder_date      # "YYYY-MM-DD"
        self.reminder_time = reminder_time      # "HH:MM"
        self.reminder_advance = reminder_advance # 0=准时, 5=提前5分
        self.reminder_frequency = reminder_frequency # "once"/"daily"/"weekly"/"monthly"

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "steps": [s.to_dict() for s in self.steps],
            "completed": self.completed,
            "created_at": self.created_at,
            "completed_at": self.completed_at,
            "tag": self.tag,
            "priority": self.priority,
            "reminder_date": self.reminder_date,
            "reminder_time": self.reminder_time,
            "reminder_advance": self.reminder_advance,
            "reminder_frequency": self.reminder_frequency,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Task":
        steps = [TaskStep.from_dict(s) for s in data.get("steps", [])]
        return cls(
            title=data["title"],
            steps=steps,
            completed=data.get("completed", False),
            task_id=data.get("id"),
            created_at=data.get("created_at"),
            completed_at=data.get("completed_at"),
            tag=data.get("tag", ""),
            priority=data.get("priority", ""),
            reminder_date=data.get("reminder_date", ""),
            reminder_time=data.get("reminder_time", ""),
            reminder_advance=data.get("reminder_advance", 0),
            reminder_frequency=data.get("reminder_frequency", "once"),
        )


class TaskManager:
    """管理任务的增删改查与 JSON 持久化"""

    def __init__(self):
        self.tasks: List[Task] = []
        self._ensure_data_dir()
        self.load()

    # ---------- 文件 IO ----------

    def _ensure_data_dir(self):
        os.makedirs(DATA_DIR, exist_ok=True)

    def load(self):
        """从 JSON 文件加载任务列表"""
        if not os.path.exists(DATA_FILE):
            self.tasks = []
            return
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                raw = json.load(f)
            self.tasks = [Task.from_dict(t) for t in raw.get("tasks", [])]
        except (json.JSONDecodeError, KeyError):
            self.tasks = []

    def save(self):
        """将任务列表写入 JSON 文件"""
        data = {"tasks": [t.to_dict() for t in self.tasks]}
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    # ---------- 任务 CRUD ----------

    def add_task(self, title: str, tag: str = "", priority: str = "") -> Task:
        task = Task(title=title.strip(), tag=tag, priority=priority)
        self.tasks.append(task)
        self.save()
        return task

    def delete_task(self, task_id: str):
        self.tasks = [t for t in self.tasks if t.id != task_id]
        self.save()

    def toggle_task_complete(self, task_id: str) -> bool:
        """切换任务的完成状态，返回新状态"""
        for task in self.tasks:
            if task.id == task_id:
                task.completed = not task.completed
                task.completed_at = datetime.now().isoformat() if task.completed else None
                self.save()
                return task.completed
        return False

    def update_task_title(self, task_id: str, new_title: str):
        for task in self.tasks:
            if task.id == task_id:
                task.title = new_title.strip()
                self.save()
                return

    def update_task_priority(self, task_id: str, priority: str):
        """设置任务优先级（空字符串 = 取消）"""
        for task in self.tasks:
            if task.id == task_id:
                task.priority = priority
                self.save()
                return

    def update_task_tag(self, task_id: str, tag: str):
        """设置任务分类"""
        for task in self.tasks:
            if task.id == task_id:
                task.tag = tag
                self.save()
                return

    # ---------- 步骤 CRUD ----------

    def add_step(self, task_id: str, description: str) -> Optional[TaskStep]:
        for task in self.tasks:
            if task.id == task_id:
                step = TaskStep(description=description.strip())
                task.steps.append(step)
                self.save()
                return step
        return None

    def delete_step(self, task_id: str, step_id: str):
        for task in self.tasks:
            if task.id == task_id:
                task.steps = [s for s in task.steps if s.id != step_id]
                self.save()
                return

    def update_step_description(self, task_id: str, step_id: str, new_description: str):
        for task in self.tasks:
            if task.id == task_id:
                for step in task.steps:
                    if step.id == step_id:
                        step.description = new_description.strip()
                        self.save()
                        return

    def toggle_step_complete(self, task_id: str, step_id: str) -> bool:
        for task in self.tasks:
            if task.id == task_id:
                for step in task.steps:
                    if step.id == step_id:
                        step.completed = not step.completed
                        self.save()
                        return step.completed
        return False

    def update_task(self, task_data: dict):
        """根据完整 dict 更新任务（标题 + 步骤 + 提醒 + 标签 + 优先级）"""
        for task in self.tasks:
            if task.id == task_data['id']:
                task.title = task_data.get('title', task.title)
                task.steps = [TaskStep.from_dict(s) for s in task_data.get('steps', [])]
                task.reminder_date = task_data.get('reminder_date', task.reminder_date)
                task.reminder_time = task_data.get('reminder_time', task.reminder_time)
                task.reminder_advance = task_data.get('reminder_advance', task.reminder_advance)
                task.reminder_frequency = task_data.get('reminder_frequency', task.reminder_frequency)
                task.tag = task_data.get('tag', task.tag)
                task.priority = task_data.get('priority', task.priority)
                self.save()
                return

# ---------- 查询 ---------- 查询 ----------
 
    def get_active_tasks(self, tag: str = None) -> List[Task]:
        tasks = [t for t in self.tasks if not t.completed]
        if tag is not None:
            tasks = [t for t in tasks if t.tag == tag]
        return tasks
 
    def get_completed_tasks(self, tag: str = None) -> List[Task]:
        tasks = [t for t in self.tasks if t.completed]
        if tag is not None:
            tasks = [t for t in tasks if t.tag == tag]
        return tasks
 
    def get_task_count_by_date(self) -> dict:
        """返回 {YYYY-MM-DD: 任务数} 字典，供万年历标记使用"""
        counts: dict = {}
        for task in self.tasks:
            try:
                date_str = datetime.fromisoformat(task.created_at).strftime("%Y-%m-%d")
                counts[date_str] = counts.get(date_str, 0) + 1
            except (ValueError, TypeError):
                pass
        return counts
