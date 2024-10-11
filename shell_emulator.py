import os
import argparse
import tarfile
import json
import sys

class ShellEmulator:
    def __init__(self, user, host, fs_path, log_file):
        self.user = user
        self.host = host
        self.fs_path = fs_path
        self.log_file = log_file
        self.current_directory = os.getcwd()  # Текущая рабочая директория

        # Инициализация файловой системы
        self.init_filesystem()

    def init_filesystem(self):
        # Распаковка файловой системы из tar файла
        with tarfile.open(self.fs_path) as tar:
            tar.extractall(path="virtual_fs")  # Распаковываем в папку virtual_fs
        os.chdir("virtual_fs")  # Переключаем текущую директорию на virtual_fs
        self.current_directory = os.getcwd()

    def log_action(self, command):
        # Логирование действий
        action = {
            'user': self.user,
            'host': self.host,
            'command': command
        }
        with open(self.log_file, 'a') as f:
            json.dump(action, f)
            f.write('\n')

    def handle_ls(self):
        # Обработка команды ls
        files = os.listdir(self.current_directory)  # Получаем файлы текущей директории
        for file in files:
            if file != 'actions_log.json':  # Пропускаем actions_log.json
                print(file)  # Выводим каждое имя файла в столбик

    def handle_cd(self, path):
        # Обработка команды cd
        new_path = os.path.join(self.current_directory, path)
        if os.path.isdir(new_path):
            os.chdir(new_path)
            self.current_directory = os.getcwd()
            return self.current_directory
        else:
            return f"cd: {path}: No such file or directory"

    def handle_find(self, filename):
        # Обработка команды find
        found_files = []
        for root, dirs, files in os.walk(self.current_directory):
            if filename in files:
                found_files.append(os.path.join(root, filename))
        return found_files

    def handle_du(self):
        # Обработка команды du
        total_size = 0
        for dirpath, dirnames, filenames in os.walk(self.current_directory):
            for f in filenames:
                fp = os.path.join(dirpath, f)
                total_size += os.path.getsize(fp)
        return total_size

    def run(self):
        # Основной цикл
        while True:
            command = input(f"{self.user}@{self.host}:{self.current_directory}$ ")
            self.log_action(command)

            if command.startswith("ls"):
                self.handle_ls()  # Выводим файлы напрямую

            elif command.startswith("cd"):
                _, path = command.split(maxsplit=1)
                result = self.handle_cd(path)
                if isinstance(result, str):
                    print(result)

            elif command.startswith("find"):
                _, filename = command.split(maxsplit=1)
                found_files = self.handle_find(filename)
                print(found_files if found_files else f"{filename} not found")

            elif command.startswith("du"):
                size_info = self.handle_du()
                print(size_info)

            elif command == "exit":
                print("Exiting the shell.")
                break

            else:
                print("Command not found.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--user', required=True, help='Username')
    parser.add_argument('--host', required=True, help='Host name')
    parser.add_argument('--fs', required=True, help='File system tar file')
    parser.add_argument('--log', required=True, help='Log file name')

    args = parser.parse_args()

    shell = ShellEmulator(args.user, args.host, args.fs, args.log)
    shell.run()
