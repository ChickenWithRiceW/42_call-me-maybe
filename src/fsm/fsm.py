from pydantic import BaseModel
from collections.abc import Callable
from typing import Any
# from typing import Callable | Subject once said dont import from typing


class FsmNode():
    def __init__(self, start, end, con_loop, con_next):
        self.start: Callable = start
        self.end: Callable[[Any]] = end
        self.con_loop: Callable[[str], bool] = con_loop
        self.con_next: Callable[[str], bool] = con_next


def trans_str() -> str:
    pass



def fsm_node_creator(parameters: tuple) -> FsmNode:
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
        case _:
            print("Nothing worked")

    return FsmNode(
        start=start,
        end=end,
        con_loop=con_loop,
        con_next=con_next
    )


def fsm_node_walker(nodes: list[FsmNode], start_str: str) -> None:
    for node in nodes:
        start_str = node.start()
        # Give start_str to LLM
        # Look at logits
        # Pick out 5 best
        # test loop then next

        # Keep in mind that it should generally not be able to just skip.

n = fsm_node_creator(("Name", str))
starting_str = "Json: {"
starting_str = n.start(starting_str)
print(starting_str)
print(n.con_loop("1"))
print(n.con_loop("a"))
