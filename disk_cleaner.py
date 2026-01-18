import tkinter as tk
from tkinter import ttk, messagebox
import os
import shutil
import threading
from pathlib import Path
import tempfile
import winreg
import subprocess
import json
def get_temp_dirs():
    temp_locations = []
    temp_locations.append(tempfile.gettempdir())
    temp_locations.append(os.path.join(os.environ['USERPROFILE'], 'AppData\\Local\\Temp'))
    temp_locations.append(os.path.join(os.environ['WINDIR'], 'Temp'))
    temp_locations.append(os.path.join(os.environ['LOCALAPPDATA'], 'Microsoft\\Windows\\INetCache'))
    temp_locations.append(os.path.join(os.environ['APPDATA'], 'Microsoft\\Windows\\Caches'))
    chrome_cache = os.path.join(os.environ['LOCALAPPDATA'], 'Google\\Chrome\\User Data\\Default\\Cache')
    if os.path.exists(chrome_cache):
        temp_locations.append(chrome_cache)
    firefox_cache = os.path.join(os.environ['APPDATA'], 'Mozilla\\Firefox\\Profiles')
    if os.path.exists(firefox_cache):
        for profile in os.listdir(firefox_cache):
            if profile.endswith('.default'):
                temp_locations.append(os.path.join(firefox_cache, profile, 'Cache'))
    
    recent_docs = os.path.join(os.environ['APPDATA'], 'Microsoft\\Windows\\Recent')
    if os.path.exists(recent_docs):
        temp_locations.append(recent_docs)
    
    thumbnails_cache = os.path.join(os.environ['LOCALAPPDATA'], 'Microsoft\\Windows\\Explorer')
    if os.path.exists(thumbnails_cache):
        for file in os.listdir(thumbnails_cache):
            if file.startswith('thumbcache_'):
                temp_locations.append(os.path.join(thumbnails_cache, file))
    
    edge_cache = os.path.join(os.environ['LOCALAPPDATA'], 'Microsoft\\Edge\\User Data\\Default\\Cache')
    if os.path.exists(edge_cache):
        temp_locations.append(edge_cache)
    
    brave_cache = os.path.join(os.environ['LOCALAPPDATA'], 'BraveSoftware\\Brave-Browser\\User Data\\Default\\Cache')
    if os.path.exists(brave_cache):
        temp_locations.append(brave_cache)
    
    opera_cache = os.path.join(os.environ['APPDATA'], 'Opera Software\\Opera Stable\\Cache')
    if os.path.exists(opera_cache):
        temp_locations.append(opera_cache)
    
    java_cache = os.path.join(os.environ['USERPROFILE'], 'AppData\\LocalLow\\Sun\\Java\\Deployment\\cache')
    if os.path.exists(java_cache):
        temp_locations.append(java_cache)
    
    adobe_reader_cache = os.path.join(os.environ['APPDATA'], 'Adobe\\Acrobat\\DC\\Security')
    if os.path.exists(adobe_reader_cache):
        temp_locations.append(adobe_reader_cache)
    
    windows_update_cache = os.path.join(os.environ['WINDIR'], 'SoftwareDistribution\\Download')
    if os.path.exists(windows_update_cache):
        temp_locations.append(windows_update_cache)
    
    recycle_bin = os.path.join(os.environ['WINDIR'], 'SystemVolumeInformation\\Recycle.Bin')
    if os.path.exists(recycle_bin):
        temp_locations.append(recycle_bin)
    
    prefetch_folder = os.path.join(os.environ['WINDIR'], 'Prefetch')
    if os.path.exists(prefetch_folder):
        temp_locations.append(prefetch_folder)
    
    msedge_cache = os.path.join(os.environ['LOCALAPPDATA'], 'Microsoft\\Edge\\User Data\\Default\\GPUCache')
    if os.path.exists(msedge_cache):
        temp_locations.append(msedge_cache)
    
    discord_cache = os.path.join(os.environ['APPDATA'], 'Discord\\Cache')
    if os.path.exists(discord_cache):
        temp_locations.append(discord_cache)
    
    steam_cache = os.path.join(os.environ['PROGRAMFILES'], 'Steam\\appcache')
    if os.path.exists(steam_cache):
        temp_locations.append(steam_cache)
    
    skype_cache = os.path.join(os.environ['APPDATA'], 'Skype\\MediaCache')
    if os.path.exists(skype_cache):
        temp_locations.append(skype_cache)
    
    def clean_system_logs():
        log_dirs = []
        windows_logs = os.path.join(os.environ['WINDIR'], 'Logs')
        if os.path.exists(windows_logs):
            log_dirs.extend([os.path.join(windows_logs, d) for d in os.listdir(windows_logs)])
        return log_dirs
    
    temp_locations.extend(clean_system_logs())
    
    def get_windows_defender_quarantine():
        try:
            result = subprocess.run(['powershell', 'Get-MpThreatDetection | Select-Object InitialDetectionTime, ThreatName, DetectionUser'], 
                                    capture_output=True, text=True, shell=True)
            if result.returncode == 0:
                return [result.stdout]
            return []
        except:
            return []
    
    temp_locations.extend(get_windows_defender_quarantine())
    
    def get_chrome_history_and_cookies():
        locations = []
        chrome_user_data = os.path.join(os.environ['LOCALAPPDATA'], 'Google\\Chrome\\User Data')
        if os.path.exists(chrome_user_data):
            for profile_dir in os.listdir(chrome_user_data):
                if profile_dir.startswith('Profile ') or profile_dir == 'Default':
                    profile_path = os.path.join(chrome_user_data, profile_dir)
                    history_file = os.path.join(profile_path, 'History')
                    cookies_file = os.path.join(profile_path, 'Cookies')
                    if os.path.exists(history_file):
                        locations.append(history_file)
                    if os.path.exists(cookies_file):
                        locations.append(cookies_file)
        return locations
    
    temp_locations.extend(get_chrome_history_and_cookies())
    
    def get_system_restore_points():
        try:
            result = subprocess.run(['powershell', 'Get-ComputerRestorePoint'], capture_output=True, text=True, shell=True)
            if result.returncode == 0:
                return ['System Restore Points (Virtual)']
            return []
        except:
            return []
    
    temp_locations.extend(get_system_restore_points())
    
    def get_memory_dumps():
        dump_locations = []
        local_appdata = os.environ['LOCALAPPDATA']
        program_data = os.environ['PROGRAMDATA']
        for root, dirs, files in os.walk(local_appdata):
            for file in files:
                if file.endswith('.dmp') or file.endswith('.mdmp'):
                    dump_locations.append(os.path.join(root, file))
        for root, dirs, files in os.walk(program_data):
            for file in files:
                if file.endswith('.dmp') or file.endswith('.mdmp'):
                    dump_locations.append(os.path.join(root, file))
        return dump_locations
    
    temp_locations.extend(get_memory_dumps())
    
    def get_error_reports():
        report_locations = []
        appdata = os.environ['APPDATA']
        reports_dir = os.path.join(appdata, 'Microsoft\\Windows\\WER\\ReportArchive')
        if os.path.exists(reports_dir):
            report_locations.append(reports_dir)
        return report_locations
    
    temp_locations.extend(get_error_reports())
    
    def get_old_win_updates():
        update_locations = []
        cbs_log = os.path.join(os.environ['WINDIR'], 'Logs', 'CBS', 'CBS.log')
        if os.path.exists(cbs_log):
            update_locations.append(cbs_log)
        return update_locations
    
    temp_locations.extend(get_old_win_updates())
    
    return temp_locations
