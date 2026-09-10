"""
任务数据管理模块
提供 Task、TaskStep 数据模型，以及 TaskManager 负责 JSON 持久化。
"""

import json
import os
from datetime import datetime
from typing import List, Optional

# 数据文件路径（存放在项目日志目录，方便携带迁移）
_script_dir = os.path.dirname(os.path.abspath(__file__))
if os.sep.join(['build', 'windows', 'app']) in _script_dir:
    # 打包版: build/windows/app/task_manager.py → 上4层到 D:\Project
    _root = os.path.normpath(os.path.join(_script_dir, '..', '..', '..', '..'))
else:
    # 开发版: D:\Project/alive-daily/task_manager.py → 上1层到 D:\Project
    _root = os.path.normpath(os.path.join(_script_dir, '..'))
DATA_DIR = os.path.join(_root, 'alivedaily项目日志', 'data')
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

    def __init__(self, on_save_status: callable = None):
        self.tasks: List[Task] = []
        self.on_save_status: callable = on_save_status  # 保存状态回调: fn("saving"|"saved"|"error", msg="")
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
        if self.on_save_status:
            self.on_save_status("saving")
        try:
            data = {"tasks": [t.to_dict() for t in self.tasks]}
            with open(DATA_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except OSError as exc:
            if self.on_save_status:
                self.on_save_status("error", str(exc))
            raise
        if self.on_save_status:
            self.on_save_status("saved")

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
        """返回 {YYYY-MM-DD: 任务数} 字典，基于 created_at 和 reminder_date"""
        counts: dict = {}
        for task in self.tasks:
            # 创建日期
            try:
                date_str = datetime.fromisoformat(task.created_at).strftime("%Y-%m-%d")
                counts[date_str] = counts.get(date_str, 0) + 1
            except (ValueError, TypeError):
                pass
            # 提醒日期
            if task.reminder_date:
                counts[task.reminder_date] = counts.get(task.reminder_date, 0) + 1
        return counts

    def get_tasks_by_date(self, date_str: str) -> List[Task]:
        """返回指定日期的所有任务（基于 created_at 或 reminder_date）"""
        result = []
        for task in self.tasks:
            try:
                created_date = datetime.fromisoformat(task.created_at).strftime("%Y-%m-%d")
                if created_date == date_str:
                    result.append(task)
                    continue
            except (ValueError, TypeError):
                pass
            if task.reminder_date == date_str:
                result.append(task)
        return result

    # ---------- 备份与恢复 ----------

    BACKUP_KEEP = 3  # 自动备份最多保留份数

    @property
    def backup_dir(self) -> str:
        return os.path.join(DATA_DIR, "backups")

    def _backup_index_path(self) -> str:
        return os.path.join(self.backup_dir, "index.json")

    def _backup_filename(self, stamp: str, suffix: str = "") -> str:
        return f"tasks-{stamp}{'-' + suffix if suffix else ''}.json"

    def _read_backup_index(self) -> dict:
        """读取备份索引 {version, backups: [{id, filename, type, label, size, size_bytes, created_at}]}"""
        try:
            with open(self._backup_index_path(), "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError, OSError):
            return {"version": 1, "backups": []}

    def _write_backup_index(self, index: dict):
        os.makedirs(self.backup_dir, exist_ok=True)
        with open(self._backup_index_path(), "w", encoding="utf-8") as f:
            json.dump(index, f, ensure_ascii=False, indent=2)

    def list_backups(self, include_missing: bool = True) -> List[dict]:
        """列出备份记录，按时间倒序。丢失文件会被过滤（除非 include_missing）"""
        index = self._read_backup_index()
        records = []
        for item in index.get("backups", []):
            if not include_missing:
                if not os.path.exists(os.path.join(self.backup_dir, item["filename"])):
                    continue
            records.append(item)
        records.sort(key=lambda r: r.get("created_at", ""), reverse=True)
        return records

    def create_backup(self, backup_type: str = "manual", label: str = "") -> dict:
        """创建一份完整备份，返回记录 dict"""
        os.makedirs(self.backup_dir, exist_ok=True)
        stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        filename = self._backup_filename(stamp)
        path = os.path.join(self.backup_dir, filename)
        size = 0
        try:
            data = {"tasks": [t.to_dict() for t in self.tasks]}
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            size = os.path.getsize(path)
        except OSError:
            # 写失败时清理残留
            if os.path.exists(path):
                try:
                    os.remove(path)
                except OSError:
                    pass
            raise

        record = {
            "id": stamp,
            "filename": filename,
            "type": backup_type,
            "label": label or {"manual": "手动备份", "automatic": "每日自动备份"}.get(backup_type, ""),
            "size_bytes": size,
            "size": self._human_size(size),
            "created_at": datetime.now().isoformat(timespec="seconds"),
        }
        index = self._read_backup_index()
        index.setdefault("backups", []).append(record)
        self._write_backup_index(index)
        return record

    def rename_backup(self, backup_id: str, new_label: str) -> bool:
        """重命名备份备注，返回是否成功"""
        index = self._read_backup_index()
        for item in index.get("backups", []):
            if item.get("id") == backup_id:
                item["label"] = new_label.strip() or item.get("label", "")
                self._write_backup_index(index)
                return True
        return False

    def delete_backup(self, backup_id: str) -> bool:
        """删除备份文件与记录，返回是否成功"""
        index = self._read_backup_index()
        for i, item in enumerate(index.get("backups", [])):
            if item.get("id") == backup_id:
                path = os.path.join(self.backup_dir, item["filename"])
                if os.path.exists(path):
                    try:
                        os.remove(path)
                    except OSError:
                        return False
                del index["backups"][i]
                self._write_backup_index(index)
                return True
        return False

    def restore_backup(self, backup_id: str) -> bool:
        """从备份恢复数据。恢复前先创建一份“恢复前安全备份”。"""
        record = next((b for b in self.list_backups(include_missing=False) if b.get("id") == backup_id), None)
        if record is None:
            return False
        path = os.path.join(self.backup_dir, record["filename"])
        try:
            with open(path, "r", encoding="utf-8") as f:
                raw = json.load(f)
            # 校验备份可读
            tasks = [Task.from_dict(t) for t in raw.get("tasks", [])]
        except (json.JSONDecodeError, KeyError, OSError):
            return False
        # 恢复前安全备份
        try:
            self.create_backup("safety", f"恢复前安全备份 {datetime.now().strftime('%H:%M')}")
        except OSError:
            pass  # 安全备份失败不阻止恢复
        self.tasks = tasks
        self.save()
        return True

    def ensure_daily_backup(self) -> dict:
        """每日自动备份：当天已有自动备份则跳过，否则创建并裁剪旧份"""
        today = datetime.now().strftime("%Y-%m-%d")
        existing = [b for b in self.list_backups(include_missing=False)
                    if b.get("type") == "automatic" and b.get("created_at", "").startswith(today)]
        if existing:
            return existing[0]
        record = self.create_backup("automatic", "每日自动备份")
        self._trim_automatic_backups()
        return record

    def _trim_automatic_backups(self):
        """只保留最近 BACKUP_KEEP 份自动备份"""
        auto = [b for b in self.list_backups(include_missing=False) if b.get("type") == "automatic"]
        if len(auto) <= self.BACKUP_KEEP:
            return
        index = self._read_backup_index()
        keep_ids = set(b["id"] for b in sorted(auto, key=lambda r: r.get("created_at", ""), reverse=True)[: self.BACKUP_KEEP])
        remaining = [item for item in index.get("backups", []) if item.get("type") != "automatic" or item.get("id") in keep_ids]
        # 删除被裁剪的自动备份文件
        removed = {item["id"] for item in index.get("backups", [])} - {item["id"] for item in remaining}
        for item in index.get("backups", []):
            if item.get("id") in removed:
                try:
                    os.remove(os.path.join(self.backup_dir, item["filename"]))
                except OSError:
                    pass
        index["backups"] = remaining
        self._write_backup_index(index)

    @staticmethod
    def _human_size(size_bytes: int) -> str:
        if size_bytes < 1024:
            return f"{size_bytes} B"
        if size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f} KB"
        return f"{size_bytes / (1024 * 1024):.1f} MB"

    def get_data_file_status(self) -> dict:
        """返回数据文件状态: 路径 / 大小 / 修改时间 / 可写性 / 任务数"""
        os.makedirs(DATA_DIR, exist_ok=True)
        status = {
            "path": DATA_FILE,
            "exists": os.path.exists(DATA_FILE),
            "size": "0 B",
            "modified": "—",
            "writable": os.access(DATA_DIR, os.W_OK),
            "task_count": len(self.tasks),
            "backup_count": len(self.list_backups(include_missing=False)),
        }
        if status["exists"]:
            try:
                status["size"] = self._human_size(os.path.getsize(DATA_FILE))
                status["modified"] = datetime.fromtimestamp(os.path.getmtime(DATA_FILE)).strftime("%Y-%m-%d %H:%M")
            except OSError:
                pass
        return status
