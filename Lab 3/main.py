import subprocess
import os
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
import hashlib

ADB_PATH = r"C:\Users\Clepfeed\AppData\Local\Android\Sdk\platform-tools\adb.exe"
PASSWORD = "jndlasf074hr"

REMOTE_ENC_FILE = "/sdcard/Download/test.jpg.enc"
REMOTE_DEC_FILE = "/sdcard/Download/test.jpg"

TEMP_ENC = "temp_enc.bin"
TEMP_DEC = "temp_dec.bin"

def get_key(password):
    sha256 = hashlib.sha256()
    sha256.update(password.encode('utf-8'))
    return sha256.digest()

def main():
    print("Запускаем ADB и скачиваем файл с эмулятора...")
    pull_result = subprocess.run([ADB_PATH, "pull", REMOTE_ENC_FILE, TEMP_ENC], capture_output=True, text=True)

    print("Расшифровываем файл...")
    with open(TEMP_ENC, 'rb') as f:
        encrypted_data = f.read()

    key = get_key(PASSWORD)
    iv = b'\x00' * 16 # Нулевой IV из Java-кода вируса
    cipher = AES.new(key, AES.MODE_CBC, iv)

    raw_decrypted = cipher.decrypt(encrypted_data)

    try:
        # Пытаемся снять паддинг
        decrypted_data = unpad(raw_decrypted, AES.block_size)
    except ValueError:
        # Если ловим ValueError, значит сработал баг Android 4.4, 
        # и блок с паддингом был утерян вирусом при шифровании. 
        # Просто используем сырые расшифрованные данные.
        print("Файл не содержит паддинга. Сохраняем сырые данные.")
        decrypted_data = raw_decrypted

    with open(TEMP_DEC, 'wb') as f:
        f.write(decrypted_data)

    print("Отправляем расшифрованную картинку обратно на устройство...")
    subprocess.run([ADB_PATH, "push", TEMP_DEC, REMOTE_DEC_FILE])

    print("Удаляем зашифрованный файл с телефона...")
    subprocess.run([ADB_PATH, "shell", "rm", REMOTE_ENC_FILE])

    print("Удаляем временные файлы с компьютера...")
    os.remove(TEMP_ENC)
    os.remove(TEMP_DEC)
    
    print("Успех!")

if __name__ == "__main__":
    main()