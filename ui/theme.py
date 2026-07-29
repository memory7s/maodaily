"""
主题配色 —— 参考「指尖时光」风格
品牌色: #FF8700 (橙色)
背景:   #F5F5F5 (浅灰)

支持亮色/暗色双主题切换，通过 ThemeManager 管理。
"""

# ── 品牌色 ──
PRIMARY = "#FF8700"
PRIMARY_HOVER = "#E07800"
PRIMARY_LIGHT = "#FFF7ED"   # 浅橙（悬停/选中背景）

# ── 页面背景 ──
BG = "#F5F5F5"

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
    """主题管理器：支持亮色/暗色切换"""

    def __init__(self, is_dark: bool = False):
        self.is_dark = is_dark
        self.light = self._build_light_theme()
        self.dark = self._build_dark_theme()

    @property
    def current(self):
        return self.dark if self.is_dark else self.light

    def toggle(self):
        """切换主题，返回新主题 dict"""
        self.is_dark = not self.is_dark
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
            "STAR_ACTIVE": "#FF8700",
            "STAR_INACTIVE": "#CCCCCC",
            "DELETE_HOVER": "#E4405F",
            "DELETE_NORMAL": "#CCCCCC",
            "ADD_STEP_HINT": "#4DABF7",
            "ADD_STEP_TEXT": "#4DABF7",
            "SHADOW": "#1A000000",
            "CARD_BORDER": "transparent",
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
            "STAR_ACTIVE": "#FF9800",
            "STAR_INACTIVE": "#616161",
            "DELETE_HOVER": "#EF5350",
            "DELETE_NORMAL": "#616161",
            "ADD_STEP_HINT": "#64B5F6",
            "ADD_STEP_TEXT": "#64B5F6",
            "SHADOW": "#40000000",
            "CARD_BORDER": "#333333",
        }


# ── Flet 主题 ──
def build_theme():
    """返回 ft.Theme 对象"""
    from flet import Theme, VisualDensity
    return Theme(
        color_scheme_seed=PRIMARY,
        visual_density=VisualDensity.COMFORTABLE,
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