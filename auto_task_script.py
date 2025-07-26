import time
import random
import json
import threading
import logging
from pynput import mouse, keyboard
from pynput.mouse import Button
from pynput.keyboard import Key

logging.basicConfig(
    filename="task.log",
    filemode="a",
    format="%(asctime)s [%(levelname)s] %(message)s",
    level=logging.INFO
)

class AutoScriptTask:
    def __init__(self):
        self.mouse_controller = mouse.Controller()
        self.keyboard_controller = keyboard.Controller()
        self.running = False
        self.current_step = 0
        self.current_scheme = 0
        self.schemes = []
        self.selecting_scheme = False
        self.macros = {}  # 初始化宏注册区

        # === 从 JSON 配置文件中加载宏和任务列表 ===
        try:
            with open('schemes.json', 'r', encoding='utf-8') as f:
                config = json.load(f)
                self.macros = config.get("macros", {})    # 宏注册区
                self.schemes = config.get("tasks", [])    # 任务方案列表
                print(f"成功加载 {len(self.schemes)} 个任务方案和 {len(self.macros)} 个宏定义。")
        except Exception as e:
            print(f"配置文件加载失败: {e}")


    def log(self, msg, level="info"):
        print(msg)
        getattr(logging, level)(msg)

    def load_schemes_from_file(self, path='schemes.json'):
        try:
            with open(path, 'r', encoding='utf-8') as f:
                config = json.load(f)
                self.macros = config.get("macros", {})
                self.schemes = config.get("tasks", [])
            self.log(f"成功加载 {len(self.schemes)} 个任务方案 和 {len(self.macros)} 个宏", "info")
        except Exception as e:
            self.log(f"[错误] 无法加载配置文件: {e}", "error")


    def hold_and_release(self, button='left', duration=1.0, position=None):
        try:
            if position:
                self.mouse_controller.position = position

            if button in ['left', 'right', 'middle']:
                mouse_button = getattr(Button, button)
                self.log(f"按下鼠标 {button}，持续 {duration} 秒")
                self.mouse_controller.press(mouse_button)
                time.sleep(duration)
                self.mouse_controller.release(mouse_button)
            else:
                key = getattr(Key, button) if hasattr(Key, button) else button
                self.log(f"按下键盘 {button}，持续 {duration} 秒")
                self.keyboard_controller.press(key)
                time.sleep(duration)
                self.keyboard_controller.release(key)
        except Exception as e:
            self.log(f"[错误] 执行按键 '{button}' 时异常: {e}", "error")

    def click_position(self, x, y, button='left', clicks=1, interval=0.1):
        self.mouse_controller.position = (x, y)
        mouse_button = getattr(Button, button)
        for _ in range(clicks):
            self.mouse_controller.click(mouse_button, 1)
            time.sleep(interval)

    def type_text(self, text, interval=0.1):
        for char in text:
            self.keyboard_controller.press(char)
            self.keyboard_controller.release(char)
            time.sleep(interval)

    def wait(self, seconds):
        self.log(f"等待 {seconds} 秒")
        time.sleep(seconds)

    def random_wait(self, min_seconds, max_seconds):
        wait_time = random.uniform(min_seconds, max_seconds)
        self.log(f"随机等待 {wait_time:.2f} 秒")
        time.sleep(wait_time)

    def stop(self):
        if self.running:
            self.running = False
            self.log("任务执行已手动停止")

    def start(self):
        if self.running:
            self.log("任务已在运行中")
            return
        if not self.schemes:
            self.log("未加载任何任务方案", "warning")
            return

        self.running = True
        self.current_step = 0
        self.log(f"1 秒后开始执行任务方案: {self.get_current_scheme_name()}")
        time.sleep(1)
        threading.Thread(target=self.run_sequence, daemon=True).start()

    def get_current_scheme_name(self):
        if not self.schemes:
            return "无方案"
        return self.schemes[self.current_scheme].get('name', f"方案 {self.current_scheme + 1}")

    def run_sequence(self):
        try:
            steps = self.schemes[self.current_scheme]['steps']
            total = len(steps)
            self.log(f"开始执行方案: {self.get_current_scheme_name()}")

            while self.running:
                if self.current_step >= total:
                    self.log(f"方案 '{self.get_current_scheme_name()}' 执行完毕，重新开始")
                    self.current_step = 0

                step = steps[self.current_step]
                action = step.get('action')
                params = step.get('params', {})

                self.log(f"[步骤 {self.current_step + 1}/{total}] {action} {params}")

                if action == "macro":
                    self.run_macro(params.get('steps', []))
                elif action == "macro_ref":
                    name = params.get("name")
                    macro_steps = self.macros.get(name)
                    if macro_steps:
                        self.log(f"[宏引用] 执行宏: {name}")
                        self.run_macro(macro_steps)
                    else:
                        self.log(f"[错误] 宏 '{name}' 未注册", "error")
                elif hasattr(self, action):
                    getattr(self, action)(**params)
                else:
                    self.log(f"[未知动作] {action}", "warning")

                self.current_step += 1
                if self.running and self.current_step < total:
                    self.random_wait(0.1, 0.5)

        except Exception as e:
            self.log(f"[异常] 任务执行出错: {e}", "error")
        finally:
            self.running = False
            self.log(f"任务方案 '{self.get_current_scheme_name()}' 已停止")

    def select_scheme(self):
        self.selecting_scheme = True
        print("\n" + "=" * 50)
        print("请选择任务方案:")
        for i, scheme in enumerate(self.schemes):
            print(f"{i + 1}. {scheme.get('name', f'方案 {i + 1}')}")
        print("=" * 50)

        while self.selecting_scheme:
            try:
                selection = input("请输入编号 (或 q 退出): ").strip()
                if selection.lower() == 'q':
                    self.log("取消任务方案选择")
                    break
                index = int(selection) - 1
                if 0 <= index < len(self.schemes):
                    self.current_scheme = index
                    self.current_step = 0
                    self.log(f"已选择方案: {self.get_current_scheme_name()}")
                    break
                else:
                    print("[输入错误] 编号无效")
            except ValueError:
                print("请输入有效数字")

        self.selecting_scheme = False
        
    def run_macro(self, steps):
        self.log("[宏] 开始执行组合动作")
        for sub_index, step in enumerate(steps, 1):
            action = step.get('action')
            params = step.get('params', {})
            self.log(f"[宏步骤 {sub_index}] {action} {params}")
            if action == "macro":
                self.run_macro(params.get('steps', []))  # 支持嵌套宏
            elif hasattr(self, action):
                getattr(self, action)(**params)
            else:
                self.log(f"[宏警告] 未知动作: {action}", "warning")
        self.log("[宏] 组合动作执行结束")


def keyboard_listener(task: AutoScriptTask):
    def on_press(key):
        if key == Key.f1:
            if task.running:
                task.stop()
            else:
                task.start()
        elif key == Key.f3:
            if task.running:
                task.stop()
                task.log("已停止当前任务")
            task.select_scheme()
            task.log(f"当前任务方案: {task.get_current_scheme_name()}")
            task.log("按 F1 启动新任务")

    with keyboard.Listener(on_press=on_press) as listener:
        task.log("键盘监听启动，等待按键...")
        listener.join()

def main():
    task = AutoScriptTask()
    task.load_schemes_from_file("schemes.json")
    task.log(f"当前方案: {task.get_current_scheme_name()}")
    task.log("按 F1 启动/停止任务，按 F3 切换方案")
    keyboard_listener(task)

if __name__ == "__main__":
    print("准备就绪，1 秒后启动键盘监听...")
    time.sleep(1)
    main()
