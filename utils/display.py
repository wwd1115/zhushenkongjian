import os
import sys
import colorama
from colorama import Fore, Back, Style
import time

colorama.init(autoreset=True)

# 增加 GUI 模式的钩子
GUI_INSTANCE = None

def set_gui_mode(gui_app):
    global GUI_INSTANCE
    GUI_INSTANCE = gui_app

def _strip_colors(text):
    # 简单的脱色处理
    import re
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    return ansi_escape.sub('', text)

def clear_screen():
    if GUI_INSTANCE:
        GUI_INSTANCE.gui_clear()
    else:
        os.system('cls' if os.name == 'nt' else 'clear')

def print_header(title):
    text = f"=== {title} ==="
    if GUI_INSTANCE:
        GUI_INSTANCE.gui_print(text, "cyan")
    else:
        print("\n" + Fore.CYAN + Style.BRIGHT + text)
    
def print_warning(text):
    if GUI_INSTANCE:
        GUI_INSTANCE.gui_print(f"[警告] {_strip_colors(text)}", "yellow")
    else:
        print(Fore.YELLOW + text)

def print_error(text):
    if GUI_INSTANCE:
        GUI_INSTANCE.gui_print(f"[错误] {_strip_colors(text)}", "red")
    else:
        print(Fore.RED + text)

def print_success(text):
    if GUI_INSTANCE:
        GUI_INSTANCE.gui_print(f"[成功] {_strip_colors(text)}", "green")
    else:
        print(Fore.GREEN + text)

def print_info(text):
    if GUI_INSTANCE:
        GUI_INSTANCE.gui_print(_strip_colors(text), "white")
    else:
        print(Fore.WHITE + text)

def draw_progress_bar(current, total, length=20, color=Fore.GREEN):
    if total <= 0: 
        bar_text = f"|{' ' * length}| 0/0"
        return bar_text if GUI_INSTANCE else f"{color}{bar_text}{Style.RESET_ALL}"
        
    percent = min(1.0, max(0.0, current / total))
    filled = int(length * percent)
    bar = '█' * filled + '-' * (length - filled)
    bar_text = f"|{bar}| {current}/{total}"
    
    return bar_text if GUI_INSTANCE else f"{color}{bar_text}{Style.RESET_ALL}"

def get_input(prompt="请选择: ", **kwargs):
    if GUI_INSTANCE:
        # 简单判断，如果是要求输入数字/具体数值（比如加点），应当用文字输入框
        if "请输入" in prompt or "点数" in prompt:
            return GUI_INSTANCE.gui_get_text_input(prompt)
        
        GUI_INSTANCE.gui_print(prompt)
        # 默认继续按钮
        return GUI_INSTANCE.gui_get_input({"ENTER": "确认"}, **kwargs)
    return input(Fore.CYAN + prompt + Style.RESET_ALL)

def get_text_input(prompt="请输入:"):
    if GUI_INSTANCE:
        return GUI_INSTANCE.gui_get_text_input(prompt)
    else:
        return input(Fore.CYAN + prompt + Style.RESET_ALL)

def show_menu(title, options, **kwargs):
    print_header(title)
    if GUI_INSTANCE:
        # 提交给GUI渲染按钮
        return GUI_INSTANCE.gui_get_input(options, **kwargs)
    else:
        for key, value in options.items():
            print(Fore.WHITE + f"[{key}] {value}")
        
        while True:
            choice = input(Fore.CYAN + "请选择: " + Style.RESET_ALL)
            if choice in options:
                return choice
            print_error("无效的选择，请重新输入。")
