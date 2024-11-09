import tkinter as tk
from tkinter import simpledialog, messagebox
import pyautogui
import threading
import time
from pynput import mouse, keyboard


class ScreenActivityTool:
    def __init__(self, root):
        self.root = root
        self.root.title("屏幕活动工具")
        self.positions = []
        self.interval = 2
        self.repeats = 100
        self.stop_flag = False
        self.keyboard_listener = None

        # 创建并放置GUI组件
        self.create_widgets()

    def create_widgets(self):
        # 添加位置按钮
        self.add_position_button = tk.Button(self.root, text="添加位置", command=self.enter_add_position_mode)
        self.add_position_button.pack()

        # 设置间隔时间
        self.interval_label = tk.Label(self.root, text="间隔时间(秒):")
        self.interval_label.pack()
        self.interval_entry = tk.Entry(self.root)
        self.interval_entry.insert(0, "2")
        self.interval_entry.pack()

        # 设置重复次数
        self.repeats_label = tk.Label(self.root, text="重复次数:")
        self.repeats_label.pack()
        self.repeats_entry = tk.Entry(self.root)
        self.repeats_entry.insert(0, "100")
        self.repeats_entry.pack()

        # 开始按钮
        self.start_button = tk.Button(self.root, text="开始", command=self.start_activity)
        self.start_button.pack()

        # 停止按钮
        self.stop_button = tk.Button(self.root, text="停止", command=self.stop_activity)
        self.stop_button.pack()

        # 提示标签
        self.escape_label = tk.Label(self.root, text="按 ESC 键退出程序")
        self.escape_label.pack()

    def enter_add_position_mode(self):
        if len(self.positions) < 5:
            self.listener = mouse.Listener(on_click=self.on_click)
            self.listener.start()
            self.root.config(cursor="crosshair")
            self.show_temporary_popup("请在屏幕上点击以选择位置")
        else:
            messagebox.showwarning("警告", "最多只能添加5个位置")

    def on_click(self, x, y, button, pressed):
        if pressed and button == mouse.Button.left:
            self.listener.stop()
            self.root.config(cursor="")
            self.positions.append((x, y))
            self.show_position_added_popup(f"位置已添加: ({x}, {y})")
            if len(self.positions) < 5:
                answer = messagebox.askyesno("继续添加", "是否继续添加位置?")
                if answer:
                    self.enter_add_position_mode()

    def show_position_added_popup(self, message):
        popup = tk.Toplevel(self.root)
        popup.title("提示")
        label = tk.Label(popup, text=message)
        label.pack(padx=20, pady=10)
        popup.after(1000, popup.destroy)  # 1秒后自动关闭

    def show_temporary_popup(self, message):
        popup = tk.Toplevel(self.root)
        popup.title("提示")
        label = tk.Label(popup, text=message)
        label.pack(padx=20, pady=10)
        popup.after(1000, popup.destroy)  # 1秒后自动关闭

    def start_activity(self):
        try:
            self.interval = float(self.interval_entry.get())
            self.repeats = int(self.repeats_entry.get())
            if not self.positions:
                raise ValueError("至少需要添加一个位置")
            self.stop_flag = False
            self.keyboard_listener = keyboard.Listener(on_press=self.on_key_press)
            self.keyboard_listener.start()
            threading.Thread(target=self.run_activity).start()
        except ValueError as e:
            messagebox.showerror("错误", str(e))

    def run_activity(self):
        for _ in range(self.repeats):
            if self.stop_flag:
                break
            for pos in self.positions:
                if self.stop_flag:
                    break
                x, y = pos
                pyautogui.moveTo(x, y, duration=0.5)
                pyautogui.click()  # 添加点击操作
                time.sleep(self.interval)

    def stop_activity(self):
        self.stop_flag = True
        if self.keyboard_listener:
            self.keyboard_listener.stop()

    def on_key_press(self, key):
        if key == keyboard.Key.esc:
            self.stop_activity()


if __name__ == "__main__":
    root = tk.Tk()
    app = ScreenActivityTool(root)
    root.mainloop()
