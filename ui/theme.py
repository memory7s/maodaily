"""
主题配色 —— 参考「指尖时光」风格
品牌色: #FF8700 (橙色)
背景:   #F5F5F5 (浅灰)

支持三套主题循环切换:
  - light  亮色
  - dark   暗色
  - neo    Neo-Brutalism（米黄纸 + 墨黑硬边框 + 硬阴影）
通过 ThemeManager 管理。
"""

# ── 品牌色 ──
PRIMARY = "#FF8700"
PRIMARY_HOVER = "#E07800"
PRIMARY_LIGHT = "#FFF7ED"   # 浅橙（悬停/选中背景）

# ── 页面背景 ──
BG = "#F5F5F5"

# 主题偏好持久化文件（放在数据目录旁）
import json
import os as _os

def _prefs_path() -> str:
    """偏好文件路径：与数据文件同级的 ui_prefs.json"""
    try:
        from task_manager import DATA_DIR
        return _os.path.join(DATA_DIR, "ui_prefs.json")
    except Exception:
        return _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "..", "ui_prefs.json")


def load_preferred_mode() -> str:
    """读取上次保存的主题模式，默认 light"""
    try:
        with open(_prefs_path(), "r", encoding="utf-8") as f:
            return json.load(f).get("theme_mode", "light")
    except (json.JSONDecodeError, FileNotFoundError, OSError):
        return "light"


