import os
import win32com.client
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import json
import shutil
import threading

class LnkModifierApp:
    def __init__(self, master):
        self.master = master
        master.title("LNK文件路径片段批量修改器")
        master.geometry("950x700")
        master.resizable(True, True)

        self.lnk_files_to_process = []
        self.config_file = "lnk_modifier_config.json"
        self.load_config()

        # ========== 查找与替换路径输入 ==========
        ttk.Label(master, text="查找路径片段 (Find String):").grid(row=0, column=0, sticky="w", padx=10, pady=5)
        self.find_path_entry = ttk.Entry(master, width=80)
        self.find_path_entry.grid(row=0, column=1, columnspan=3, sticky="ew", padx=10, pady=5)
        if self.saved_find_path:
            self.find_path_entry.insert(0, self.saved_find_path)

        ttk.Label(master, text="替换为路径片段 (Replace String):").grid(row=1, column=0, sticky="w", padx=10, pady=5)
        self.replace_path_entry = ttk.Entry(master, width=80)
        self.replace_path_entry.grid(row=1, column=1, columnspan=2, sticky="ew", padx=10, pady=5)
        if self.saved_replace_path:
            self.replace_path_entry.insert(0, self.saved_replace_path)
        ttk.Button(master, text="选择目录", command=lambda: self.browse_path(self.replace_path_entry)).grid(row=1, column=3, padx=5, pady=5)

        # ========== 模式选择 ==========
        ttk.Label(master, text="选择替换范围:").grid(row=2, column=0, sticky="w", padx=10, pady=5)
        self.mode_var = tk.StringVar(value=self.saved_mode if self.saved_mode else "all")
        ttk.Radiobutton(master, text="同时替换目标路径和起始位置", variable=self.mode_var, value="all").grid(row=2, column=1, sticky="w", padx=5)
        ttk.Radiobutton(master, text="仅替换目标路径", variable=self.mode_var, value="target_only").grid(row=3, column=1, sticky="w", padx=5)
        ttk.Radiobutton(master, text="仅替换起始位置", variable=self.mode_var, value="working_dir_only").grid(row=4, column=1, sticky="w", padx=5)

        self.check_path_var = tk.BooleanVar(value=self.saved_check_path if self.saved_check_path is not None else True)
        ttk.Checkbutton(master, text="替换后检查新目标路径是否有效", variable=self.check_path_var).grid(row=4, column=3, sticky="w", padx=10)

        # ========== 操作按钮 ==========
        ttk.Button(master, text="查找LNK文件", command=self.open_directory_dialog).grid(row=5, column=0, padx=10, pady=10, sticky="w")
        ttk.Button(master, text="预览修改", command=self.preview_changes).grid(row=5, column=1, padx=10, pady=10)
        ttk.Button(master, text="立即修改选中文件", command=self.modify_selected_lnk_files).grid(row=5, column=2, padx=10, pady=10)

        # ========== 文件列表 ==========
        ttk.Label(master, text="LNK文件列表:").grid(row=6, column=0, sticky="w", padx=10, pady=5)
        columns = ("File Name", "Full Path", "Old TargetPath", "Old WorkingDir")
        self.tree = ttk.Treeview(master, columns=columns, show="headings")
        self.tree.grid(row=7, column=0, columnspan=4, sticky="nsew", padx=10, pady=5)

        for col in columns:
            self.tree.heading(col, text=col)
        self.tree.column("File Name", width=180)
        self.tree.column("Full Path", width=360)
        self.tree.column("Old TargetPath", width=220)
        self.tree.column("Old WorkingDir", width=180)

        vsb = ttk.Scrollbar(master, orient="vertical", command=self.tree.yview)
        vsb.grid(row=7, column=4, sticky="ns")
        self.tree.configure(yscrollcommand=vsb.set)

        self.status_label = ttk.Label(master, text="状态：就绪", anchor="w")
        self.status_label.grid(row=8, column=0, columnspan=4, sticky="ew", padx=10, pady=5)

        # 窗口自适应布局
        master.grid_rowconfigure(7, weight=1)
        master.grid_columnconfigure(1, weight=1)
        master.protocol("WM_DELETE_WINDOW", self.on_closing)

    # ========== 配置文件处理 ==========
    def load_config(self):
        self.saved_find_path = ""
        self.saved_replace_path = ""
        self.saved_mode = ""
        self.saved_check_path = True
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.saved_find_path = data.get("find_path", "")
                    self.saved_replace_path = data.get("replace_path", "")
                    self.saved_mode = data.get("mode", "all")
                    self.saved_check_path = data.get("check_path_exists", True)
            except Exception as e:
                messagebox.showwarning("配置文件错误", f"无法加载配置：{e}")

    def save_config(self):
        data = {
            "find_path": self.find_path_entry.get(),
            "replace_path": self.replace_path_entry.get(),
            "mode": self.mode_var.get(),
            "check_path_exists": self.check_path_var.get()
        }
        try:
            with open(self.config_file, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
        except Exception as e:
            messagebox.showwarning("保存配置错误", f"无法保存配置文件: {e}")

    def on_closing(self):
        self.save_config()
        self.master.destroy()

    # ========== 查找LNK文件 ==========
    def open_directory_dialog(self):
        path = filedialog.askdirectory(title="选择扫描目录")
        if not path:
            path = os.getcwd()
        threading.Thread(target=self.find_lnk_files, args=(path,), daemon=True).start()

    def find_lnk_files(self, start_path):
        """递归扫描LNK文件"""
        self.status_label.config(text=f"正在扫描目录：{start_path} ...")
        self.tree.delete(*self.tree.get_children())
        self.lnk_files_to_process.clear()

        for root, _, files in os.walk(start_path):
            for file in files:
                if file.lower().endswith(".lnk"):
                    full_path = os.path.join(root, file)
                    self.lnk_files_to_process.append(full_path)
                    old_target, old_work = self.get_shortcut_info(full_path)
                    self.tree.insert("", "end", values=(file, full_path, old_target, old_work))

        total = len(self.lnk_files_to_process)
        self.status_label.config(text=f"扫描完成，共找到 {total} 个 .lnk 文件")

        if total == 0:
            messagebox.showinfo("结果", "未找到任何 .lnk 文件。")
        else:
            messagebox.showinfo("扫描完成", f"共找到 {total} 个 .lnk 文件。")

    def get_shortcut_info(self, path):
        try:
            shell = win32com.client.Dispatch("WScript.Shell")
            shortcut = shell.CreateShortCut(path)
            target = shortcut.TargetPath or ""
            workdir = shortcut.WorkingDirectory or ""
            return target, workdir
        except Exception as e:
            return f"错误: {e}", ""

    # ========== 预览和修改 ==========
    def apply_path_replacement(self, original, find, repl):
        if not find:
            return original
        return original.replace(find, repl)

    def preview_changes(self):
        if not self.lnk_files_to_process:
            messagebox.showwarning("请先扫描", "请先执行 '查找LNK文件'")
            return
        find_str = self.find_path_entry.get()
        replace_str = self.replace_path_entry.get()
        if not find_str:
            messagebox.showwarning("输入缺失", "请填写 '查找路径片段'")
            return

        preview_window = tk.Toplevel(self.master)
        preview_window.title("预览修改结果")
        preview_window.geometry("1100x600")

        tree = ttk.Treeview(preview_window, columns=("File", "OldTarget", "NewTarget", "OldWorkDir", "NewWorkDir"), show="headings")
        for col in ("File", "OldTarget", "NewTarget", "OldWorkDir", "NewWorkDir"):
            tree.heading(col, text=col)
            tree.column(col, width=200)
        tree.pack(fill="both", expand=True)

        for lnk in self.lnk_files_to_process:
            old_target, old_work = self.get_shortcut_info(lnk)
            new_target = self.apply_path_replacement(old_target, find_str, replace_str)
            new_work = self.apply_path_replacement(old_work, find_str, replace_str)
            tree.insert("", "end", values=(os.path.basename(lnk), old_target, new_target, old_work, new_work))

    def modify_selected_lnk_files(self):
        if not self.lnk_files_to_process:
            messagebox.showwarning("未找到文件", "请先执行 '查找LNK文件'")
            return

        find_str = self.find_path_entry.get()
        replace_str = self.replace_path_entry.get()
        if not find_str:
            messagebox.showwarning("输入缺失", "请填写 '查找路径片段'")
            return

        confirm = messagebox.askyesno("确认修改", f"确认要修改 {len(self.lnk_files_to_process)} 个 LNK 文件？")
        if not confirm:
            return

        for lnk in self.lnk_files_to_process:
            try:
                shell = win32com.client.Dispatch("WScript.Shell")
                sc = shell.CreateShortCut(lnk)
                sc.TargetPath = self.apply_path_replacement(sc.TargetPath or "", find_str, replace_str)
                sc.WorkingDirectory = self.apply_path_replacement(sc.WorkingDirectory or "", find_str, replace_str)
                sc.Save()
            except Exception as e:
                print(f"修改失败：{lnk} -> {e}")

        messagebox.showinfo("完成", "所有 LNK 文件已修改完成。")
        self.find_lnk_files(os.getcwd())

# 运行程序
if __name__ == "__main__":
    root = tk.Tk()
    app = LnkModifierApp(root)
    root.mainloop()
