# from pydantic import BaseModel
import numpy
# from typing import Any
import llm_sdk
from abc import ABC, abstractmethod
# from typing import Callable | Subject once said dont import from typing

PARAMETER_KEY = '"parameters": {'

llm = llm_sdk.Small_LLM_Model()


# TODO: Maybe change conditions to regex patterns

class Node(ABC):
    def __init__(self, start: str, end: str, isfirst: bool, islast: bool):
        if isfirst:
            start = PARAMETER_KEY + start

        if islast:
            end = end.replace(",", "") + "}"

        self.start: str = start
        self.end: str = end

        self.isfirst: bool = isfirst
        self.islast: bool = islast

    @abstractmethod
    def con_loop(self, s: str) -> bool:
        pass

    @abstractmethod
    def con_next(self, s: str) -> bool:
        pass


class NodeInt(Node):
    def __init__(
            self,
            start: str,
            end: str,
            isfirst: bool,
            islast: bool
            ) -> None:
        super().__init__(start, end, isfirst, islast)

    def con_loop(self, s: str) -> bool:
        return s.isdecimal()

    def con_next(self, s: str) -> bool:
        if self.islast:
            return s == "}"
        return s == ","


class NodeFloat(Node):
    def __init__(
            self,
            start: str,
            end: str,
            isfirst: bool,
            islast: bool
            ) -> None:
        super().__init__(start, end, isfirst, islast)

    def con_loop(self, s: str) -> bool:
        return s.isdecimal() or s == '.'

    def con_next(self, s: str) -> bool:
        if self.islast:
            return s == "}"
        return s == ","


class NodeStr(Node):
    def __init__(
            self,
            start: str,
            end: str,
            isfirst: bool,
            islast: bool
            ) -> None:

        if islast:
            end += "}"
        super().__init__(start, end, isfirst, islast)

    def con_loop(self, s: str) -> bool:
        return s.isalnum()

    def con_next(self, s: str) -> bool:
        return s == '"'


def fsm_node_creator(
    parameters: tuple[str, str],
    isfirst: bool,
    islast: bool
        ) -> Node:

    # Start will add key onto string
    start = f'"{parameters[0]}":'
    match parameters[1]:
        case "int":
            end = ""
            return NodeInt(
                start=start,
                end=end,
                isfirst=isfirst,
                islast=islast
            )

        case "float":
            end = ""
            return NodeFloat(
                start=start,
                end=end,
                isfirst=isfirst,
                islast=islast
            )

        case "str":
            end = ","
            return NodeStr(
                start=start + '"',
                end=end,
                isfirst=isfirst,
                islast=islast
            )
        case _:
            print("Issue..")
            exit()
        # TODO: Extend functionality to match given func signature


def fsm_node_walker(
        nodes: list[Node],
        sys_instruction: str,
        json_output: str
        ) -> None:

    for node in nodes:
        # Inserting key
        json_output += node.start
        print(json_output)

        while True:
            ids = llm.encode(text=sys_instruction + json_output)
            logits = llm.get_logits_from_input_ids(ids[0].tolist())
            max_log = numpy.argmax(logits)
            decoded = llm.decode([max_log])

            print(decoded)
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

    # Does not match anything
    if count == 0:
        return None

    # Not uniq
    if count > 1:
        return ""

    # Matches uniq name
    return selected_name
