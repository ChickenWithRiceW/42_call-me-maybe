import json
from jsonschema import validate, ValidationError
from typing import Any

PROMPT_SCHEMA = {
    "type": "array",
    "items": {
        "type": "object",
        "properties": {
            "prompt": {
                "type": "string"
            }
        },
        "required": [
            "prompt"
        ]
    }
}


FUNC_SCHEMA = {
    "type": "array",
    "items": {
        "type": "object",
        "required": ["name", "description", "parameters", "returns"],
        "properties": {
            "name": {"type": "string"},
            "description": {"type": "string"},
            "parameters": {
                "type": "object",
                "additionalProperties": {
                    "type": "object",
                    "required": ["type"],
                    "properties": {
                        "type": {
                            "type": "string",
                            "enum": [
                                "integer",
                                "number",
                                "string",
                                "boolean",
                                "none"],
                        }
                    },
                    "additionalProperties": False,
                },
            },
            "returns": {
                "type": "object",
                "required": ["type"],
                "properties": {
                    "type": {
                        "type": "string",
                        "enum": [
                            "float",
                            "number",
                            "string",
                            "boolean",
                            "none"],
                    }
                },
                "additionalProperties": False,
            },
        },
        "additionalProperties": False,
    }
}


def func_def_loader(file_name: str) -> list[dict[str, Any]]:
    try:
        with open(file_name, 'r') as file:
            data: list[dict[str, Any]] = json.load(file)
            validate(instance=data, schema=FUNC_SCHEMA)
            return data
    except FileNotFoundError as e:
        print(e)
        exit(1)
    except ValidationError as e:
        print(f"{e.message}. Error in {file_name}")
        exit(1)
    except json.decoder.JSONDecodeError:
        print(f"Invalid {file_name} json")
        exit(1)


def prompt_json_loader(file_name: str) -> list[str]:
    try:
        with open(file_name, 'r') as file:
            prompt_list: list[dict[str, str]] = json.load(file)
            validate(instance=prompt_list, schema=PROMPT_SCHEMA)
            return [prompt["prompt"] for prompt in prompt_list]
    except FileNotFoundError as e:
        print(e)
        exit(1)
    except json.decoder.JSONDecodeError:
        print(f"Invalid {file_name} json")
        exit(1)
    except ValidationError as e:
        print(f"{e.message}. Error in {file_name}")
        exit(1)


def get_arguments_from_func(
        func_name: str,
        func_def_list: list[dict[str, Any]]
        ) -> list[tuple[str, str]]:
    args = []
    for d in func_def_list:
        if d["name"] == func_name:
            if not d["parameters"].items():
                exit()

            for arg in d["parameters"].items():
                args.append((arg[0], arg[1]["type"]))
    return args
