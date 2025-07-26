import time
import random
from pynput import mouse, keyboard
from pynput.mouse import Button
from pynput.keyboard import Key
import threading

class AutoScriptTask:
    def __init__(self):
        self.mouse_controller = mouse.Controller()
        self.keyboard_controller = keyboard.Controller()
        self.running = False  # 任务是否正在运行
        self.stopped = True   # 任务是否已停止
        self.current_step = 0  # 当前执行到的步骤索引
        self.current_scheme = 0  # 当前任务方案索引
        self.schemes = []     # 存储所有任务方案
        self.selecting_scheme = False  # 是否正在选择方案
        
    def hold_and_release(self, button='left', duration=1.0, position=None):
        """
        按住鼠标按键或键盘按键一段时间后松开
        
        Args:
            button: 要按住的按键 ('left', 'right', 'middle') 或键盘按键
            duration: 按住的时间（秒）
            position: 鼠标位置 (x, y)，如果为None则在当前位置按住
        """
        if position:
            self.mouse_controller.position = position
            
        if button in ['left', 'right', 'middle']:
            # 鼠标按键处理
            mouse_button = getattr(Button, button)
            print(f"按下鼠标{button}键，持续{duration}秒")
            self.mouse_controller.press(mouse_button)
            time.sleep(duration)
            self.mouse_controller.release(mouse_button)
            print(f"松开鼠标{button}键")
        else:
            # 键盘按键处理
            print(f"按下键盘{button}键，持续{duration}秒")
            # 修改: 处理特殊按键
            if isinstance(button, str) and hasattr(Key, button):
                key = getattr(Key, button)
                self.keyboard_controller.press(key)
                time.sleep(duration)
                self.keyboard_controller.release(key)
            else:
                self.keyboard_controller.press(button)
                time.sleep(duration)
                self.keyboard_controller.release(button)
            print(f"松开键盘{button}键")
    
    def click_position(self, x, y, button='left', clicks=1, interval=0.1):
        """
        点击指定位置
        
        Args:
            x, y: 屏幕坐标
            button: 鼠标按键
            clicks: 点击次数
            interval: 多次点击间隔时间
        """
        self.mouse_controller.position = (x, y)
        mouse_button = getattr(Button, button)
        for _ in range(clicks):
            self.mouse_controller.click(mouse_button, 1)
            time.sleep(interval)
    
    def type_text(self, text, interval=0.1):
        """
        输入文本
        
        Args:
            text: 要输入的文本
            interval: 字符间间隔时间
        """
        for char in text:
            self.keyboard_controller.press(char)
            self.keyboard_controller.release(char)
            time.sleep(interval)
    
    def wait(self, seconds):
        """
        等待指定时间
        
        Args:
            seconds: 等待时间（秒）
        """
        print(f"等待 {seconds} 秒")
        time.sleep(seconds)
    
    def random_wait(self, min_seconds, max_seconds):
        """
        随机等待时间
        
        Args:
            min_seconds: 最小等待时间
            max_seconds: 最大等待时间
        """
        wait_time = random.uniform(min_seconds, max_seconds)
        print(f"随机等待 {wait_time:.2f} 秒")
        time.sleep(wait_time)
    
    def stop(self):
        """停止执行"""
        if self.running:
            self.running = False
            self.stopped = True
            print("任务已停止")
    
    def start(self):
        """开始执行当前任务方案"""
        if self.running:
            print("任务已在运行中")
            return
            
        if not self.schemes:
            print("没有可用的任务方案")
            return
            
        self.running = True
        self.stopped = False
        self.current_step = 0  # 重置为第一步
        
        # 启动任务线程
        task_thread = threading.Thread(target=self.run_sequence)
        task_thread.daemon = True
        print("1秒后开始执行任务...")
        time.sleep(1)  # 等待1秒以便用户准备
        task_thread.start()
        print(f"任务方案 '{self.get_current_scheme_name()}' 已开始执行")
    
    def get_current_scheme_name(self):
        """获取当前任务方案的名称"""
        if not self.schemes:
            return "无方案"
        return self.schemes[self.current_scheme].get('name', f"方案 {self.current_scheme+1}")
    
    def run_sequence(self):
        """
        执行任务序列
        """
        if not self.schemes:
            print("没有可用的任务方案")
            return
            
        steps = self.schemes[self.current_scheme]['steps']
        step_count = len(steps)
        
        print(f"开始执行自动化流程: {self.get_current_scheme_name()}")
        
        while self.running and self.current_step < step_count:
            step = steps[self.current_step]
            action = step.get('action')
            params = step.get('params', {})
            
            print(f"步骤 {self.current_step + 1}/{step_count}: {action}")
            
            # 根据动作名称调用相应函数
            if hasattr(self, action):
                func = getattr(self, action)
                func(**params)
            else:
                print(f"未知动作: {action}")
            
            # 移动到下一步
            self.current_step += 1
            
            # 如果不是最后一步且任务仍在运行，添加随机间隔
            if self.running and self.current_step < step_count:
                self.random_wait(0.1, 0.5)
        
        # 如果完成所有步骤且任务仍在运行，则重新开始
        if self.running and self.current_step >= step_count:
            print(f"自动化流程 '{self.get_current_scheme_name()}' 执行完成，重新开始...")
            self.current_step = 0  # 重置为第一步
            self.run_sequence()    # 递归调用重新开始
        
        print(f"自动化流程 '{self.get_current_scheme_name()}' 执行结束")
    
    def select_scheme(self):
        """选择任务方案"""
        self.selecting_scheme = True
        print("\n" + "="*50)
        print("请选择任务方案:")
        
        # 显示所有方案
        for i, scheme in enumerate(self.schemes):
            name = scheme.get('name', f"方案 {i+1}")
            print(f"{i+1}. {name}")
        
        print("="*50)
        
        # 等待用户输入
        while self.selecting_scheme:
            try:
                selection = input("请输入方案编号 (或输入 'q' 退出选择): ")
                if selection.lower() == 'q':
                    print("取消选择任务方案")
                    self.selecting_scheme = False
                    return
                
                selection = int(selection) - 1
                if 0 <= selection < len(self.schemes):
                    self.current_scheme = selection
                    self.current_step = 0  # 重置步骤
                    print(f"已选择方案: {self.get_current_scheme_name()}")
                    self.selecting_scheme = False
                    return
                else:
                    print("无效的编号，请重新输入")
            except ValueError:
                print("请输入有效的数字")


