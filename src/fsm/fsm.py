# from pydantic import BaseModel
import numpy
# from typing import Any
import llm_sdk
from abc import ABC, abstractmethod
import re
# from main import llm
# from typing import Callable | Subject once said dont import from typing

PARAMETER_KEY = '"parameters":{'

from fuck import llm
# llm = llm_sdk.Small_LLM_Model()


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
        return re.fullmatch(r'^(-?)([0-9]|$)+$', s)

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
        return re.fullmatch(r"^(-?)([0-9]|$)+(\.?)+([0-9]|$)+$", s)

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
        return re.fullmatch(r"^[A-Za-z-,!? 0-9]+$", s)

    def con_next(self, s: str) -> bool:
        return s == '"'


class NodeBool(Node):
    def __init__(
            self,
            start: str,
            end: str,
            isfirst: bool,
            islast: bool
            ) -> None:
        super().__init__(start, end, isfirst, islast)

    def con_loop(self, s: str) -> bool:
        return False

    def con_next(self, s: str) -> bool:
        if self.islast:
            self.end = "}"
        if s == "t":
            return "true" + self.end
        if s == "f":
            return "false" + self.end


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
        case "bool":
            end = ","
            return NodeBool(
                start=start,
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

        test = ""
        ids = llm.encode(text=sys_instruction + json_output)
        logits = llm.get_logits_from_input_ids(ids[0].tolist())
        while True:
            pop = False
            max_log = numpy.argmax(logits)
            decoded = llm.decode([max_log])

            print("decoded: ", decoded)
            for c in decoded:
                print(c)
                test += c
                if node.con_loop(test):
                    json_output += c
                    print("loop")
                    continue

                elif node.con_next(c):
                    print("next")
                    auto = node.con_next(c)
                    print(type(auto))
                    if isinstance(auto, bool):
                        json_output += c + node.end
                    else:
                        json_output += auto + node.end
                    break

                else:
                    logits.pop(max_log)
                    print("pop")    # Needs fixing for edge case
                    pop = True
                    break
                
            else:
                ids = llm.encode(text=sys_instruction + json_output)
                logits = llm.get_logits_from_input_ids(ids[0].tolist())
                # test = ""
                continue

            test = ""
            if not pop:
                break
    print(json_output)
    return json_output


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
