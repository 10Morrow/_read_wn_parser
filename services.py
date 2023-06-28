import os
import re
import urllib
import urllib.parse
import pickle
import requests
from fake_useragent import UserAgent
import time
from config import TIME_DELAY, NUMBER_OF_PROXY, USE_PROXY


def increase_number(stop_num=11):
    number = (-1)

    def increment():
        nonlocal number
        number += 1
        if number == stop_num:
            number = 0

        return number

    return increment

if USE_PROXY:
    request_counter = increase_number(11)
    proxy_num = increase_number(NUMBER_OF_PROXY)


def create_closure():
    value = None

    def get_value():
        return value

    def set_value(new_value):
        nonlocal value
        value = new_value

    return get_value, set_value


get_value_func, set_value_func = create_closure()


def default_request(link, counter = 0):
    ua = UserAgent()
    user_agent = ua.random
    headers = {
        'User-Agent': user_agent
    }
    time.sleep(TIME_DELAY)
    if USE_PROXY:
        global request_counter
        global get_value_func
        global set_value_func
        if request_counter() == 0:
            set_value_func(change_proxy())
        proxy = get_value_func()
        ip, port, login, password = proxy.split(':')
        proxies = {
            'http': f"http://{login}:{password}@{ip}:{port}",
            'https': f"http://{login}:{password}@{ip}:{port}"
        }

        response = requests.get(url=link, headers=headers, proxies=proxies)
    else:
        response = requests.get(url=link, headers=headers)
    print(link, response.status_code)
    if (response.status_code == 403 or response.status_code == 429) and counter != 3:
        counter += 1
        print(link, f"try again ({counter})")
        default_request(link=link, counter=counter)
    return response


def get_pagination_number(link):
    parsed_url = urllib.parse.urlparse(link)
    path = parsed_url.path
    number = re.search(r'\d+', path).group()

    return number


def is_valid_url(url):
    try:
        result = urllib.parse.urlparse(url)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False


def create_folder_if_not_exists(folder_name):
    if not os.path.isdir(f"all_novels/{folder_name}"):
        os.makedirs(f"all_novels/{folder_name}")


def write_data_to_file(folder_name, file_num,  my_data):
    file_path = f"all_novels/{folder_name}/{file_num}.txt"
    if not (os.path.exists(file_path) and os.path.isfile(file_path)):
        with open(file_path, 'w') as file:
            for item in my_data:
                file.write(str(item) + '\n')


def save_state(data):
    with open("data.pickle", 'wb') as file:
        pickle.dump(data, file)


def load_state():
    if os.path.exists("data.pickle") and os.path.isfile("data.pickle"):
        with open("data.pickle", 'rb') as file:
            data = pickle.load(file)
        return data


def create_pickle():
    data = {}
    if not (os.path.exists("data.pickle") and os.path.isfile("data.pickle")):
        with open("data.pickle", 'wb') as file:
            pickle.dump(data, file)


def change_proxy():
    global proxy_num
    proxy_list = []
    with open('proxy.txt', 'r') as file:
        for line in file:
            line = line.strip()

            if line:
                proxy_list.append(line)
    num = proxy_num()
    proxy_list=proxy_list[1:]
    if proxy_list:
        return proxy_list[num]
    else:
        raise IndexError("You don't have proxy in 'proxy.txt'")