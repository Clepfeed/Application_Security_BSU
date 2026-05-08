from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
import hashlib
import os

PASSWORD = "jndlasf074hr"
LOCAL_ENC_FILE = "test.jpg.enc"
LOCAL_DEC_FILE = "test.jpg"

def get_key(password):
    sha256 = hashlib.sha256()
    sha256.update(password.encode('utf-8'))
    return sha256.digest()

def decrypt_file(input_path, output_path):

    with open(input_path, 'rb') as f:
        encrypted_data = f.read()

    key = get_key(PASSWORD)
    iv = b'\x00' * 16  # Нулевой IV из Java-кода вируса
    
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

    with open(output_path, 'wb') as f:
        f.write(decrypted_data)
        
    print(f"Файл успешно расшифрован и сохранен как: {output_path}")

if __name__ == "__main__":
    decrypt_file(LOCAL_ENC_FILE, LOCAL_DEC_FILE)