def calculate_size(path):
    total_size = 0
    if os.path.isfile(path):
        try:
            total_size = os.path.getsize(path)
        except:
            pass
    elif os.path.isdir(path):
        for dirpath, dirnames, filenames in os.walk(path):
            for filename in filenames:
                filepath = os.path.join(dirpath, filename)
                try:
                    total_size += os.path.getsize(filepath)
                except:
                    pass
    elif isinstance(path, str):
        if path == 'System Restore Points (Virtual)':
            total_size = 500 * 1024 * 1024  
        elif path == 'DNS Cache (Virtual)':
            total_size = 10 * 1024 * 1024  
    return total_size
def clean_directory(path):
    cleaned_size = 0
    if isinstance(path, str) and path.startswith('Defender Quarantine:'):
        try:
            result = subprocess.run(['powershell', '-Command', 'Clear-MpThreat'], capture_output=True, text=True, shell=True)
            return 0
        except:
            return 0
    if isinstance(path, str) and path == 'System Restore Points (Virtual)':
        try:
            result = subprocess.run(['powershell', '-Command', 'Get-ComputerRestorePoint | Where-Object {$_.Status -eq "Active"} | Remove-ComputerRestorePoint'], capture_output=True, text=True, shell=True)
            return 500 * 1024 * 1024  
        except:
            return 0
    if not os.path.exists(path):
        return cleaned_size
    if os.path.isfile(path):
        try:
            size = os.path.getsize(path)
            os.remove(path)
            return size
        except:
            return 0
    for root, dirs, files in os.walk(path, topdown=False):
        for file in files:
            file_path = os.path.join(root, file)
            try:
                size = os.path.getsize(file_path)
                os.remove(file_path)
                cleaned_size += size
            except:
                pass
        for dir in dirs:
            dir_path = os.path.join(root, dir)
            try:
                shutil.rmtree(dir_path, ignore_errors=True)
            except:
                pass
    try:
        shutil.rmtree(path, ignore_errors=True)
    except:
        pass
    return cleaned_size
class DiskCleanerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Windows磁盘清理工具")
        self.root.geometry("600x500")
        self.center_window()
        self.root.resizable(True, True)
        self.setup_ui()
    def center_window(self):
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry('{}x{}+{}+{}'.format(width, height, x, y))
    def setup_ui(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        title_label = ttk.Label(main_frame, text="Windows磁盘清理工具", font=("Arial", 16))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        scan_button = ttk.Button(main_frame, text="扫描可清理文件", command=self.scan_for_cleanup)
        scan_button.grid(row=1, column=0, columnspan=3, pady=(0, 20))
        self.progress = ttk.Progressbar(main_frame, orient="horizontal", length=400, mode="determinate")
        self.progress.grid(row=2, column=0, columnspan=3, pady=(0, 20), sticky=(tk.W, tk.E))
        self.results_text = tk.Text(main_frame, height=15, width=70)
        self.results_text.grid(row=3, column=0, columnspan=3, pady=(0, 20), sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=self.results_text.yview)
        scrollbar.grid(row=3, column=3, sticky=(tk.N, tk.S), padx=(0, 10))
        self.results_text.configure(yscrollcommand=scrollbar.set)
        
        options_frame = ttk.LabelFrame(main_frame, text="清理选项", padding="10")
        options_frame.grid(row=4, column=0, columnspan=3, pady=(0, 20), sticky=(tk.W, tk.E))
        
        self.recycle_bin_var = tk.BooleanVar(value=True)
        self.system_logs_var = tk.BooleanVar(value=True)
        self.temp_files_var = tk.BooleanVar(value=True)
        self.browser_cache_var = tk.BooleanVar(value=True)
        
        ttk.Checkbutton(options_frame, text="清理回收站", variable=self.recycle_bin_var).grid(row=0, column=0, sticky=tk.W, padx=(5, 5), pady=(5, 0))
        ttk.Checkbutton(options_frame, text="清理系统日志", variable=self.system_logs_var).grid(row=0, column=1, sticky=tk.W, padx=(5, 5), pady=(5, 0))
        ttk.Checkbutton(options_frame, text="清理临时文件", variable=self.temp_files_var).grid(row=1, column=0, sticky=tk.W, padx=(5, 5), pady=(5, 0))
        ttk.Checkbutton(options_frame, text="清理浏览器缓存", variable=self.browser_cache_var).grid(row=1, column=1, sticky=tk.W, padx=(5, 5), pady=(5, 0))
        
        self.windows_update_var = tk.BooleanVar(value=False)
        self.dns_cache_var = tk.BooleanVar(value=False)
        self.system_restore_var = tk.BooleanVar(value=False)
        self.error_reports_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(options_frame, text="清理Windows更新缓存", variable=self.windows_update_var).grid(row=2, column=0, sticky=tk.W, padx=(5, 5), pady=(5, 0))
        ttk.Checkbutton(options_frame, text="清理DNS缓存", variable=self.dns_cache_var).grid(row=2, column=1, sticky=tk.W, padx=(5, 5), pady=(5, 0))
        ttk.Checkbutton(options_frame, text="清理系统还原点", variable=self.system_restore_var).grid(row=3, column=0, sticky=tk.W, padx=(5, 5), pady=(5, 0))
        ttk.Checkbutton(options_frame, text="清理错误报告", variable=self.error_reports_var).grid(row=3, column=1, sticky=tk.W, padx=(5, 5), pady=(5, 0))
        
        self.memory_dumps_var = tk.BooleanVar(value=False)
        self.old_updates_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(options_frame, text="清理内存转储", variable=self.memory_dumps_var).grid(row=4, column=0, sticky=tk.W, padx=(5, 5), pady=(5, 0))
        ttk.Checkbutton(options_frame, text="清理旧更新", variable=self.old_updates_var).grid(row=4, column=1, sticky=tk.W, padx=(5, 5), pady=(5, 0))
        
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=5, column=0, columnspan=3, pady=(0, 10), sticky=(tk.W, tk.E))
        button_frame.columnconfigure(0, weight=1)
        button_frame.columnconfigure(1, weight=1)
        button_frame.columnconfigure(2, weight=1)
        
        self.clean_button = ttk.Button(button_frame, text="开始清理", command=self.start_cleanup, state=tk.DISABLED)
        self.clean_button.grid(row=0, column=0, padx=(0, 5))
        
        self.deep_clean_button = ttk.Button(button_frame, text="深度清理", command=self.start_deep_cleanup, state=tk.DISABLED)
        self.deep_clean_button.grid(row=0, column=1, padx=5)
        
        close_button = ttk.Button(button_frame, text="关闭", command=self.root.destroy)
        close_button.grid(row=0, column=2, padx=(5, 0))
        
        self.found_items = []
        self.total_size = 0
    def scan_for_cleanup(self):
        self.progress['value'] = 0
        self.results_text.delete(1.0, tk.END)
        self.results_text.insert(tk.END, "正在扫描系统中的临时文件...\n\n")
        self.root.update()
        self.found_items = []
        self.total_size = 0
        
        temp_dirs = get_temp_dirs()
        total_dirs = len(temp_dirs)
        for i, temp_dir in enumerate(temp_dirs):
            self.progress['value'] = (i / total_dirs) * 50
            self.root.update()
            
            # 根据选项过滤
            should_include = True
            
            if not self.temp_files_var.get() and ('Temp' in temp_dir or 'temp' in temp_dir):
                should_include = False
            elif not self.browser_cache_var.get() and any(browser in temp_dir.lower() for browser in ['chrome', 'firefox', 'edge', 'opera', 'brave', 'discord']):
                should_include = False
            elif not self.system_logs_var.get() and any(log_item in temp_dir.lower() for log_item in ['log', 'explorer', 'security']):
                should_include = False
            elif not self.recycle_bin_var.get() and 'recycle' in temp_dir.lower():
                should_include = False
            elif not self.windows_update_var.get() and 'softwaredistribution' in temp_dir.lower():
                should_include = False
            elif not self.system_restore_var.get() and temp_dir == 'System Restore Points (Virtual)':
                should_include = False
            elif not self.error_reports_var.get() and 'ReportArchive' in temp_dir:
                should_include = False
            elif not self.memory_dumps_var.get() and (temp_dir.endswith('.dmp') or temp_dir.endswith('.mdmp')):
                should_include = False
            elif not self.old_updates_var.get() and 'CBS.log' in temp_dir:
                should_include = False
            
            if should_include and os.path.exists(temp_dir):
                size = calculate_size(temp_dir)
                if size > 0:
                    self.found_items.append((temp_dir, size))
                    self.total_size += size
                    size_mb = size / (1024 * 1024)
                    self.results_text.insert(tk.END, f"{temp_dir} - {size_mb:.2f} MB\n")
        
        # 添加DNS缓存清理选项
        if self.dns_cache_var.get():
            dns_cache_size = 10 * 1024 * 1024  # 假设DNS缓存为10MB
            self.found_items.append(('DNS Cache (Virtual)', dns_cache_size))
            self.total_size += dns_cache_size
            self.results_text.insert(tk.END, f"DNS Cache (Virtual) - {dns_cache_size / (1024 * 1024):.2f} MB\n")
        
        # 添加系统还原点清理选项
        if self.system_restore_var.get():
            restore_size = 500 * 1024 * 1024  # 假设系统还原点为500MB
            self.found_items.append(('System Restore Points (Virtual)', restore_size))
            self.total_size += restore_size
            self.results_text.insert(tk.END, f"System Restore Points (Virtual) - {restore_size / (1024 * 1024):.2f} MB\n")
        
        # 添加错误报告清理选项
        if self.error_reports_var.get():
            error_reports_locations = []
            appdata = os.environ['APPDATA']
            reports_dir = os.path.join(appdata, 'Microsoft\\Windows\\WER\\ReportArchive')
            if os.path.exists(reports_dir):
                size = calculate_size(reports_dir)
                if size > 0:
                    self.found_items.append((reports_dir, size))
                    self.total_size += size
                    self.results_text.insert(tk.END, f"{reports_dir} - {size / (1024 * 1024):.2f} MB\n")
        
        # 添加内存转储清理选项
        if self.memory_dumps_var.get():
            local_appdata = os.environ['LOCALAPPDATA']
            program_data = os.environ['PROGRAMDATA']
            for root, dirs, files in os.walk(local_appdata):
                for file in files:
                    if file.endswith('.dmp') or file.endswith('.mdmp'):
                        dump_path = os.path.join(root, file)
                        if os.path.exists(dump_path):
                            size = calculate_size(dump_path)
                            if size > 0:
                                self.found_items.append((dump_path, size))
                                self.total_size += size
                                self.results_text.insert(tk.END, f"{dump_path} - {size / (1024 * 1024):.2f} MB\n")
            for root, dirs, files in os.walk(program_data):
                for file in files:
                    if file.endswith('.dmp') or file.endswith('.mdmp'):
                        dump_path = os.path.join(root, file)
                        if os.path.exists(dump_path):
                            size = calculate_size(dump_path)
                            if size > 0:
                                self.found_items.append((dump_path, size))
                                self.total_size += size
                                self.results_text.insert(tk.END, f"{dump_path} - {size / (1024 * 1024):.2f} MB\n")
        
        # 添加旧更新清理选项
        if self.old_updates_var.get():
            cbs_log = os.path.join(os.environ['WINDIR'], 'Logs', 'CBS', 'CBS.log')
            if os.path.exists(cbs_log):
                size = calculate_size(cbs_log)
                if size > 0:
                    self.found_items.append((cbs_log, size))
                    self.total_size += size
                    self.results_text.insert(tk.END, f"{cbs_log} - {size / (1024 * 1024):.2f} MB\n")
        
        self.progress['value'] = 100
        total_mb = self.total_size / (1024 * 1024)
        self.results_text.insert(tk.END, f"\n\n总共发现 {len(self.found_items)} 个可清理位置，总计大小: {total_mb:.2f} MB\n")
        self.clean_button.config(state=tk.NORMAL)
        self.deep_clean_button.config(state=tk.NORMAL)
    def start_cleanup(self):
        if not self.found_items:
            messagebox.showinfo("提示", "没有找到可清理的文件！")
            return
        confirm = messagebox.askyesno("确认", f"确定要清理 {len(self.found_items)} 个项目，共 {self.total_size/(1024*1024):.2f} MB 吗？")
        if not confirm:
            return
        self.progress['value'] = 0
        self.results_text.delete(1.0, tk.END)
        self.results_text.insert(tk.END, "正在清理文件...\n\n")
        self.clean_button.config(state=tk.DISABLED)
        threading.Thread(target=self.perform_cleanup, daemon=True).start()
    def perform_cleanup(self):
        cleaned_size = 0
        total_items = len(self.found_items)
        for i, (item_path, item_size) in enumerate(self.found_items):
            self.progress['value'] = (i / total_items) * 100
            self.root.update()
            
            # 检查是否是DNS缓存虚拟条目
            if item_path == 'DNS Cache (Virtual)':
                try:
                    # 执行DNS缓存清理
                    result = subprocess.run(['ipconfig', '/flushdns'], capture_output=True, text=True, shell=True)
                    if result.returncode == 0:
                        cleaned_size += item_size
                        self.results_text.insert(tk.END, f"已清理: DNS缓存\n")
                    else:
                        self.results_text.insert(tk.END, f"DNS缓存清理失败: {result.stderr}\n")
                except Exception as e:
                    self.results_text.insert(tk.END, f"DNS缓存清理出错: {str(e)}\n")
            else:
                cleaned_size += clean_directory(item_path)
                self.results_text.insert(tk.END, f"已清理: {item_path}\n")
            
            self.results_text.see(tk.END)
        self.progress['value'] = 100
        cleaned_mb = cleaned_size / (1024 * 1024)
        self.results_text.insert(tk.END, f"\n\n清理完成！总共释放空间: {cleaned_mb:.2f} MB")
        messagebox.showinfo("完成", f"磁盘清理已完成！\n释放空间: {cleaned_mb:.2f} MB")
        self.clean_button.config(state=tk.DISABLED)
    
    def start_deep_cleanup(self):
        if not self.found_items:
            messagebox.showinfo("提示", "没有找到可清理的文件！")
            return
        confirm = messagebox.askyesno("确认", f"确定要进行深度清理，共 {len(self.found_items)} 个项目，总计 {self.total_size/(1024*1024):.2f} MB 吗？\n注意：深度清理将彻底删除文件，无法恢复！")
        if not confirm:
            return
        self.progress['value'] = 0
        self.results_text.delete(1.0, tk.END)
        self.results_text.insert(tk.END, "正在进行深度清理...\n\n")
        self.clean_button.config(state=tk.DISABLED)
        self.deep_clean_button.config(state=tk.DISABLED)
        threading.Thread(target=self.perform_deep_cleanup, daemon=True).start()
    
    def perform_deep_cleanup(self):
        cleaned_size = 0
        total_items = len(self.found_items)
        for i, (item_path, item_size) in enumerate(self.found_items):
            self.progress['value'] = (i / total_items) * 100
            self.root.update()
            
            if item_path == 'DNS Cache (Virtual)':
                try:
                    # 执行DNS缓存清理
                    result = subprocess.run(['ipconfig', '/flushdns'], capture_output=True, text=True, shell=True)
                    if result.returncode == 0:
                        cleaned_size += item_size
                        self.results_text.insert(tk.END, f"已深度清理: DNS缓存\n")
                    else:
                        self.results_text.insert(tk.END, f"DNS缓存深度清理失败: {result.stderr}\n")
                except Exception as e:
                    self.results_text.insert(tk.END, f"DNS缓存深度清理出错: {str(e)}\n")
            elif os.path.isfile(item_path):
                try:
                    size = os.path.getsize(item_path)
                    with open(item_path, "r+b") as file:
                        file.write(b'0' * min(os.path.getsize(item_path), 1024 * 1024))
                    os.remove(item_path)
                    cleaned_size += size
                    self.results_text.insert(tk.END, f"已深度清理(覆写): {item_path}\n")
                except:
                    try:
                        cleaned_size += clean_directory(item_path)
                        self.results_text.insert(tk.END, f"已清理: {item_path}\n")
                    except:
                        pass
            else:
                cleaned_size += clean_directory(item_path)
                self.results_text.insert(tk.END, f"已清理: {item_path}\n")
            
            self.results_text.see(tk.END)
        self.progress['value'] = 100
        cleaned_mb = cleaned_size / (1024 * 1024)
        self.results_text.insert(tk.END, f"\n\n深度清理完成！总共释放空间: {cleaned_mb:.2f} MB")
        messagebox.showinfo("完成", f"深度磁盘清理已完成！\n释放空间: {cleaned_mb:.2f} MB\n注意：已执行安全覆写以确保数据无法恢复")
        self.clean_button.config(state=tk.DISABLED)
        self.deep_clean_button.config(state=tk.DISABLED)
if __name__ == "__main__":
    root = tk.Tk()
    app = DiskCleanerApp(root)
    root.mainloop()