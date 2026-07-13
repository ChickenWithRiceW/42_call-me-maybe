from pydantic import BaseModel
import numpy
from collections.abc import Callable
from typing import Any
import json
import llm_sdk
# from typing import Callable | Subject once said dont import from typing

llm = llm_sdk.Small_LLM_Model()


class Node:
    def __init__(self, start:str, end: str, isfirst: bool, islast: bool):
        if isfirst:
            start = '"parameters": {' + start

        if islast:
            end = end.replace(" ", "") + "}"

        self.start: str = start
        self.end: str = end

        self.isfirst: bool = isfirst
        self.islast: bool = islast

    # TODO: Either remove or make abstract method
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



# TODO: Either keep or remove
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
            end = " "
            return NodeInt(
                start=start,
                end=end,
                isfirst=isfirst,
                islast=islast
            )

        case str.__class__():
            end = ", "
            return NodeStr(
                start=start,
                end=end,
                isfirst=isfirst,
                islast=islast
            )
        # TODO: Extend functionality to match given func signature


def fsm_node_walker(nodes: list[Node], sys_instruction: str, json_output: str) -> None:
    for node in nodes:
        # Inserting key
        json_output += node.start

        while True:
            ids = llm.encode(text=sys_instruction + json_output)
            logits = llm.get_logits_from_input_ids(ids[0].tolist())
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
    print(json_output)



def select_function(sys_instruction: str, json_output: str):
    tmp_name = ""
    while True:
        ids = llm.encode(text=sys_instruction + json_output + tmp_name)
        logits = llm.get_logits_from_input_ids(ids[0].tolist())
        max_log = numpy.argmax(logits)
        decoded: str = llm.decode([max_log])

        for c in decoded:
            print(tmp_name)
            if c.isalnum() or c == "_" or c == "-":
                name = matches_uniq_str(tmp_name + c, ["fn_add_numbers", "fn_greet"])

                if name:
                    json_output += name + '", '
                    break

                elif name == "":
                    tmp_name += c

                elif name is None:
                    logits.pop(max_log)
                    break
        else:
            continue

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
    prompt = "What is 5+5?"

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


    functions =\
'''\
[
    {
        "name": "fn_add_numbers",
        "description": "Add two numbers together and return their sum.",
        "parameters": {
            "a": {
                "type": "number"
            },
            "b": {
                "type": "number"
            }
        },
        "returns": {
            "type": "number"
    },
    {
    "name": "none",
    "description": "Pick if no usful function exist",
    "parameters": {},
    "returns": {
        "type": "none"
},
}
}'''
    sys_instruction = t_instruction_prefix + functions + t_instruction_suffix + text


    name, json_output = select_function(sys_instruction, '{"name": "')
    print(json_output)

    test = [("a", int), ("b", int)]

    nodes = []
    for i, t in enumerate(test, start=1):
        if i == 1:
            nodes.append(fsm_node_creator(t, True, False))
        elif i == len(test):
            nodes.append(fsm_node_creator(t, False, True))
        else:
            nodes.append(fsm_node_creator(t, False, False))

    
    fsm_node_walker(nodes, sys_instruction, json_output)


start()