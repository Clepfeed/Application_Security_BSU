import os
import json
import zipfile
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

# Импортируем Windows-специфичные модули
import win32security
import win32api
import win32process

# WIN

def enable_privileges(): # Включаем привилегии менять права доступа
    try:
        priv_flags = win32security.TOKEN_ADJUST_PRIVILEGES | win32security.TOKEN_QUERY
        # Флаги которые хотим поменять у токена доступа (настройки процесса)
        # Сохраняем в priv_flags флаги на изменение привилегий и прочтение информации токена
        hToken = win32security.OpenProcessToken(win32api.GetCurrentProcess(), priv_flags)
        # Получаем наш токен для процесса приложения
        privilege_id = win32security.LookupPrivilegeValue(None, win32security.SE_RESTORE_NAME)
        # То что мы хотим выдать процессу
        win32security.AdjustTokenPrivileges(hToken, 0,[(privilege_id, win32security.SE_PRIVILEGE_ENABLED)])
        # Выдаём
    except Exception as e:
        print(f"Не удалось выдать привилегии. Запустите от имени Администратора. Ошибка: {e}")

def get_windows_acl(path: str) -> str: # Читаем значения у файлов и dir указанной dir и превращаем в SDDL 
    flags = win32security.OWNER_SECURITY_INFORMATION | \
            win32security.GROUP_SECURITY_INFORMATION | \
            win32security.DACL_SECURITY_INFORMATION
    
    sd = win32security.GetFileSecurity(path, flags)
    sddl = win32security.ConvertSecurityDescriptorToStringSecurityDescriptor(
        sd, win32security.SDDL_REVISION_1, flags
    )
    return sddl

def set_windows_acl(path: str, sddl: str): # Устанавливаем значения SDDL для папки / строки
    flags = win32security.OWNER_SECURITY_INFORMATION | \
            win32security.GROUP_SECURITY_INFORMATION | \
            win32security.DACL_SECURITY_INFORMATION
    
    sd = win32security.ConvertStringSecurityDescriptorToSecurityDescriptor(
        sddl, win32security.SDDL_REVISION_1
    )
    win32security.SetFileSecurity(path, flags, sd)

# Загрузка в архив

def pack_archive(target_path: str, archive_path: str): # Упаковка в архив с сохранением 
    metadata = {}
    parent_dir = os.path.dirname(target_path)

    with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        if os.path.isfile(target_path):
            # Если это один файл
            rel_path = os.path.relpath(target_path, parent_dir)
            zf.write(target_path, arcname=rel_path)
            metadata[rel_path] = {"type": "file", "sddl": get_windows_acl(target_path)}
        else:
            # Если это папка -- обходим рекурсивно
            for root, dirs, files in os.walk(target_path):
                # Сохраняем права для папок
                for d in dirs:
                    full_p = os.path.join(root, d)
                    rel_path = os.path.relpath(full_p, parent_dir).replace("\\", "/")
                    metadata[rel_path] = {"type": "dir", "sddl": get_windows_acl(full_p)}
                # Сохраняем права для файлов
                for f in files:
                    full_p = os.path.join(root, f)
                    rel_path = os.path.relpath(full_p, parent_dir).replace("\\", "/")
                    zf.write(full_p, arcname=rel_path)
                    metadata[rel_path] = {"type": "file", "sddl": get_windows_acl(full_p)}
            
            
            root_rel = os.path.basename(target_path)
            metadata[root_rel] = {"type": "dir", "sddl": get_windows_acl(target_path)}

        # Сохраняем метаданные в архив
        meta_json = json.dumps(metadata, indent=4)
        zf.writestr('metadata.json', meta_json)

# Распаковка архива

def unpack_archive(archive_path: str, extract_dir: str):
    enable_privileges() # Активируем права на восстановление владельца
    
    with zipfile.ZipFile(archive_path, 'r') as zf:
        # 1. Читаем метаданные
        if 'metadata.json' not in zf.namelist():
            raise Exception("Это не архив с бекапом (отсутствует metadata.json)")
        
        meta_json = zf.read('metadata.json').decode('utf-8')
        metadata = json.loads(meta_json)
        
        # 2. Извлекаем файлы
        members =[m for m in zf.namelist() if m != 'metadata.json']
        zf.extractall(path=extract_dir, members=members)
        
        # 3. Восстанавливаем права
        for rel_path, info in metadata.items():
            full_path = os.path.normpath(os.path.join(extract_dir, rel_path))
            
            if info["type"] == "dir" and not os.path.exists(full_path):
                os.makedirs(full_path, exist_ok=True)
                
            if os.path.exists(full_path):
                set_windows_acl(full_path, info["sddl"])

# GUI

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Менеджер Архивов")
        self.geometry("450x300")
        self.resizable(False, False)

        # Вкладки
        tab_control = ttk.Notebook(self)
        self.tab_pack = ttk.Frame(tab_control)
        self.tab_unpack = ttk.Frame(tab_control)
        tab_control.add(self.tab_pack, text='Запаковать')
        tab_control.add(self.tab_unpack, text='Распаковать')
        tab_control.pack(expand=1, fill="both")

        self._init_pack_tab()
        self._init_unpack_tab()

    def _init_pack_tab(self):
        # Элементы вкладки "Запаковать"
        tk.Label(self.tab_pack, text="Выберите, что будем сохранять:").pack(pady=(20, 5))
        
        btn_frame = tk.Frame(self.tab_pack)
        btn_frame.pack(pady=5)
        
        tk.Button(btn_frame, text="Выбрать Файл", command=lambda: self.pack_process('file'), width=15).pack(side=tk.LEFT, padx=10)
        tk.Button(btn_frame, text="Выбрать Папку", command=lambda: self.pack_process('dir'), width=15).pack(side=tk.LEFT, padx=10)

    def _init_unpack_tab(self):
        # Элементы вкладки "Распаковать"
        tk.Label(self.tab_unpack, text="Распаковка архива").pack(pady=(20, 5))
        tk.Button(self.tab_unpack, text="Выбрать архив и распаковать", command=self.unpack_process, width=30, height=2).pack(pady=10)

    def pack_process(self, mode):
        # 1. Выбор исходника
        if mode == 'file':
            target = filedialog.askopenfilename(title="Выберите файл")
        else:
            target = filedialog.askdirectory(title="Выберите папку")
            
        if not target: return

        # 2. Выбор куда сохранить архив
        archive_name = filedialog.asksaveasfilename(
            title="Сохранить архив как...", 
            defaultextension=".mysec",
            filetypes=[("Security Archive", "*.mysec"), ("All files", "*.*")]
        )
        if not archive_name: return

        # 3. Упаковка
        try:
            pack_archive(target, archive_name)
            messagebox.showinfo("Успех", f"Успешно сохранено в:\n{archive_name}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Произошла ошибка при упаковке:\n{str(e)}")

    def unpack_process(self):
        # 1. Выбор архива
        archive_path = filedialog.askopenfilename(
            title="Выберите архив .mysec",
            filetypes=[("Security Archive", "*.mysec"), ("All files", "*.*")]
        )
        if not archive_path: return

        # 2. Выбор папки для распаковки
        extract_dir = filedialog.askdirectory(title="Выберите папку для извлечения")
        if not extract_dir: return

        # 3. Распаковка
        try:
            unpack_archive(archive_path, extract_dir)
            messagebox.showinfo("Успех", "Файлы и их права доступа успешно восстановлены!")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Произошла ошибка при распаковке:\n{str(e)}")

if __name__ == "__main__":
    app = App()
    app.mainloop()