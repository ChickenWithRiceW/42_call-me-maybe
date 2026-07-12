import json

def loader(file_name: str = "output_sig.json") -> None:
    parameter: list = []
    try:
        with open(file_name, 'r') as file:
            data: dict = json.load(file)

            for key, value in data.items():
                if not isinstance(value, (list, dict, set, tuple)):
                    try:
                        parameter.append({key: eval(value)})
                    except NameError as e:
                        print(e)
                else:
                    parameter.append((key, value))
    except FileNotFoundError as e:
        print(e)
        exit(1)
    print(parameter)

if __name__ == "__main__":
    loader()