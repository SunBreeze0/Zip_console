import zipfile
import calendar
from datetime import datetime

vfs_path = 'files.zip'


# Чтение всех файлов из архива
def read_zip():
    with zipfile.ZipFile(vfs_path, 'r') as myzip:
        return myzip.namelist()


# Запись в архив
def write_zip(files_to_write):
    with zipfile.ZipFile(vfs_path, 'w') as myzip:
        for file in files_to_write:
            if file.endswith('/'):
                zinfo = zipfile.ZipInfo(file)
                zinfo.external_attr = 0o40775 << 16
                myzip.writestr(zinfo, '')
            else:
                myzip.writestr(file, '')

files_in_zip = read_zip()

current_dir = ''  # Начальная директория, пустая строка значит корень

while True:
    command = input(f'MyComputer {current_dir}$ ')

    if command == 'ls':
        unique_files = set()
        for name in files_in_zip:
            if name.startswith(current_dir):
                name_in_current_dir = name[len(current_dir):].split('/')[0]
                if name_in_current_dir.strip():
                    unique_files.add(name_in_current_dir)

        if unique_files:
            for file in unique_files:
                print(file)
        else:
            print("Нет файлов/папок в текущей директории.")

    elif command.startswith('cd '):
        path = command.split()[1]
        if path == '-':
            if current_dir:
                current_dir = '/'.join(current_dir.rstrip('/').split('/')[:-1]) + '/'
                if not current_dir or current_dir == "/":
                    current_dir = ''
            else:
                print("Вы уже находитесь в корневой директории.")
        elif any(name.startswith(current_dir + path + '/') for name in files_in_zip):
            current_dir = current_dir + path + '/'
        else:
            print("Директория не найдена.")

    elif command == 'exit':
        break

    elif command.startswith('rmdir '):
        dir_to_remove = command.split()[1]
        dir_path = current_dir + dir_to_remove + '/'
        files_in_dir = [name for name in files_in_zip if name.startswith(dir_path)]

        if not files_in_dir:
            print(f"Директория '{dir_to_remove}' пуста или не существует.")
        else:
            files_to_keep = [file for file in files_in_zip if not file.startswith(dir_path)]
            write_zip(files_to_keep)
            print(f"Директория '{dir_to_remove}' удалена.")
            files_in_zip = files_to_keep

    elif command.startswith('cat '):
        path = current_dir + command.split()[1]
        try:
            with zipfile.ZipFile(vfs_path, 'r') as myzip:
                content = myzip.read(path).decode('utf-8')
                print(content)
        except KeyError:
            print("Файл не найден.")
        except UnicodeDecodeError:
            print("Ошибка кодировки: файл не в UTF-8.")

    elif command == 'cal':
        now = datetime.now()
        print(calendar.month(now.year, now.month))

    else:
        print("Команда не найдена.")
