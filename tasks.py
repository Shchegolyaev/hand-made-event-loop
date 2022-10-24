import json
import os
import random
import string
import time

import requests

from logger import logging


class Tasks:
    @staticmethod
    def target():
        data_chunk = yield
        print(f"Target: Получено {data_chunk}")
        yield

    @staticmethod
    def pipe():
        output = Tasks.target()
        output.send(None)
        data_chunk = yield
        print(f"Pipe: Обработка {data_chunk}")
        output.send(data_chunk)
        yield

    @staticmethod
    def source():
        output = Tasks.pipe()
        output.send(None)
        data = 111
        output.send(data)
        print(f"Source: Отправлено {data}")
        yield
        output.close()

    @staticmethod
    def get_five_random_user():
        users = []
        for num in range(1, 6):
            logging.info(f"Get {num} user.")
            request = requests.get("https://randomuser.me/api/")
            request_text = request.text
            request_text = json.loads(request.text)
            full_name = (
                f"{request_text['results'][0]['name']['first']} "
                f"{request_text['results'][0]['name']['last']}"
            )
            users.append(full_name)
            logging.info(f"Get user info {full_name}.")
            yield
        logging.info(f"Get users: {users}")

    @staticmethod
    def generate_random_string(length):
        # generate file with random text
        letters = string.ascii_lowercase
        lines = [
            "".join(random.choice(letters)
                    for i in range(length)) for _ in range(5)
        ]
        name_file = f"{random.randint(100, 1000)}_file.txt"
        logging.info(f"Create file {name_file}.")
        with open(name_file, "w") as file:
            for line in lines:
                file.write(line + "\n")
        logging.info(f"File {name_file} created.")
        time.sleep(1)

        # read line by line created file
        with open(name_file, "r") as file:
            for line in file:
                # logging.info("One string from file: \n", line)
                yield
        time.sleep(1)

        # delete file
        os.remove(name_file)
        logging.info(f"File {name_file} deleted.")

    @staticmethod
    def manage_folders_os(name_dir):
        print(f"Begin task manage_folders_os {name_dir}")
        time.sleep(5)
        logging.info("Begin task manage_folders_os")

        os.mkdir(name_dir)
        time.sleep(5)
        yield
        logging.info("Created dir folder_for_coro")
        time.sleep(4)
        yield
        os.makedirs(f"{name_dir}/inner_coro/rabbit_hope")
        os.renames(f"{name_dir}", "new_folder_for_coro")
        os.system("touch documents.txt")
        os.removedirs("new_folder_for_coro/inner_coro/rabbit_hope")
        time.sleep(4)
        yield
        os.remove("documents.txt")
        logging.info("End task manage_folders_os")

        print("End task manage_folders_os")


# coro = Tasks.get_five_random_user()
# next(coro)
