import zipfile
import calendar
from datetime import datetime
import xml.etree.ElementTree as ET
import os

vfs_path = 'files.zip'
computer_name = 'MyComputer'
log_file = "log.xml"


def initialize_log():
    """Инициализирует log.xml, если он не существует."""
    if not os.path.exists(log_file):
        root = ET.Element("log")
        tree = ET.ElementTree(root)
        save_xml(tree)


def save_xml(tree):
    """Сохраняет XML, каждое действие на новой строке."""
    xml_str = ET.tostring(tree.getroot(), encoding="utf-8").decode("utf-8")
    xml_str = xml_str.replace("><", ">\n<")
    with open(log_file, "w", encoding="utf-8") as f:
        f.write(xml_str)


def log_action(command, parameters, result):
    """Логирует команду с результатом в log.xml."""
    try:
        if os.path.exists(log_file):
            try:
                tree = ET.parse(log_file)
                root = tree.getroot()
            except ET.ParseError:
                root = ET.Element("log")
                tree = ET.ElementTree(root)
        else:
            root = ET.Element("log")
            tree = ET.ElementTree(root)

        # Добавляем новую запись в лог
        action = ET.SubElement(root, "action")
        timestamp = ET.SubElement(action, "timestamp")
        timestamp.text = str(datetime.now())
        cmd = ET.SubElement(action, "command")
        cmd.text = command
        params = ET.SubElement(action, "parameters")
        params.text = str(parameters)
        result_elem = ET.SubElement(action, "result")
        result_elem.text = result
        save_xml(tree)

    except Exception as e:
        print(f"Error logging action: {str(e)}")

def read_zip():
    """Чтение всех файлов из архива в память."""
    with zipfile.ZipFile(vfs_path, 'r') as myzip:
        return myzip.namelist()

def write_zip(files_to_write):
    """Запись в архив."""
    with zipfile.ZipFile(vfs_path, 'w') as myzip:
        for file in files_to_write:
            myzip.write(file, arcname=file)

# Загружаем все файлы из архива в память
files_in_zip = read_zip()

current_dir = ''  # Начальная директория, пустая строка значит корень

initialize_log()  # Инициализация лог-файла

while True:
    command = input(f'{computer_name} {current_dir}$ ')

    if command == 'ls':
        try:
            unique_files = set()
            for name in files_in_zip:
                # Если имя начинается с текущей директории, это файл/папка в текущей директории
                if name.startswith(current_dir):
                    name_in_current_dir = name[len(current_dir):].split('/')[0]
                    if name_in_current_dir.strip():
                        unique_files.add(name_in_current_dir)
            # Выводим уникальные имена файлов и папок
            if unique_files:
                for file in unique_files:
                    print(file)
                log_action("ls", [], "Success")
            else:
                print("Нет файлов/папок в текущей директории.")
                log_action("ls", [], "No files/folders found")

        except Exception as e:
            log_action("ls", [], f"Error: {str(e)}")

    elif command.startswith('cd '):
        path = command.split()[1]
        try:
            if path == '-':
                # Переход в родительскую директорию
                if current_dir:
                    # Убираем последний уровень из пути
                    current_dir = '/'.join(current_dir.rstrip('/').split('/')[:-1]) + '/'
                    # Если путь пустой, мы находимся в корневой директории
                    if not current_dir or current_dir == "/":
                        current_dir = ''
                else:
                    print("Вы уже находитесь в корневой директории.")
                    log_action("cd", [path], "Already at root directory.")
            elif any(name.startswith(current_dir + path + '/') for name in files_in_zip):
                # Переход в подкаталог
                current_dir = current_dir + path + '/'
                log_action("cd", [path], "Success")
            else:
                print("Директория не найдена.")
                log_action("cd", [path], "Directory not found")
        except Exception as e:
            log_action("cd", [path], f"Error: {str(e)}")

    elif command == 'exit':
        log_action("exit", [], "Exit program")
        break

    elif command == 'cal':
        try:
            now = datetime.now()
            print(calendar.month(now.year, now.month))
            log_action("cal", [], "Success")
        except Exception as e:
            log_action("cal", [], f"Error: {str(e)}")

    elif command.startswith('rmdir '):
        try:
            dir_to_remove = command.split()[1]
            dir_path = current_dir + dir_to_remove + '/'
            # Проверка, пуста ли директория
            files_in_dir = [name for name in files_in_zip if name.startswith(dir_path)]
            if files_in_dir:
                print(f"Директория '{dir_to_remove}' не пуста.")
                log_action("rmdir", [dir_to_remove], "Directory not empty")
            else:
                # Создаем новый архив без этой директории
                files_to_keep = [file for file in files_in_zip if not file.startswith(dir_path)]
                # Перезаписываем архив без удаленной директории
                write_zip(files_to_keep)
                print(f"Директория '{dir_to_remove}' удалена.")
                # Обновляем список файлов в архиве
                files_in_zip = files_to_keep
                log_action("rmdir", [dir_to_remove], "Directory removed successfully")

        except Exception as e:
            log_action("rmdir", [dir_to_remove], f"Error: {str(e)}")

    else:
        print("Команда не найдена.")
        log_action(command, [], "Command not found")
