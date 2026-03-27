import tkinter as tk
from tkinter import messagebox
import requests
import os

SERVER_URL = "https://localhost:4433/api/match"
CERT_PATH = "certificate/server.crt" 

BG_APP = "#0b1711"
BG_CONTAINER = "#15291e"
BG_INPUT = "#112219"
COLOR_TEXT_PRIMARY = "#e2f5e6"
COLOR_TEXT_SEC = "#8dae98"
COLOR_ACCENT = "#285e3f"
COLOR_ACCENT_HOVER = "#357a52"
COLOR_SUCCESS = "#55a873"
COLOR_ERROR = "#cc6666"
COLOR_BORDER = "#1e3b2b"

FONT_TITLE = ("Segoe UI", 16, "bold")
FONT_LABEL = ("Segoe UI", 10, "bold")
FONT_INPUT = ("Segoe UI", 11)


def fetch_data():
    date = entry_date.get().strip()
    team = entry_team.get().strip()

    if not date or not team:
        messagebox.showwarning("Ошибка", "Пожалуйста, введите дату и название команды")
        return

    # Очищаем список игроков и сбрасываем статус
    listbox_players.delete(0, tk.END)
    lbl_status.config(text="Подключение к серверу...", fg=COLOR_TEXT_SEC)
    root.update()

    # Проверяем, на месте ли зашитый сертификат
    if not os.path.exists(CERT_PATH):
        lbl_status.config(text="КРИТИЧЕСКАЯ ОШИБКА: Сертификат не найден в приложении", fg=COLOR_ERROR)
        return

    try:
        # Параметр verify=CERT_PATH заставляет Python доверять только этому файлу.
        # Если сервер пришлет invalid.crt, произойдет ошибка SSLError.
        response = requests.get(
            SERVER_URL, 
            params={'date': date, 'team': team}, 
            verify=CERT_PATH,
            timeout=5
        )

        # Если данные найдены
        if response.status_code == 200:
            match_data = response.json()
            lbl_status.config(text="Успех: Данные защищены и проверены", fg=COLOR_SUCCESS)
            
            # Выводим игроков в интерфейс
            players = match_data.get('players',[])
            for i, player in enumerate(players, 1):
                listbox_players.insert(tk.END, f"{i}. {player}")
                
        # Если такого файла нет на сервере
        elif response.status_code == 404:
            lbl_status.config(text="Ошибка: Матч не найден на сервере.", fg="#d4a373")
            
        else:
            lbl_status.config(text=f"Ошибка сервера: {response.status_code}", fg=COLOR_ERROR)

    except requests.exceptions.SSLError as e:
        # Если сертификат не сошёлся
        error_msg = "ОШИБКА БЕЗОПАСНОСТИ!\nПодлинность сервера не подтверждена!\nВозможен перехват трафика (MitM)."
        lbl_status.config(text="СОЕДИНЕНИЕ РАЗОРВАНО (Неверный сертификат)", fg=COLOR_ERROR)
        messagebox.showerror("Критическая уязвимость", error_msg)
        print(f"[SECURITY ALERT] Попытка подмены сертификата: {e}")

    except requests.exceptions.ConnectionError:
        lbl_status.config(text="Ошибка: Сервер недоступен", fg=COLOR_ERROR)
    except Exception as e:
        lbl_status.config(text="Неизвестная ошибка", fg=COLOR_ERROR)
        print(e)

# --- ГРАФИЧЕСКИЙ ИНТЕРФЕЙС (Tkinter в стиле Dark Forest) ---
root = tk.Tk()
root.title("Клиент: Заявка на матч")
root.geometry("480x580")
root.config(bg=BG_APP) # Устанавливаем цвет фона самого окна

# Создаем главный контейнер (имитация .container из CSS)
main_frame = tk.Frame(root, bg=BG_CONTAINER, bd=0, highlightthickness=1, highlightbackground=COLOR_BORDER)
main_frame.pack(fill=tk.BOTH, expand=True, padx=25, pady=30)

# Верхняя зеленая полоска (декор, как в CSS border-top)
top_border = tk.Frame(main_frame, bg=COLOR_ACCENT, height=6)
top_border.pack(fill=tk.X, side=tk.TOP)

# Внутренний отступ для контента
content_frame = tk.Frame(main_frame, bg=BG_CONTAINER, padx=25, pady=20)
content_frame.pack(fill=tk.BOTH, expand=True)

# Заголовок
tk.Label(content_frame, text="ЗАПРОС СОСТАВА", font=FONT_TITLE, bg=BG_CONTAINER, fg=COLOR_TEXT_PRIMARY).pack(pady=(0, 5))
tk.Label(content_frame, text="Безопасное получение данных о матче", font=("Segoe UI", 10), bg=BG_CONTAINER, fg=COLOR_TEXT_SEC).pack(pady=(0, 20))

# Блок полей ввода
frame_inputs = tk.Frame(content_frame, bg=BG_CONTAINER)
frame_inputs.pack(fill=tk.X, pady=5)