def save_preferred_mode(mode: str):
    """保存主题模式偏好"""
    try:
        data = {}
        p = _prefs_path()
        if _os.path.exists(p):
            with open(p, "r", encoding="utf-8") as f:
                data = json.load(f)
        data["theme_mode"] = mode
        _os.makedirs(_os.path.dirname(p), exist_ok=True)
        with open(p, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except (OSError, json.JSONDecodeError):
        pass

# ── 卡片 ──
CARD_BG = "#FFFFFF"
CARD_SHADOW = "#E0E0E0"

# ── 文字 ──
TEXT_PRIMARY = "#333333"
TEXT_SECONDARY = "#999999"
TEXT_DISABLED = "#CCCCCC"    # 已完成项

# ── 功能色 ──
DANGER = "#E4405F"
SUCCESS = "#4CAF50"
WARNING = "#FFC107"

# ── 标签色 ──
TAG_COLORS = {
    "工作": "#FF6B6B",       # 红
    "学习": "#4DABF7",       # 蓝
    "生活": "#51CF66",       # 绿
    "其他": "#868E96",       # 灰
    "暂时不做": "#ADB5BD",    # 浅灰
    "就是不做": "#868E96",    # 中灰
}

# ── 优先级色 ──
PRIORITY_COLORS = {
    "高": "#FF6B6B",
    "中": "#FF8700",
    "低": "#ADB5BD",
}

# ── 通用色 ──
DIVIDER = "#E0E0E0"
INPUT_BG = "#FFFFFF"
INPUT_BORDER = "#FFFFFF"
STEP_DIVIDER = "#F0F0F0"
OVERLAY_BG = "#80000000"
DIALOG_BG = "#FFFFFF"
WHITE_TEXT = "#FFFFFF"


class ThemeManager:
    """主题管理器：亮色 / 暗色 / Neo-Brutalism 三主题循环切换"""

    MODE_LABELS = {
        "light": "亮色主题",
        "dark": "暗色主题",
        "neo": "Neo-Brutalism 主题",
    }

    def __init__(self, is_dark: bool = False, mode: str = None):
        if mode is None:
            mode = load_preferred_mode()
        if mode not in self.MODE_LABELS:
            mode = "dark" if is_dark else "light"
        self.mode = mode
        self.light = self._build_light_theme()
        self.dark = self._build_dark_theme()
        self.neo = self._build_neo_theme()

    @property
    def current(self):
        return getattr(self, self.mode)

    @property
    def is_dark(self):
        """兼容旧代码：dark / neo 都视为非亮色"""
        return self.mode != "light"

    def toggle(self):
        """循环切换主题，保存偏好并返回新主题 dict"""
        modes = ["light", "dark", "neo"]
        idx = modes.index(self.mode)
        self.mode = modes[(idx + 1) % len(modes)]
        save_preferred_mode(self.mode)
        return self.current

    def switch_to(self, mode: str):
        """切换到指定主题并保存偏好"""
        if mode in self.MODE_LABELS:
            self.mode = mode
            save_preferred_mode(self.mode)
        return self.current

    # ── 亮色主题 ──
    def _build_light_theme(self):
        return {
            "PRIMARY": "#FF8700",
            "PRIMARY_HOVER": "#E07800",
            "PRIMARY_LIGHT": "#FFF7ED",
            "BG": "#F5F5F5",
            "CARD_BG": "#FFFFFF",
            "CARD_SHADOW": "#E0E0E0",
            "TEXT_PRIMARY": "#333333",
            "TEXT_SECONDARY": "#999999",
            "TEXT_DISABLED": "#CCCCCC",
            "DANGER": "#E4405F",
            "SUCCESS": "#4CAF50",
            "WARNING": "#FFC107",
            "TAG_COLORS": {
                "工作": "#FF6B6B",
                "学习": "#4DABF7",
                "生活": "#51CF66",
                "其他": "#868E96",
                "暂时不做": "#ADB5BD",
                "就是不做": "#868E96",
            },
            "PRIORITY_COLORS": {
                "高": "#FF6B6B",
                "中": "#FF8700",
                "低": "#ADB5BD",
            },
            "DIVIDER": "#E0E0E0",
            "INPUT_BG": "#FFFFFF",
            "INPUT_BORDER": "#FFFFFF",
            "STEP_DIVIDER": "#F0F0F0",
            "OVERLAY_BG": "#80000000",
            "DIALOG_BG": "#FFFFFF",
            "WHITE_TEXT": "#FFFFFF",
            "NAV_TEXT": "#666666",
            "STAR_ACTIVE": "#FF8700",
            "STAR_INACTIVE": "#CCCCCC",
            "DELETE_HOVER": "#E4405F",
            "DELETE_NORMAL": "#CCCCCC",
            "ADD_STEP_HINT": "#4DABF7",
            "ADD_STEP_TEXT": "#4DABF7",
            "SHADOW": "#1A000000",
            "CARD_BORDER": "transparent",
            "CARD_BORDER_WIDTH": 0,
            "SHADOW_BLUR": 6,
            "SHADOW_X": 0,
            "SHADOW_Y": 2,
            "STEP_BOX_BG": "#F8F9FA",
            "STEP_BOX_BORDER": "#E0E0E0",
        }

    # ── 暗色主题 ──
    def _build_dark_theme(self):
        return {
            "PRIMARY": "#FF9800",
            "PRIMARY_HOVER": "#FFA726",
            "PRIMARY_LIGHT": "#3E2723",
            "BG": "#121212",
            "CARD_BG": "#1E1E1E",
            "CARD_SHADOW": "#000000",
            "TEXT_PRIMARY": "#E0E0E0",
            "TEXT_SECONDARY": "#9E9E9E",
            "TEXT_DISABLED": "#616161",
            "DANGER": "#EF5350",
            "SUCCESS": "#66BB6A",
            "WARNING": "#FFC107",
            "TAG_COLORS": {
                "工作": "#EF5350",
                "学习": "#42A5F5",
                "生活": "#66BB6A",
                "其他": "#757575",
                "暂时不做": "#9E9E9E",
                "就是不做": "#616161",
            },
            "PRIORITY_COLORS": {
                "高": "#EF5350",
                "中": "#FF9800",
                "低": "#9E9E9E",
            },
            "DIVIDER": "#333333",
            "INPUT_BG": "#2C2C2C",
            "INPUT_BORDER": "#333333",
            "STEP_DIVIDER": "#2C2C2C",
            "OVERLAY_BG": "#B0000000",
            "DIALOG_BG": "#2C2C2C",
            "WHITE_TEXT": "#E0E0E0",
            "NAV_TEXT": "#C8C8C8",
            "STAR_ACTIVE": "#FF9800",
            "STAR_INACTIVE": "#616161",
            "DELETE_HOVER": "#EF5350",
            "DELETE_NORMAL": "#616161",
            "ADD_STEP_HINT": "#64B5F6",
            "ADD_STEP_TEXT": "#64B5F6",
            "SHADOW": "#40000000",
            "CARD_BORDER": "#333333",
            "CARD_BORDER_WIDTH": 1,
            "SHADOW_BLUR": 10,
            "SHADOW_X": 0,
            "SHADOW_Y": 4,
            "STEP_BOX_BG": "#252525",
            "STEP_BOX_BORDER": "#333333",
        }

    # ── Neo-Brutalism 主题 ──
    # 风格: 米黄纸底 + 墨黑文字 + 珊瑚主色 + 2px 硬边框 + 4px 硬偏移阴影 + 近直角
    # 颜色基调取自 my-own-app 的 neo.css（--neo-paper 等）
    def _build_neo_theme(self):
        return {
            "PRIMARY": "#D75D42",          # 珊瑚红（主操作色）
            "PRIMARY_HOVER": "#AD422E",    # 深珊瑚（悬停）
            "PRIMARY_LIGHT": "#F2C2B5",    # 浅珊瑚（选中/悬停背景）
            "BG": "#F2EDE3",               # 米黄纸（页面背景）
            "CARD_BG": "#FFFAF0",          # 白卡纸（卡片）
            "CARD_SHADOW": "#20221F",      # 墨黑（硬阴影色）
            "TEXT_PRIMARY": "#20221F",     # 墨黑（标题）
            "TEXT_SECONDARY": "#555951",   # 墨灰（次要文字）
            "TEXT_DISABLED": "#75796F",    # 淡墨（已完成项）
            "DANGER": "#AD422E",
            "SUCCESS": "#568F88",          # Neo 青绿
            "WARNING": "#D3A13F",          # Neo 金黄
            "TAG_COLORS": {
                "工作": "#D75D42",         # coral
                "学习": "#687FA3",         # blue
                "生活": "#71945F",         # leaf
                "其他": "#82766A",         # stone
                "暂时不做": "#B98542",     # ochre
                "就是不做": "#C96F82",     # rose
            },
            "PRIORITY_COLORS": {
                "高": "#D75D42",
                "中": "#D3A13F",
                "低": "#82766A",
            },
            "DIVIDER": "#9B9C91",
            "INPUT_BG": "#FFFAF0",
            "INPUT_BORDER": "#20221F",     # 输入框硬黑边
            "STEP_DIVIDER": "#DFD6C7",
            "OVERLAY_BG": "#80000000",
            "DIALOG_BG": "#FFFDF8",
            "WHITE_TEXT": "#FFFFFF",
            "NAV_TEXT": "#3E423A",
            "STAR_ACTIVE": "#D75D42",
            "STAR_INACTIVE": "#82766A",
            "DELETE_HOVER": "#D75D42",
            "DELETE_NORMAL": "#82766A",
            "ADD_STEP_HINT": "#687FA3",
            "ADD_STEP_TEXT": "#687FA3",
            "SHADOW": "#20221F",           # 硬阴影：纯墨黑无透明
            "CARD_BORDER": "#20221F",      # 2px 硬黑边
            "CARD_BORDER_WIDTH": 2,
            "SHADOW_BLUR": 0,              # 无模糊 → 硬阴影
            "SHADOW_X": 4,
            "SHADOW_Y": 4,
            "STEP_BOX_BG": "#FFF6E5",
            "STEP_BOX_BORDER": "#20221F",
            "GLOBALS": {"FONT_MONO": True},
            # 圆角控制: 卡片近直角
            "RADIUS_CARD": 3,
            "RADIUS_INPUT": 3,
        }


# ── Flet 主题 ──
def build_theme():
    """返回 ft.Theme 对象

    font_family 显式指定微软雅黑：避免 Flutter 在 Windows 上对中文逐字回落
    （中日共用汉字命中日文字体、简体专用字落到中文字体，导致同词粗细不一）。
    """
    from flet import Theme, VisualDensity
    return Theme(
        color_scheme_seed=PRIMARY,
        visual_density=VisualDensity.COMFORTABLE,
        font_family="Microsoft YaHei",
    )


__all__ = [
    "PRIMARY", "PRIMARY_HOVER", "PRIMARY_LIGHT", "BG",
    "CARD_BG", "CARD_SHADOW",
    "TEXT_PRIMARY", "TEXT_SECONDARY", "TEXT_DISABLED",
    "DANGER", "SUCCESS", "WARNING",
    "TAG_COLORS", "PRIORITY_COLORS",
    "DIVIDER", "INPUT_BG", "INPUT_BORDER", "STEP_DIVIDER",
    "OVERLAY_BG", "DIALOG_BG", "WHITE_TEXT",
    "ThemeManager", "build_theme",
]