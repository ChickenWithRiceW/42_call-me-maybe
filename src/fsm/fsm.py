from pydantic import BaseModel
import numpy
from collections.abc import Callable
from typing import Any
import json
import llm_sdk
# from typing import Callable | Subject once said dont import from typing


class FsmNode():
    def __init__(self, start, end, con_loop, con_next, isfirst, islast):
        self.start: Callable = start
        self.end: Callable[[Any]] = end

        self.isfirst: bool = isfirst
        self.islast: bool = islast

        self.con_loop: Callable[[str], bool] = con_loop
        self.con_next: Callable[[str], bool] = con_next

class Node:
    def __init__(self, start:str , end: str, con_loop, con_next, isfirst: bool, islast: bool):
        if isfirst:
            start = "{" + start

        if islast:
            end = end + "}"

        self.start: str = start
        self.end: str = end

        self.isfirst: bool = isfirst
        self.islast: bool = islast

    def con_loop(self, s: str) -> bool:
        pass

    def con_next(self, s: str) -> bool:
        pass

class NodeInt(Node):
    def __init__(self, start, end, isfirst, islast):
        super().__init__(start, end, isfirst, islast)

    def con_loop(self, s: str) -> None:
        return s.isnumeric()
    
    def con_next(self, s: str):
        if self.islast:
            return s == "}"
        return s == ","

class NodeStr(Node):
    def __init__(self, start, end, isfirst, islast):
        super().__init__(start, end, isfirst, islast)

    def con_loop(self, s: str) -> None:
        return s.isalnum()
    
    def con_next(self, s: str):
        return s == ','




def func_def_loader(file_name: str = "functions_definition.json") -> None:
    parameter: list = []
    try:
        with open(file_name, 'r') as file:
            data: dict | list = json.load(file)
    except FileNotFoundError as e:
        print(e)
        exit(1)
    return data


def fsm_node_creator(parameters: tuple, isfirst: bool, islast: bool) -> FsmNode:
    # Start will add key onto string
    start = f'"{parameters[0]}": '
    match parameters[1]:
        case int.__class__():
            end = None
            return NodeInt(
                start=start,
                end=end,
                isfirst=isfirst,
                islast=islast
            )

        case str.__class__():
            end = ","
            return NodeStr(
                start=start,
                end=end,
                isfirst=isfirst,
                islast=islast
            )
        
        case "func":
            end = ","
        case _:
            print("Nothing worked")

    return FsmNode(
        start=start,
        end=end,
        isfirst=
    )


def fsm_node_walker(nodes: list[FsmNode], sys_instruction: str, json_output: str) -> None:
    llm = llm_sdk.Small_LLM_Model()

    for node in nodes:
        # Inserting key
        json_output += node.start

        while True:
            ids = llm.encode(text=sys_instruction + json_output)
            logits = llm.get_logits_from_input_ids(id[0].tolist())
            max_log = numpy.argmax(logits)
            decoded = llm.decode([max_log])

            for c in decoded:
                if node.con_loop(c):
                    json_output += c

                elif node.con_next(c):
                    json_output += c + node.end
                    break
                
                else:
                    logits.pop(max_log)
                    break
            else:
                continue

            break



    while True:



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