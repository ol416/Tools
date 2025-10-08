import os
import win32com.client
import pythoncom
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import json
import threading
import shutil
import time

class LnkModifierApp:
    def __init__(self, master):
        self.master = master
        master.title("LNK 文件路径片段批量修改器")
        master.geometry("1050x700")
        master.resizable(True, True)

        self.lnk_files_to_process = []
        self.config_file = "lnk_modifier_config.json"
        self.load_config()

        # ====== 查找与替换路径输入区 ======
        ttk.Label(master, text="查找路径片段 (Find String):").grid(row=0, column=0, sticky="w", padx=10, pady=5)
        self.find_path_entry = ttk.Entry(master, width=80)
        self.find_path_entry.grid(row=0, column=1, columnspan=3, sticky="ew", padx=10, pady=5)
        
        # *** 修改点 1: 移除默认的 "WorkingDirectory" 文本，只加载保存的配置。此修改点已在原代码中实现。***
        if self.saved_find_path:
            self.find_path_entry.insert(0, self.saved_find_path)

        ttk.Label(master, text="替换为路径片段 (Replace String):").grid(row=1, column=0, sticky="w", padx=10, pady=5)
        self.replace_path_entry = ttk.Entry(master, width=80)
        self.replace_path_entry.grid(row=1, column=1, columnspan=2, sticky="ew", padx=10, pady=5)
        if self.saved_replace_path:
            self.replace_path_entry.insert(0, self.saved_replace_path)
        ttk.Button(master, text="选择目录", command=lambda: self.browse_path(self.replace_path_entry)).grid(row=1, column=3, padx=5, pady=5)

        # ====== 模式选择 ======
        ttk.Label(master, text="选择替换范围:").grid(row=2, column=0, sticky="w", padx=10, pady=5)
        self.mode_var = tk.StringVar(value=self.saved_mode if self.saved_mode else "all")
        ttk.Radiobutton(master, text="同时替换目标路径和起始位置", variable=self.mode_var, value="all").grid(row=2, column=1, sticky="w", padx=5)
        ttk.Radiobutton(master, text="仅替换目标路径", variable=self.mode_var, value="target_only").grid(row=3, column=1, sticky="w", padx=5)
        ttk.Radiobutton(master, text="仅替换起始位置", variable=self.mode_var, value="working_dir_only").grid(row=4, column=1, sticky="w", padx=5)

        self.check_path_var = tk.BooleanVar(value=self.saved_check_path if self.saved_check_path is not None else True)
        ttk.Checkbutton(master, text="替换后检查新目标路径是否存在", variable=self.check_path_var).grid(row=4, column=3, sticky="w", padx=10)

        # ====== 操作按钮 ======
        # 传入 os.getcwd() 作为默认扫描目录
        ttk.Button(master, text="🔍 查找当前目录LNK文件", command=lambda: threading.Thread(target=self.find_lnk_files, args=(os.getcwd(),), daemon=True).start()).grid(row=5, column=0, padx=10, pady=10, sticky="w")
        ttk.Button(master, text="📂 自定义查找目录", command=self.select_custom_directory).grid(row=5, column=1, padx=10, pady=10, sticky="w")
        ttk.Button(master, text="👁️ 预览修改", command=self.preview_changes).grid(row=5, column=2, padx=10, pady=10)
        ttk.Button(master, text="💾 执行修改", command=self.modify_selected_lnk_files).grid(row=5, column=3, padx=10, pady=10)

        # ====== 文件列表 ======
        ttk.Label(master, text="LNK 文件列表:").grid(row=6, column=0, sticky="w", padx=10, pady=5)
        columns = ("File Name", "TargetPath", "WorkingDir")
        self.tree = ttk.Treeview(master, columns=columns, show="headings")
        self.tree.grid(row=7, column=0, columnspan=4, sticky="nsew", padx=10, pady=5)

        for col in columns:
            self.tree.heading(col, text=col)

        self.tree.column("File Name", width=150)
        self.tree.column("TargetPath", width=250)
        self.tree.column("WorkingDir", width=250)

        self.tree.bind("<Motion>", self.on_tree_hover)

        vsb = ttk.Scrollbar(master, orient="vertical", command=self.tree.yview)
        vsb.grid(row=7, column=4, sticky="ns")
        self.tree.configure(yscrollcommand=vsb.set)

        # 状态栏
        self.status_label = ttk.Label(master, text="状态：就绪", anchor="w")
        self.status_label.grid(row=8, column=0, columnspan=4, sticky="ew", padx=10, pady=5)

        # 自适应布局
        master.grid_rowconfigure(7, weight=1)
        master.grid_columnconfigure(1, weight=1)
        master.protocol("WM_DELETE_WINDOW", self.on_closing)

        # Tooltip
        self.tooltip = tk.Toplevel(self.master)
        self.tooltip.withdraw()
        self.tooltip.wm_overrideredirect(True)
        self.tooltip_label = ttk.Label(self.tooltip, background="lightyellow", relief="solid", borderwidth=1)
        self.tooltip_label.pack()

    # ====== 工具方法 ======
    def browse_path(self, entry):
        path = filedialog.askdirectory(title="选择目录")
        if path:
            entry.delete(0, tk.END)
            entry.insert(0, path)

    def on_tree_hover(self, event):
        """鼠标悬停时显示完整路径"""
        region = self.tree.identify("region", event.x, event.y)
        if region == "cell":
            row_id = self.tree.identify_row(event.y)
            col = self.tree.identify_column(event.x)
            if row_id:
                value = self.tree.item(row_id, "values")[int(col[1:]) - 1]
                # 获取单元格的边界框，并加上偏移量来放置Tooltip
                x, y, w, h = self.tree.bbox(row_id, col)
                self.tooltip_label.config(text=value)
                # 使用 event.x_root 和 event.y_root 获取屏幕绝对位置
                self.tooltip.geometry(f"+{event.x_root + 10}+{event.y_root + 10}")
                self.tooltip.deiconify()
        else:
            self.tooltip.withdraw()

    # ====== 配置加载保存 ======
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

    # ====== LNK 查找 ======
    def select_custom_directory(self):
        path = filedialog.askdirectory(title="选择自定义扫描目录")
        if path:
            threading.Thread(target=self.find_lnk_files, args=(path,), daemon=True).start()

    def find_lnk_files(self, start_path):
        """递归扫描 LNK 文件"""
        self.status_label.config(text=f"正在扫描目录：{start_path} ...")
        self.tree.delete(*self.tree.get_children())
        self.lnk_files_to_process.clear()
        first_lnk_workdir = None # 记录第一个 LNK 文件的 WorkingDirectory

        for root, dirs, files in os.walk(start_path):
            
            # *** 需求修改点 2: 查找lnk文件时，忽略LNK_Backup文件夹。***
            # 在 os.walk 循环中修改 dirs 列表可以跳过特定目录
            # 注意：这里使用了一个更通用的模式来处理所有以 'LNK_Backup' 开头的文件夹，以匹配创建备份文件夹时的命名方式
            dirs[:] = [d for d in dirs if not d.lower().startswith("lnk_backup")]

            for file in files:
                if file.lower().endswith(".lnk"):
                    full_path = os.path.join(root, file)
                    self.lnk_files_to_process.append(full_path)
                    target, workdir = self.get_shortcut_info(full_path)
                    
                    # 记录第一个 LNK 文件的 WorkingDirectory
                    if first_lnk_workdir is None and workdir:
                        first_lnk_workdir = os.path.normpath(workdir)

                    self.tree.insert("", "end", values=(
                        file,
                        self.truncate_path(target),
                        self.truncate_path(workdir)
                    ))

        total = len(self.lnk_files_to_process)
        self.status_label.config(text=f"扫描完成，共找到 {total} 个 .lnk 文件")
        
        # *** 需求修改点 1: 将默认查找路径设置为第一个 LNK 文件属性中的“起始位置 (Working Directory)”，而不是 LNK 文件本身的父目录。***
        # 仅当查找输入框为空时才设置默认值
        if not self.find_path_entry.get():
             default_find_path = None

             if first_lnk_workdir:
                 # 使用第一个 LNK 文件的 Working Directory
                 default_find_path = first_lnk_workdir
                 message = f"已将 '查找路径片段' 默认设置为第一个 LNK 文件的起始位置 (Working Directory):\n{default_find_path}"
             elif start_path:
                 # 如果没有找到 Working Directory，退回到使用扫描根目录 (原逻辑)
                 default_find_path = os.path.normpath(start_path)
                 message = f"未找到有效的起始位置，已将 '查找路径片段' 默认设置为扫描目录: \n{default_find_path}"

             if default_find_path:
                 self.find_path_entry.insert(0, default_find_path)
                 messagebox.showinfo("提示", message)
             elif total == 0:
                 messagebox.showinfo("结果", "未找到任何 .lnk 文件。")
        elif total == 0:
            messagebox.showinfo("结果", "未找到任何 .lnk 文件。")
        else:
            messagebox.showinfo("扫描完成", f"共找到 {total} 个 .lnk 文件。")

    def truncate_path(self, path, max_len=50):
        """路径过长时自动省略显示"""
        if len(path) > max_len:
            return f"...{path[-max_len:]}"
        return path

    def get_shortcut_info(self, path):
        """获取 LNK 文件的 TargetPath 和 WorkingDirectory"""
        try:
            # 修复 COM 线程错误：初始化 COM
            pythoncom.CoInitialize()
            
            shell = win32com.client.Dispatch("WScript.Shell")
            shortcut = shell.CreateShortCut(path)
            # 使用 or "" 确保返回的是空字符串而不是 None
            return shortcut.TargetPath or "", shortcut.WorkingDirectory or ""
        except Exception:
            return "", ""
        finally:
            # 修复 COM 线程错误：取消初始化 COM
            # 确保在线程结束时释放资源
            pythoncom.CoUninitialize() 

    # ====== 路径替换 ======
    def apply_path_replacement(self, original, find, repl):
        if not find:
            return original
        return original.replace(find, repl)

    # ====== 预览修改 ======
    def preview_changes(self):
        if not self.lnk_files_to_process:
            messagebox.showwarning("请先扫描", "请先执行 '查找LNK文件'")
            return

        find_str = self.find_path_entry.get()
        replace_str = self.replace_path_entry.get()

        preview_window = tk.Toplevel(self.master)
        preview_window.title("预览修改结果")
        preview_window.geometry("1100x600")

        cols = ("文件名", "旧目标路径", "新目标路径", "旧工作目录", "新工作目录")
        tree = ttk.Treeview(preview_window, columns=cols, show="headings")
        for c in cols:
            tree.heading(c, text=c)
            tree.column(c, width=200)
        tree.pack(fill="both", expand=True)

        for lnk in self.lnk_files_to_process:
            old_target, old_work = self.get_shortcut_info(lnk)
            new_target = self.apply_path_replacement(old_target, find_str, replace_str)
            new_work = self.apply_path_replacement(old_work, find_str, replace_str)
            tree.insert("", "end", values=(os.path.basename(lnk),
                                             self.truncate_path(old_target),
                                             self.truncate_path(new_target),
                                             self.truncate_path(old_work),
                                             self.truncate_path(new_work)))

    # ====== 执行修改 ======
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

        # 创建备份
        backup_dir = f"LNK_Backup_{time.strftime('%Y%m%d_%H%M%S')}"
        os.makedirs(backup_dir, exist_ok=True)
        for lnk in self.lnk_files_to_process:
            try:
                # 复制到备份目录，保持文件名
                shutil.copy2(lnk, os.path.join(backup_dir, os.path.basename(lnk)))
            except Exception as e:
                print(f"备份文件失败：{lnk} -> {e}")

        # 修改路径
        modified_count = 0
        for lnk in self.lnk_files_to_process:
            try:
                pythoncom.CoInitialize()                 
                shell = win32com.client.Dispatch("WScript.Shell")
                sc = shell.CreateShortCut(lnk)
                
                # 预先保存旧值，用于检查是否发生了替换
                original_target = sc.TargetPath or ""
                original_workdir = sc.WorkingDirectory or ""

                new_target = original_target
                new_workdir = original_workdir
                
                # 替换目标路径
                if self.mode_var.get() in ("all", "target_only"):
                    new_target = self.apply_path_replacement(original_target, find_str, replace_str)
                
                # 替换起始位置
                if self.mode_var.get() in ("all", "working_dir_only"):
                    new_workdir = self.apply_path_replacement(original_workdir, find_str, replace_str)

                # 检查新目标路径是否存在（如果用户勾选了）
                if self.check_path_var.get() and self.mode_var.get() in ("all", "target_only"):
                    # os.path.exists() 可以检查文件或目录
                    if not os.path.exists(new_target):
                        # 如果新目标不存在，跳过本次修改，并提示
                        print(f"警告：新目标路径不存在，跳过修改 {lnk}: {new_target}")
                        continue # 跳过保存，进入下一个文件
                
                # 只有在路径有变化时才赋值和保存
                if new_target != original_target:
                    sc.TargetPath = new_target
                if new_workdir != original_workdir:
                    sc.WorkingDirectory = new_workdir

                # 检查是否有实际修改
                if (new_target != original_target) or (new_workdir != original_workdir):
                    sc.Save()
                    modified_count += 1

            except Exception as e:
                print(f"修改失败：{lnk} -> {e}")
            finally:
                # 修复 COM 线程错误：取消初始化 COM
                pythoncom.CoUninitialize()                

        messagebox.showinfo("完成", f"已成功修改 {modified_count} 个 LNK 文件并备份到 {backup_dir}。")
        
        # 重新加载列表以显示新值，并使用当前的起始目录（如果列表非空），否则使用当前工作目录
        scan_path = os.path.dirname(self.lnk_files_to_process[0]) if self.lnk_files_to_process else os.getcwd()
        threading.Thread(target=self.find_lnk_files, args=(scan_path,), daemon=True).start()


if __name__ == "__main__":
    root = tk.Tk()
    # 确保应用程序在主线程中运行
    app = LnkModifierApp(root)
    root.mainloop()
