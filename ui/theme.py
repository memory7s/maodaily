"""
主题配色 —— 参考「指尖时光」风格
品牌色: #FF8700 (橙色)
背景:   #F5F5F5 (浅灰)
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
    "工作": "#FF6B6B",   # 红
    "学习": "#4DABF7",   # 蓝
    "生活": "#51CF66",   # 绿
    "其他": "#868E96",   # 灰
}

# ── 优先级色 ──
PRIORITY_COLORS = {
    "高": "#FF6B6B",
    "中": "#FF8700",
    "低": "#ADB5BD",
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
    "build_theme",
]
