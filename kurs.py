import os
import time
import sys
import socket
import subprocess

results = []  # Список для хранения результатов

def log_result(message):
    """Добавляет сообщение в список результатов."""
    print(message)  # Выводим сообщение на экран
    results.append(message)  # Добавляем сообщение в список результатов

def check_internet_connection():
    """Проверка наличия соединения с Интернетом."""
    try:
        socket.create_connection(("8.8.8.8", 53), timeout=5)
        log_result("Интернет-соединение: Доступно")
    except OSError:
        log_result("Интернет-соединение: Недоступно")

def check_firewall_installed():
    """Проверка наличия установленного межсетевого экрана."""
    if os.name == 'nt':
        try:
            os.system('netsh advfirewall show allprofiles')
            log_result("Межсетевой экран установлен: Да")
        except subprocess.CalledProcessError:
            log_result("Межсетевой экран установлен: Нет или недоступен")
    else:
        log_result("Данная проверка поддерживается только на Windows.")

def check_firewall_status():
    """Проверка работоспособности межсетевого экрана."""
    if os.name == 'nt':
        try:
            result = subprocess.check_output('netsh advfirewall show allprofiles', shell=True, stderr=subprocess.STDOUT).decode('cp1251')
            profiles = ["Domain Profile", "Private Profile", "Public Profile"]
            all_on = True
            for profile in profiles:
                state_line = [line for line in result.split('\n') if profile in line]
                if state_line:
                    state = "ON" in state_line[0]
                    log_result(f"{profile}: {'Включен' if state else 'Выключен'}")
                    if not state:
                        all_on = False
            if all_on:
                log_result("Межсетевой экран работает: Да (все профили включены)")
            else:
                log_result("Межсетевой экран работает: Нет (не все профили включены)")
        except subprocess.CalledProcessError:
            log_result("Не удалось проверить статус межсетевого экрана.")
    else:
        log_result("Данная проверка поддерживается только на Windows.")

def check_antivirus_installed():
    """Проверка наличия установленного антивируса и его названия."""
    if os.name == 'nt':
        try:
            result = subprocess.check_output(
                'powershell "Get-CimInstance -Namespace root/SecurityCenter2 -ClassName AntivirusProduct | Select-Object displayName"', 
                shell=True, stderr=subprocess.STDOUT).decode('cp1251')

            antivirus_names = [line.strip() for line in result.split('\n') if line.strip() and 'displayName' not in line]
            if antivirus_names:
                log_result(f"Антивирус установлен: Да ({', '.join(antivirus_names)})")
                return True
            else:
                log_result("Антивирус установлен: Нет")
                return False
        except subprocess.CalledProcessError:
            log_result("Антивирус установлен: Нет или недоступен")
            return False
    else:
        log_result("Данная проверка поддерживается только на Windows.")
        return False

def check_antivirus_status():
    """Проверка работоспособности антивирусного ПО."""
    if os.name == 'nt':
        try:
            result = subprocess.check_output('powershell Get-MpComputerStatus', shell=True, stderr=subprocess.STDOUT).decode('cp1251')
            real_time = "RealTimeProtectionEnabled        : True" in result
            antivirus_running = "AMServiceEnabled                 : True" in result
            log_result(f"Антивирус работает (Real-Time Protection): {'Да' if real_time else 'Нет'}")
            log_result(f"Служба антивируса активна: {'Да' if antivirus_running else 'Нет'}")
            return real_time and antivirus_running
        except subprocess.CalledProcessError:
            log_result("Не удалось проверить статус антивирусного ПО.")
            return False
    else:
        log_result("Данная проверка поддерживается только на Windows.")
        return False

def test_antivirus_resident_module():
    """Тестирование антивирусного ПО с использованием тестового файла EICAR."""
    eicar_test_string = 'X5O!P%@AP[4\PZX54(P^)7CC)7}$EICAR-STANDARD-ANTIVIRUS-TEST-FILE!$H+H*'
    test_file_path = os.path.join(os.getcwd(), "eicar_test_file.txt")

    try:
        # Создание тестового файла
        with open(test_file_path, 'w') as file:
            file.write(eicar_test_string)
        log_result(f"Тестовый файл создан: {test_file_path}")
        subprocess.run(["notepad.exe", test_file_path])
        # Подождем немного, чтобы антивирус успел отреагировать
        log_result("Ожидание 20 секунд, чтобы антивирус мог проверить тестовый файл...")
        time.sleep(20)

        # Проверка, существует ли файл
        if not os.path.exists(test_file_path):
            log_result("Антивирус обнаружил и удалил тестовый файл: Тест пройден успешно.")
        else:
            log_result("Антивирус не обнаружил тестовый файл: Тест не пройден.")
            # Удалим файл вручную
            os.remove(test_file_path)
            log_result("Тестовый файл удален после проверки.")
    except Exception as e:
        log_result(f"Ошибка при тестировании антивируса: {e}")

def display_menu():
    """Отображение меню выбора функционала."""
    menu = """
    Выберите функционал:
    
    Проверка межсетевого экрана:
    1 - Проверка подключения к Интернету
    2 - Проверка наличия установленного межсетевого экрана
    3 - Проверка работоспособности межсетевого экрана
    
    Проверка антивирусного ПО:
    4 - Проверка наличия установленного антивируса (с выводом наименования)
    5 - Проверка работоспособности антивирусного ПО
    6 - Тестирование антивирусного ПО (резидентный модуль с использованием EICAR)
    
    0 - Выход
    """
    print(menu)

def display_results():
    """Вывод всех результатов в конце программы."""
    print("\nРезультаты проверок:")
    for result in results:
        print(result)

def main():
    while True:
        display_menu()
        try:
            choice = int(input("Введите номер выбранного пункта: "))
        except ValueError:
            log_result("Пожалуйста, введите числовое значение от 0 до 6.")
            continue

        if choice == 0:
            log_result("Выход из программы.")
            display_results()  # Выводим результаты перед выходом
            sys.exit()
        elif choice == 1:
            check_internet_connection()
        elif choice == 2:
            check_firewall_installed()
        elif choice == 3:
            check_firewall_status()
        elif choice == 4:
            check_antivirus_installed()
        elif choice == 5:
            check_antivirus_status()
        elif choice == 6:
            test_antivirus_resident_module()
        else:
            log_result("Неверный выбор. Пожалуйста, выберите число от 0 до 6.")
        
        input("\nНажмите Enter для продолжения...")
        display_results()  # Выводим результаты после каждого действия

if __name__ == "__main__":
    main()
