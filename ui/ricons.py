"""
RemixIcon 图标常量 —— v4.6.0 (Apache-2.0)
https://remixicon.com

字体文件位于 assets/fonts/remixicon.ttf，由 main.py 通过 page.fonts 注册。
Flet 0.86 的 icon= 参数接受任意控件（IconDataOrControl），
因此所有图标统一用「Text + remixicon 字体」的方式渲染：

    from .ricons import RI, ri
    ft.Text(RI.BELL, font_family=RI.FONT)          # 手写
    ri(RI.BELL, size=18, color=TEXT_SECONDARY)     # 快捷函数
    ft.IconButton(icon=ri(RI.CLOSE, 18))           # 按钮里塞字形

码点来源: remixicon.css (v4.6.0)，升级字体版本前请勿改动。
"""

import flet as ft

FONT = "remixicon"


class RI:
    """RemixIcon 码点（字符串形式，直接作为 Text 的 value 使用）"""

    FONT = "remixicon"

    # ── 导航 ──
    LIST_CHECK = "\ueeb9"      # list-check-2 全部任务
    BRIEFCASE = "\ueaf5"       # briefcase-line 工作
    BOOK_OPEN = "\ueadb"       # book-open-line 学习
    HOME = "\uee1f"            # home-5-line 生活
    PAUSE_CIRCLE = "\uefd6"    # pause-circle-line 暂时不做
    FORBID = "\ued95"          # forbid-line 就是不做
    CALENDAR = "\ueb27"        # calendar-line 日历
    SETTINGS = "\uf0e6"        # settings-3-line 设置
    SETTINGS_FILL = "\uf0e5"   # settings-3-fill 设置标题

    # ── 任务状态 ──
    CIRCLE = "\ueb7d"          # checkbox-blank-circle-line 未完成圈
    CIRCLE_DONE = "\ueb80"     # checkbox-circle-fill 已完成勾
    CHECK = "\ueb7b"           # check-line 步骤完成
    STAR_FILL = "\uf186"       # star-fill 已标星
    STAR_LINE = "\uf18b"       # star-line 未标星
    BELL = "\ueabc"            # bell-line 提醒

    # ── 操作 ──
    ADD = "\uea13"             # add-line 添加
    CLOSE = "\ueb99"           # close-line 删除/关闭
    EDIT = "\uec86"            # edit-line 编辑
    DELETE = "\uec2a"          # delete-bin-line 删除
    MORE = "\uef76"            # more-2-fill ⋯ 菜单
    ALARM_ADD = "\uf5d0"       # alarm-add-line 设置提醒
    HISTORY = "\uee17"         # history-line 恢复备份
    SHIELD_CHECK = "\uf100"    # shield-check-line 备份
    FOLDER_OPEN = "\ued70"     # folder-open-line 打开目录
    FILE_TEXT = "\ued0f"       # file-text-line 数据文件

    # ── 主题切换 ──
    MOON = "\uef75"            # moon-line（亮色模式按钮，点击切暗色）
    PALETTE = "\uefc5"         # palette-line（暗色模式按钮）
    SUN = "\uf1bf"             # sun-line（Neo 模式按钮）
    STYLE_LIGHT = "\uf1bf"     # 风格卡片：亮色 ☀
    STYLE_DARK = "\uef75"      # 风格卡片：暗色 ☾
    STYLE_NEO = "\uee97"       # 风格卡片：Neo 砖石 layout-masonry-line

    # ── 方向 ──
    ARROW_UP_S = "\uea78"      # arrow-up-s-line
    ARROW_DOWN_S = "\uea4e"    # arrow-down-s-line
    ARROW_LEFT_S = "\uea64"    # arrow-left-s-line
    ARROW_RIGHT_S = "\uea6e"   # arrow-right-s-line
    BACK = "\uea58"            # arrow-go-back-line 返回
    TIME = "\uf20f"            # time-line 时间

    # ── 布局 ──
    MENU_FOLD = "\uef3d"       # menu-fold-line 收起导航栏
    MENU_UNFOLD = "\uef40"     # menu-unfold-line 展开导航栏


def ri(codepoint: str, size=None, color=None, **kwargs) -> ft.Text:
    """快捷构造一个 RemixIcon 字形 Text 控件"""
    return ft.Text(codepoint, size=size, color=color, font_family=FONT, **kwargs)