# Поле: Дата
tk.Label(frame_inputs, text="ДАТА (YYYY-MM-DD):", font=FONT_LABEL, bg=BG_CONTAINER, fg=COLOR_TEXT_SEC).grid(row=0, column=0, sticky="w", pady=10)
entry_date = tk.Entry(frame_inputs, font=FONT_INPUT, bg=BG_INPUT, fg=COLOR_TEXT_PRIMARY, 
                      insertbackground=COLOR_TEXT_PRIMARY, # Цвет курсора
                      relief="flat", highlightthickness=1, highlightbackground=COLOR_BORDER, highlightcolor=COLOR_SUCCESS)
entry_date.grid(row=0, column=1, padx=(10, 0), pady=10, ipady=4, sticky="ew")
entry_date.insert(0, "2026-03-27")

# Поле: Команда
tk.Label(frame_inputs, text="КОМАНДА:", font=FONT_LABEL, bg=BG_CONTAINER, fg=COLOR_TEXT_SEC).grid(row=1, column=0, sticky="w", pady=10)
entry_team = tk.Entry(frame_inputs, font=FONT_INPUT, bg=BG_INPUT, fg=COLOR_TEXT_PRIMARY, 
                      insertbackground=COLOR_TEXT_PRIMARY, 
                      relief="flat", highlightthickness=1, highlightbackground=COLOR_BORDER, highlightcolor=COLOR_SUCCESS)
entry_team.grid(row=1, column=1, padx=(10, 0), pady=10, ipady=4, sticky="ew")
entry_team.insert(0, "GSW")

frame_inputs.columnconfigure(1, weight=1) # Растягиваем поля ввода

# Кнопка
btn_fetch = tk.Button(content_frame, text="ЗАПРОСИТЬ ДАННЫЕ", font=("Segoe UI", 11, "bold"), 
                      bg=COLOR_ACCENT, fg=COLOR_TEXT_PRIMARY, 
                      activebackground=COLOR_ACCENT_HOVER, activeforeground=COLOR_TEXT_PRIMARY,
                      relief="flat", borderwidth=0, cursor="hand2", command=fetch_data)
btn_fetch.pack(fill=tk.X, pady=20, ipady=6)

# Статус
lbl_status = tk.Label(content_frame, text="Готов к отправке запроса...", font=("Segoe UI", 10, "italic"), bg=BG_CONTAINER, fg=COLOR_TEXT_SEC)
lbl_status.pack(pady=(0, 10))

# Секция со списком игроков
tk.Label(content_frame, text="ЗАЯВЛЕННЫЕ ИГРОКИ:", font=FONT_LABEL, bg=BG_CONTAINER, fg=COLOR_TEXT_SEC).pack(anchor="w")

# Список
listbox_players = tk.Listbox(content_frame, font=FONT_INPUT, bg=BG_INPUT, fg=COLOR_SUCCESS, 
                             selectbackground=COLOR_ACCENT, selectforeground=COLOR_TEXT_PRIMARY,
                             relief="flat", highlightthickness=1, highlightbackground=COLOR_BORDER)
listbox_players.pack(fill=tk.BOTH, expand=True, pady=(5, 0))

root.mainloop()



























# # --- ГРАФИЧЕСКИЙ ИНТЕРФЕЙС (Tkinter) ---
# root = tk.Tk()
# root.title("Клиент: Просмотр заявок на матч")
# root.geometry("450x500")
# root.config(padx=20, pady=20)

# # Заголовок
# tk.Label(root, text="Поиск состава команды", font=("Arial", 16, "bold")).pack(pady=(0, 15))

# # Поля ввода
# frame_inputs = tk.Frame(root)
# frame_inputs.pack(fill=tk.X, pady=5)

# tk.Label(frame_inputs, text="Дата (YYYY-MM-DD):").grid(row=0, column=0, sticky="w", pady=5)
# entry_date = tk.Entry(frame_inputs, width=25)
# entry_date.grid(row=0, column=1, padx=10, pady=5)
# entry_date.insert(0, "2006-04-30")

# tk.Label(frame_inputs, text="Команда:").grid(row=1, column=0, sticky="w", pady=5)
# entry_team = tk.Entry(frame_inputs, width=25)
# entry_team.grid(row=1, column=1, padx=10, pady=5)
# entry_team.insert(0, "Golden State Warriors")

# btn_fetch = tk.Button(root, text="Скачать данные", bg="#4CAF50", fg="black", font=("Arial", 12), command=fetch_data)
# btn_fetch.pack(fill=tk.X, pady=15)

# lbl_status = tk.Label(root, text="Ожидание действий...", font=("Arial", 10, "bold"), fg="gray")
# lbl_status.pack(pady=5)

# tk.Label(root, text="Заявленные игроки:").pack(anchor="w")
# listbox_players = tk.Listbox(root, font=("Arial", 12), height=10)
# listbox_players.pack(fill=tk.BOTH, expand=True, pady=5)

# root.mainloop()