from pydantic import BaseModel
import numpy
from typing import Any
import llm_sdk
from abc import ABC, abstractmethod
import re

PARAMETER_KEY = '"parameters":{'
SUPPORTED_TYPES = {"int", "float", "str", "bool"}


class Node(ABC):
    def __init__(self, start: str, end: str, is_first: bool, is_last: bool):
        if is_first:
            start = PARAMETER_KEY + start

        if is_last:
            end = end.replace(",", "") + "}"

        self.start: str = start
        self.end: str = end

        self.is_first: bool = is_first
        self.is_last: bool = is_last

    @abstractmethod
    def con_loop(self, s: str) -> Any:
        pass

    @abstractmethod
    def con_next(self, s: str) -> Any:
        pass


class NodeInt(Node):
    def __init__(
            self,
            start: str,
            end: str,
            is_first: bool,
            is_last: bool
            ) -> None:
        super().__init__(start, end, is_first, is_last)

    def con_loop(self, s: str) -> bool:
        return bool(re.fullmatch(r'^(-?)([0-9]|$)+$', s))

    def con_next(self, s: str) -> bool:
        if self.is_last:
            return s == "}"
        return s == ","


class NodeFloat(Node):
    def __init__(
            self,
            start: str,
            end: str,
            is_first: bool,
            is_last: bool
            ) -> None:
        super().__init__(start, end, is_first, is_last)

    def con_loop(self, s: str) -> bool:
        return bool(re.fullmatch(r"^(-?)([0-9]|$)+(\.?)+([0-9]|$)+$", s))

    def con_next(self, s: str) -> bool:
        if self.is_last:
            return s == "}"
        return s == ","


class NodeStr(Node):
    def __init__(
            self,
            start: str,
            end: str,
            is_first: bool,
            is_last: bool
            ) -> None:

        if is_last:
            end += "}"
        super().__init__(start, end, is_first, is_last)

    def con_loop(self, s: str) -> bool:
        return bool(re.fullmatch(r"^[A-Za-z-,!? 0-9]+$", s))

    def con_next(self, s: str) -> bool:
        return s == '"'


class NodeBool(Node):
    def __init__(
            self,
            start: str,
            end: str,
            is_first: bool,
            is_last: bool
            ) -> None:
        if self.is_last:
            self.end = "}"
        super().__init__(start, end, is_first, is_last)

    def con_loop(self, s: str) -> bool:
        return False

    def con_next(self, s: str) -> str | bool:
        if s == "t":
            return "true" + self.end
        if s == "f":
            return "false" + self.end
        return False


def fsm_node_creator(
    parameters: tuple[str, str],
    is_first: bool,
    is_last: bool
        ) -> Node:

    # Start will add key onto string
    start = f'"{parameters[0]}":'
    match parameters[1]:
        case "int":
            end = ""
            return NodeInt(
                start=start,
                end=end,
                is_first=is_first,
                is_last=is_last
            )

        case "float":
            end = ""
            return NodeFloat(
                start=start,
                end=end,
                is_first=is_first,
                is_last=is_last
            )

        case "str":
            end = ","
            return NodeStr(
                start=start + '"',
                end=end,
                is_first=is_first,
                is_last=is_last
            )
        case "bool":
            end = ","
            return NodeBool(
                start=start,
                end=end,
                is_first=is_first,
                is_last=is_last
            )
        case _:
            print(f"{parameters[1]} is not supported")
            print(f"Supported: {SUPPORTED_TYPES}")
            exit()


def fsm_node_walker(
        nodes: list[Node],
        sys_instruction: str,
        json_output: str,
        llm: llm_sdk.Small_LLM_Model
        ) -> str:

    for node in nodes:
        json_output += node.start

        build_str = ""
        ids = llm.encode(text=sys_instruction + json_output)
        logits = llm.get_logits_from_input_ids(ids[0].tolist())

        while True:
            pop = False
            max_log = numpy.argmax(logits)
            decoded = llm.decode([int(max_log)])

            for c in decoded:
                build_str += c
                if node.con_loop(build_str):
                    json_output += c
                    print(json_output)
                    continue

                elif node.con_next(c):
                    auto_complete = node.con_next(c)

                    if isinstance(auto_complete, bool):
                        json_output += c + node.end
                    else:
                        json_output += auto_complete + node.end
                    break

                else:
                    logits.pop(max_log)
                    pop = True
                    break

            else:
                ids = llm.encode(text=sys_instruction + json_output)
                logits = llm.get_logits_from_input_ids(ids[0].tolist())
                continue

            build_str = ""
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