def main():
    # 创建自动化任务实例
    task = AutoScriptTask()
    
    # 定义多个任务方案
    task.schemes = [
        {
            'name': '巴鲁矿',
            'steps': [
                {'action': 'hold_and_release', 'params': {'button': 'w', 'duration': 2.0}},
                {'action': 'random_wait', 'params': {'min_seconds': 0.5, 'max_seconds': 2}},
                {'action': 'hold_and_release', 'params': {'button': 's', 'duration': 0.6}},
                {'action': 'random_wait', 'params': {'min_seconds': 0.5, 'max_seconds': 1}},
                {'action': 'hold_and_release', 'params': {'button': 'a', 'duration': 0.3}},
                {'action': 'hold_and_release', 'params': {'button': 'f', 'duration': 3.6}},
                {'action': 'hold_and_release', 'params': {'button': 'd', 'duration': 1.7}},
                {'action': 'hold_and_release', 'params': {'button': 'f', 'duration': 3.6}},
                {'action': 'hold_and_release', 'params': {'button': 'd', 'duration': 1.7}},
                {'action': 'hold_and_release', 'params': {'button': 'w', 'duration': 0.7}},
                {'action': 'hold_and_release', 'params': {'button': 'd', 'duration': 0.5}},
                {'action': 'hold_and_release', 'params': {'button': 'f', 'duration': 3.6}},
                {'action': 'hold_and_release', 'params': {'button': 's', 'duration': 0.4}},
                {'action': 'random_wait', 'params': {'min_seconds': 0.5, 'max_seconds': 1}},
                {'action': 'hold_and_release', 'params': {'button': 'd', 'duration': 3}},
                {'action': 'hold_and_release', 'params': {'button': 'f', 'duration': 3.6}},
                {'action': 'hold_and_release', 'params': {'button': 'a', 'duration': 6.3}},
                {'action': 'hold_and_release', 'params': {'button': 'w', 'duration': 1.3}},
            ]
        },
        {
            'name': '木枝',
            'steps': [
                {'action': 'hold_and_release', 'params': {'button': 'f', 'duration': 3.6}},
                {'action': 'random_wait', 'params': {'min_seconds': 0.5, 'max_seconds': 1}},
                {'action': 'hold_and_release', 'params': {'button': 'f', 'duration': 3.6}},
                {'action': 'random_wait', 'params': {'min_seconds': 0.5, 'max_seconds': 1}},
                {'action': 'hold_and_release', 'params': {'button': 'f', 'duration': 3.6}},
                {'action': 'random_wait', 'params': {'min_seconds': 0.5, 'max_seconds': 1}},
                {'action': 'hold_and_release', 'params': {'button': 'a', 'duration': 0.4}},
                {'action': 'random_wait', 'params': {'min_seconds': 0.2, 'max_seconds': 0.6}},
                {'action': 'hold_and_release', 'params': {'button': 'w', 'duration': 0.6}},
                {'action': 'hold_and_release', 'params': {'button': 'f', 'duration': 3.6}},
                {'action': 'random_wait', 'params': {'min_seconds': 0.5, 'max_seconds': 1}},
                {'action': 'hold_and_release', 'params': {'button': 'w', 'duration': 0.3}},
                {'action': 'hold_and_release', 'params': {'button': 'd', 'duration': 0.2}},
                {'action': 'hold_and_release', 'params': {'button': 'f', 'duration': 3.6}},
                {'action': 'random_wait', 'params': {'min_seconds': 0.5, 'max_seconds': 1}},
                {'action': 'hold_and_release', 'params': {'button': 'a', 'duration': 0.2}},
                {'action': 'hold_and_release', 'params': {'button': 's', 'duration': 0.9}},                
                # {'action': 'hold_and_release', 'params': {'button': 's', 'duration': 0.6}},
                {'action': 'hold_and_release', 'params': {'button': 'd', 'duration': 0.5}},
                {'action': 'random_wait', 'params': {'min_seconds': 6, 'max_seconds': 7}},
            ]
        },
        {
            'name': '组合方案',
            'steps': [
                {'action': 'hold_and_release', 'params': {'button': 'w', 'duration': 2.0}},
                {'action': 'hold_and_release', 'params': {'button': 'f', 'duration': 3.6}},
                {'action': 'hold_and_release', 'params': {'button': 'd', 'duration': 1.7}},
                {'action': 'hold_and_release', 'params': {'button': 's', 'duration': 0.6}},
                {'action': 'hold_and_release', 'params': {'button': 'a', 'duration': 0.3}},
                {'action': 'hold_and_release', 'params': {'button': 'f', 'duration': 3.6}},
                {'action': 'hold_and_release', 'params': {'button': 'w', 'duration': 1.3}},
            ]
        }
    ]
    
    # 设置默认方案
    task.current_scheme = 0
    
    print("自动化任务已初始化")
    print(f"当前任务方案: {task.get_current_scheme_name()}")
    print("按 F1 启动/停止任务")
    print("按 F3 切换任务方案")
    
    def on_press(key):
        if key == Key.f1:
            if task.running:
                task.stop()
            else:
                task.start()
        elif key == Key.f3:
            # 如果任务正在运行，先停止
            if task.running:
                task.stop()
                print("已停止当前任务")
            
            # 切换到方案选择
            print("切换到任务方案选择...")
            task.select_scheme()
            print(f"当前任务方案: {task.get_current_scheme_name()}")
            print("请按 F1 开始执行新方案")
    
    # 启动键盘监听
    with keyboard.Listener(on_press=on_press) as listener:
        print("监听键盘输入中...")
        listener.join()


if __name__ == "__main__":
    print("1秒后开始监听按键，请准备好...")
    print("按 F1 开始执行任务")
    print("按 F3 切换任务方案")
    time.sleep(1)
    main()