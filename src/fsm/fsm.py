from pydantic import BaseModel
import numpy
from collections.abc import Callable
from typing import Any
import json
import llm_sdk
# from typing import Callable | Subject once said dont import from typing


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
    start = lambda s: s + f'"{parameters[0]}": '
    print(parameters[1])
    match parameters[1]:
        case int.__class__():
            con_loop = lambda c: c.isnumeric()
            con_next = lambda c: c == ','
            end = None

        case str.__class__():
            con_loop = lambda c: c.isalnum()
            con_next = lambda c: c == '"'
            end = lambda s: s + ","
        
        case "func":
            con_loop = lambda s: matches_uniq_str(s, name_list)
            con_next = lambda c: c == '"'
            end = lambda s: s + ","
        case _:
            print("Nothing worked")

    return FsmNode(
        start=start,
        end=end,
        con_loop=con_loop,
        con_next=con_next
    )


def fsm_node_walker(nodes: list[FsmNode], start_str: str) -> None:

    print(start_str)
    tmp_name = ""
    start_node = fsm_node_creator(("name", "func"))
    llm = llm_sdk.Small_LLM_Model()

    id = llm.encode(text=start_str)
    print(id[0].tolist())
    logits = llm.get_logits_from_input_ids(id[0].tolist())
    print(logits[0])
    max_log = numpy.argmax(logits)
    print(max(logits))
    print(logits[max_log])
    print(llm.decode([max_log]))


    # for node in nodes:
    #     start_str = node.start()
    #     # Give start_str to LLM
    #     # Look at logits
    #     # Pick out 5 best
    #     # test loop then next

    #     # Keep in mind that it should generally not be able to just skip.


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
    llm = llm_sdk.Small_LLM_Model()
    prompt = "Hey, can you help me pick a colour for my house?"

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
    '<tool_call>\n'\
    '{"name": "'
    fsm_node_walker(None, t_instruction_prefix + '{"name": addition, "arguments": {a: int}}' + t_instruction_suffix + text)


start()