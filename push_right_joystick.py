# 使用前请确保已安装 ViGEmBus 驱动: https://github.com/ViGEm/ViGEmBus/releases
import vgamepad as vg
from pynput import keyboard
import time
import threading

# --- 全局变量 ---
gamepad = vg.VDS4Gamepad()  # 创建一个虚拟 DS4 手柄
bound_key = None  # 用于存储绑定的触发按键
is_loop_active = False  # 循环动作激活状态标志
action_thread = None  # 用于存放动作线程


def repeating_action_loop():
    """
    在独立的线程中执行循环动作：推3秒，复位，等待2秒，然后重复。
    这个循环会持续进行，直到 is_loop_active 标志变为 False。
    """
    while is_loop_active:
        print("循环中：开始向右推... (持续3秒)")
        # 模拟右摇杆向右推到最大值
        gamepad.right_joystick_float(x_value_float=1.0, y_value_float=0.0)
        gamepad.update()

        # 等待3秒
        time.sleep(3)

        # 在复位前再次检查标志，以便在3秒等待期间可以停止
        if not is_loop_active:
            break

        print("循环中：复位摇杆... (等待2秒)")
        # 复位摇杆
        gamepad.right_joystick_float(x_value_float=0.0, y_value_float=0.0)
        gamepad.update()

        # 等待2秒，完成一个5秒的周期
        time.sleep(2)

    # 确保循环停止时摇杆是复位的
    gamepad.right_joystick_float(x_value_float=0.0, y_value_float=0.0)
    gamepad.update()
    print("循环动作已停止，摇杆已复位。")


def on_press(key):
    """
    键盘按键按下的回调函数。
    """
    global is_loop_active, action_thread

    # 如果按下的是绑定的键，则切换循环状态
    if key == bound_key:
        is_loop_active = not is_loop_active  # 切换状态

        if is_loop_active:
            # 如果当前没有活动的线程，则启动一个新的
            if action_thread is None or not action_thread.is_alive():
                print(">>> 已启动循环动作。再次按下绑定键可停止。")
                action_thread = threading.Thread(target=repeating_action_loop)
                action_thread.start()
        else:
            print(">>> 已发送停止信号，将在当前周期结束后停止。")

    # 如果按下 Esc 键，则停止监听，退出程序
    elif key == keyboard.Key.esc:
        print("接收到 Esc 键，程序即将退出...")
        is_loop_active = False  # 确保循环线程会退出
        return False  # 停止监听


def on_bind(key):
    """
    用于绑定按键的回调函数。
    """
    global bound_key
    bound_key = key
    return False  # 停止绑定监听器


if __name__ == "__main__":
    print("=" * 40)
    print("      欢迎使用视角定时循环右推脚本")
    print("=" * 40)
    # 1. 绑定按键
    print("\n[步骤1] 请按下一个您想用来触发动作的按键...")
    with keyboard.Listener(on_press=on_bind) as bind_listener:
        bind_listener.join()
    print(f"成功绑定按键: {bound_key}")

    # 2. 启动主监听器并显示说明
    print("\n[步骤2] 脚本已启动。")
    print(f" - 按下绑定的键 '{bound_key}' 可启动循环动作。")
    print("   (动作: 视角右推3秒，复位，每5秒重复一次)")
    print(f" - 再次按下 '{bound_key}' 可停止循环。")
    print(" - 按下 'Esc' 键可随时退出本程序。")
    print("-" * 40)
    with keyboard.Listener(on_press=on_press) as main_listener:
        main_listener.join()

    print("程序已退出。")