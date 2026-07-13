from pydantic import BaseModel
import numpy
from collections.abc import Callable
from typing import Any
import json
import llm_sdk
# from typing import Callable | Subject once said dont import from typing

llm = llm_sdk.Small_LLM_Model()

class FsmNode():
    def __init__(self, start, end, con_loop, con_next):
        self.start: Callable = start
        self.end: Callable[[Any]] = end
        self.con_loop: Callable[[str], bool] = con_loop
        self.con_next: Callable[[str], bool] = con_next


def func_def_loader(file_name: str = "functions_definition.json") -> None:
    parameter: list = []
    try:
        with open(file_name, 'r') as file:
            data: dict | list = json.load(file)
    except FileNotFoundError as e:
        print(e)
        exit(1)
    return data


def fsm_node_creator(parameters: tuple, name_list: list[str] = None) -> FsmNode:
    # Start will add key onto string
    start = lambda s: s + f' "{parameters[0]}": '
    global end
    global con_loop
    global con_next
    match parameters[1]:
        case int.__class__():
            con_loop = lambda c: c.isnumeric()
            con_next = lambda c: c == ','
            end = ""

        case str.__class__():
            con_loop = lambda c: c.isalnum()
            con_next = lambda c: c == '"'
            end = ","

        case "func":
            con_loop = matches_uniq_str
            con_next = lambda c: c == '"'
            end = ","
        case _:
            print("Nothing worked")

    return FsmNode(
        start=start,
        end=end,
        con_loop=con_loop,
        con_next=con_next
    )


def fsm_node_walker(nodes: list[FsmNode], start_str: str, json_output: str) -> None:

    llm = llm_sdk.Small_LLM_Model()

    # print(start_str)

    for node in nodes:
        json_output = node.start(json_output)
        print(start_str + json_output)
        while True:
            id = llm.encode(text=start_str + json_output)
            logits = llm.get_logits_from_input_ids(id[0].tolist())
            max_log = numpy.argmax(logits)
            deco = llm.decode(max_log)
            print(deco)
            for c in deco:
                if node.con_loop(c):
                    json_output += c
                    print("Loop")

                elif node.con_next(c):
                    json_output += c
                    print("next")
                    break
                else:
                    logits.pop(max_log)
                    print("Skip")

            else:
                continue
            break
        json_output += node.end

    print(start_str + json_output)




def create_nodes(arg_list: list) -> list:
    ls = []

    for i, arg in enumerate(arg_list, start=1):
        if i == 1:
            arg = ('parameters: {"' + arg[0], arg[1])

        elif i == len(arg_list):
            arg = (arg[0], arg[1])

        print(arg)
        ls.append(fsm_node_creator(arg))
    return ls


def selecting_function_name(data: list, start_str: str) -> None:
    json_output = '{"name": "'
    start_node = fsm_node_creator(("name", "func"))

    id = llm.encode(text=start_str + json_output)
    logits = llm.get_logits_from_input_ids(id[0].tolist())

    deco = ""
    while True:
        max_log = numpy.argmax(logits)
        deco += llm.decode(max_log)
        print("deco: " + deco)
        name = start_node.con_loop(deco, data)
        print("name: " + name)
        if name:
            json_output += name.removeprefix(deco) + '",'
            break
        if name is None:
            logits.pop(max_log)
        if name == "":
            json_output += deco
            id = llm.encode(text=start_str + json_output)
            logits = llm.get_logits_from_input_ids(id[0].tolist())
            print(json_output)
    return (name, json_output)


def matches_uniq_str(prefix_str: str, name_list: list[str]) -> None | str:
    """Checks if given string is uniq to a name in the name list.

    Args:
        pre_str (str): Prefix to match
        name_list (list[str]): List of names

    Returns:
        None | str: Return an empty string when not uniq, None if nothing
            matched and a name from name_list if uniq
    """
    count = 0
    selected_name = ""

    for name in name_list:
        if name.startswith(prefix_str):
            count += 1
            selected_name = name

    # Does not match
    if count == 0:
        return None

    # Not uniq
    if count > 1:
        return ""

    # Matches uniq name
    return selected_name


def start() -> None:
    prompt = "What is one plus one"

    t_instruction_prefix =\
    '''
    <|im_start|>system\n
    You are provided with function signatures 
    within <tools></tools> XML tags:\n
    <tools>\n

    '''

    t_instruction_suffix =\
    '''
    </tools>\n
    For each function call, return a json
    object within <tool_call></tool_call> tags:\n
    <tool_call>\n
    {"name": <function-name>, "arguments": <args-json-object>}\n
    </tool_call>\n
    <|im_end|>\n
    '''


    text = '<|im_start|>user\n' + prompt + '\n<|im_end|>\n'\
    '<|im_start|>assistant\n'\
    '<tool_call>\n'

    data = func_def_loader()
    func = str(data)

    func_names = [i["name"] for i in data]

    complete = t_instruction_prefix + func + t_instruction_suffix + text


    # print(matches_uniq_str('fn', func_names))
    selected_func = selecting_function_name(func_names, complete)

    # print(selected_func[1])
    args = []
    for d in data:
        if d["name"] == selected_func[0]:
            for arg in d["parameters"].items():
                args.append((arg[0], eval(arg[1]["type"])))
    # print(args)
    ls = create_nodes(args)
    fsm_node_walker(ls, complete, selected_func[1])
    exit()


# print(matches_uniq_str("addition", ["addition", "subtraction", "cut"]))
start()