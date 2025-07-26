import json
import time
import threading
import random
from pynput import mouse, keyboard
from pynput.mouse import Button
from pynput.keyboard import Key

class AutoScriptTask:
    def __init__(self):
        self.mouse_controller = mouse.Controller()
        self.keyboard_controller = keyboard.Controller()
        self.running = False
        self.current_step = 0
        self.current_scheme = 0
        self.schemes = []
        self.macros = {}
        self.selecting_scheme = False
        self.listener = None
        self.load_schemes_from_file()

    def load_schemes_from_file(self, path='schemes.json'):
        try:
            with open(path, 'r', encoding='utf-8') as f:
                config = json.load(f)
                self.macros = config.get("macros", {})
                self.schemes = config.get("tasks", [])
            self.log(f"成功加载 {len(self.schemes)} 个任务方案 和 {len(self.macros)} 个宏", "info")
        except Exception as e:
            self.log(f"[错误] 无法加载配置文件: {e}", "error")

    def run(self):
        if not self.schemes:
            self.log("[错误] 没有加载任何任务方案", "error")
            return
        self.running = True
        while self.running:
            self.current_step = 0
            scheme = self.schemes[self.current_scheme]
            self.log(f"[运行] 当前任务方案：{scheme.get('name', '未命名')}")
            steps = scheme.get('steps', [])
            while self.running and self.current_step < len(steps):
                step = steps[self.current_step]
                action = step.get('action')
                params = step.get('params', {})
                self.log(f"[步骤 {self.current_step + 1}] {action} {params}")
                if action == "macro":
                    macro_name = params.get('name')
                    if macro_name in self.macros:
                        self.run_macro(self.macros[macro_name])
                    else:
                        self.log(f"[宏] 未找到宏：{macro_name}", "warning")
                elif hasattr(self, action):
                    getattr(self, action)(**params)
                else:
                    self.log(f"[警告] 未知动作: {action}", "warning")
                self.current_step += 1
            self.log("[循环] 当前方案执行完毕，准备下一轮...")

    def run_macro(self, steps):
        self.log("[宏] 开始执行组合动作")
        for sub_index, step in enumerate(steps, 1):
            action = step.get('action')
            params = step.get('params', {})
            self.log(f"[宏步骤 {sub_index}] {action} {params}")
            if action == "macro":
                self.run_macro(params.get('steps', []))  # 嵌套宏
            elif hasattr(self, action):
                getattr(self, action)(**params)
            else:
                self.log(f"[宏警告] 未知动作: {action}", "warning")
        self.log("[宏] 组合动作执行结束")

    def mouse_click(self, button="left", count=1, delay=0.1):
        btn = Button.left if button == "left" else Button.right
        for _ in range(count):
            self.mouse_controller.click(btn)
            time.sleep(delay)

    def mouse_move(self, x=0, y=0, relative=True):
        if relative:
            self.mouse_controller.move(x, y)
        else:
            self.mouse_controller.position = (x, y)

    def key_press(self, key):
        try:
            if len(key) == 1:
                self.keyboard_controller.press(key)
                self.keyboard_controller.release(key)
            else:
                k = getattr(Key, key, key)
                self.keyboard_controller.press(k)
                self.keyboard_controller.release(k)
        except Exception as e:
            self.log(f"[按键错误] {key}: {e}", "error")

    def wait(self, seconds=1.0):
        time.sleep(seconds)

    def random_wait(self, min_seconds=0.5, max_seconds=2.0):
        duration = random.uniform(min_seconds, max_seconds)
        self.log(f"[随机等待] {duration:.2f} 秒")
        time.sleep(duration)

    def hold_and_release(self, button, duration=1.0):
        try:
            self.log(f"[按住释放] 按键: {button}, 时长: {duration}")
            self.keyboard_controller.press(button)
            time.sleep(duration)
            self.keyboard_controller.release(button)
        except Exception as e:
            self.log(f"[错误] hold_and_release 失败：{e}", "error")

    def stop(self):
        self.running = False
        self.log("[停止] 任务已手动中止")

    def toggle_scheme(self):
        self.current_scheme = (self.current_scheme + 1) % len(self.schemes)
        scheme_name = self.schemes[self.current_scheme].get("name", f"方案 {self.current_scheme+1}")
        self.log(f"[切换] 当前任务方案已切换为：{scheme_name}", "info")

    def log(self, msg, level="info"):
        prefix = {
            "info": "[信息]",
            "warning": "[警告]",
            "error": "[错误]"
        }.get(level, "[信息]")
        print(f"{prefix} {msg}")

    def start_listener(self):
        def on_press(key):
            if key == Key.f3:
                self.toggle_scheme()
            elif key == Key.f1:
                if not self.running:
                    threading.Thread(target=self.run).start()
                else:
                    self.stop()

        self.listener = keyboard.Listener(on_press=on_press)
        self.listener.start()

# 启动示例
if __name__ == "__main__":
    task = AutoScriptTask()
    task.start_listener()
    print("监听启动成功，按 F3 切换任务方案，按 F1 启动/停止任务")
    while True:
        time.sleep(1)
