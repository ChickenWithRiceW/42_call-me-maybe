import json


def __init__(self) -> None:
    self.names


def func_def_loader(file_name: str = "functions_definition.json") -> list:
    try:
        with open(file_name, 'r') as file:
            data: list = json.load(file)
    except FileNotFoundError as e:
        print(e)
        exit(1)
    return data


def get_arguments_from_func(func_name: str, func_def_list: list[str]) -> list:
    args = []
    for d in func_def_list:
        if d["name"] == func_name:
            if not d["parameters"].items():
                exit()

            for arg in d["parameters"].items():
                args.append((arg[0], arg[1]["type"]))
    return args
