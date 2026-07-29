"""
后台提醒服务 —— 定时轮询 tasks.json 中设有提醒的任务，
到期时将通知请求放入队列，由主线程（Flet 事件循环）负责弹出对话框。
"""
import json
import os
import queue
import threading
import time
from datetime import datetime, timedelta

DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "tasks.json")

# 全局引用
_reminder_thread = None
_page = None
_notification_queue = queue.Queue()  # 线程安全队列：后台线程 → 主线程


def get_pending_notifications() -> list:
    """主线程调用：从队列中取出所有待显示的通知（非阻塞）"""
    items = []
    while not _notification_queue.empty():
        try:
            items.append(_notification_queue.get_nowait())
        except queue.Empty:
            break
    return items


def _load_reminders() -> list:
    """读取所有设有提醒的未完成任务"""
    if not os.path.exists(DATA_FILE):
        return []
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            raw = json.load(f)
    except (json.JSONDecodeError, KeyError):
        return []
    tasks = raw.get("tasks", [])
    reminders = []
    for t in tasks:
        if t.get("completed", False):
            continue
        rd = t.get("reminder_date", "")
        rt = t.get("reminder_time", "")
        if not rd or not rt:
            continue
        reminders.append({
            "id": t.get("id", ""),
            "title": t.get("title", ""),
            "reminder_date": rd,
            "reminder_time": rt,
            "reminder_advance": t.get("reminder_advance", 0),
            "reminder_frequency": t.get("reminder_frequency", "once"),
        })
    return reminders


def _check_and_notify(notified_ids: set) -> set:
    """检查提醒，对到期未通知的弹出 AlertDialog，返回已通知 ID 集合"""
    now = datetime.now()
    reminders = _load_reminders()
    print(f"[ReminderService] 轮询: 当前={now.strftime('%Y-%m-%d %H:%M:%S')} | 待检查={len(reminders)} | 已通知={len(notified_ids)}")

    for r in reminders:
        rid = r["id"]
        # 使用 (任务ID, 提醒日期, 提醒时间) 组合作为唯一标识，支持修改提醒时间或周期提醒触发
        notified_key = (rid, r["reminder_date"], r["reminder_time"])
        if notified_key in notified_ids:
            continue

        try:
            remind_dt = datetime.strptime(
                f"{r['reminder_date']} {r['reminder_time']}", "%Y-%m-%d %H:%M"
            )
        except ValueError:
            continue

        advance_minutes = r.get("reminder_advance", 0)
        remind_dt = remind_dt - timedelta(minutes=advance_minutes)

        print(f"[ReminderService] 检查: {r['title']} | 提醒={remind_dt} | 当前={now} | 到期={now >= remind_dt}")

        if now >= remind_dt:
            print(f"[ReminderService] 🔔 触发提醒: {r['title']}")
            _notification_queue.put({
                "title": r["title"],
                "message": f"提醒时间：{r['reminder_date']} {r['reminder_time']}",
            })
            notified_ids.add(notified_key)

            if r["reminder_frequency"] == "once":
                _clear_reminder(r["id"])

    return notified_ids


def _clear_reminder(task_id: str):
    """单次提醒触发后自动清除提醒字段"""
    if not os.path.exists(DATA_FILE):
        return
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            raw = json.load(f)
    except (json.JSONDecodeError, KeyError):
        return

    for t in raw.get("tasks", []):
        if t.get("id") == task_id:
            t["reminder_date"] = ""
            t["reminder_time"] = ""
            t["reminder_advance"] = 0
            t["reminder_frequency"] = "once"
            break

    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(raw, f, ensure_ascii=False, indent=2)


def start_reminder_service(page=None):
    """启动后台提醒线程（每 10 秒检查一次，首次延迟 2 秒）

    Args:
        page: Flet Page 对象，用于弹出 AlertDialog
    """
    global _reminder_thread, _page
    _page = page
    state = {"notified": set(), "heartbeat": 0}

    def _loop():
        time.sleep(2)
        print("[ReminderService] 🚀 开始轮询（间隔 10s）...")
        while True:
            try:
                state["notified"] = _check_and_notify(state["notified"])
                state["heartbeat"] += 1
                if state["heartbeat"] % 6 == 0:
                    print(f"[ReminderService] 💓 心跳 #{state['heartbeat']} — 线程存活")
            except Exception as ex:
                import traceback
                traceback.print_exc()
                print(f"[ReminderService] ❌ 轮询异常: {ex}")
            time.sleep(10)

    _reminder_thread = threading.Thread(target=_loop, daemon=True)
    _reminder_thread.start()
    print("[ReminderService] ✅ 后台提醒服务已启动（每 10s 轮询，Flet AlertDialog）")