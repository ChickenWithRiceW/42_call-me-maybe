import json


def func_def_loader(file_name: str) -> list:
    try:
        with open(file_name, 'r') as file:
            data: list = json.load(file)
            return data
    except FileNotFoundError as e:
        print(e)
        exit(1)


def prompt_json_loader(file_name: str):
    try:
        with open(file_name, 'r') as file:
            prompt_list: list = json.load(file)
            return [prompt["prompt"] for prompt in prompt_list]
    except FileNotFoundError as e:
        print(e)
        exit(1)


def get_arguments_from_func(func_name: str, func_def_list: list[str]) -> list:
    args = []
    for d in func_def_list:
        if d["name"] == func_name:
            if not d["parameters"].items():
                exit()

            for arg in d["parameters"].items():
                args.append((arg[0], arg[1]["type"]))
    return args
