from src.instruction.llm_instruction import get_llm_instruction
from src.loader.loader import func_def_loader, get_arguments_from_func
from src.fsm.fsm import fsm_node_creator, fsm_node_walker, matches_uniq_str
import numpy
from fuck import llm


JSON_START = '{"name":"'

def start(prompt: str) -> str:
    # Interactive user prompt for testing
    # prompt = input("Prompt: ")

    # prompt = "What is -1.1 plus 2.2"

    # Load function definitions
    func_def_list = func_def_loader()

    # Construct system prompt with function definitions
    sys_instruction = get_llm_instruction(prompt, str(func_def_list))

    # Extract only function names
    func_names = [i["name"] for i in func_def_list]

    # Let LLM select function to call
    selected_name, json_output = select_function(
        sys_instruction,
        JSON_START,
        func_names
        )

    # TODO: Either delete or properly use to check if type is supported
    known_types = {
        'int': int,
        'float': float,
        'str': str,
        'bool': bool
    }

    # Extract parameters of selected function
    args = get_arguments_from_func(selected_name, func_def_list)

    # Create FSM nodes
    nodes = []
    for i, t in enumerate(args, start=1):
        print(t)
        if i == 1 and i == len(args):
            nodes.append(fsm_node_creator(t, True, True))
        elif i == 1:
            nodes.append(fsm_node_creator(t, True, False))
        elif i == len(args):
            nodes.append(fsm_node_creator(t, False, True))
        else:
            nodes.append(fsm_node_creator(t, False, False))

    # Walk the nodes
    return fsm_node_walker(nodes, sys_instruction, json_output)


# ! Should be handled over node walker possibly
# Will be difficult as I need to firstly figure out what function arguments to extract



def select_function(
        sys_instruction: str,
        json_output: str,
        function_names: list[str]):

    tmp_name = ""
    while True:
        ids = llm.encode(text=sys_instruction + json_output + tmp_name)
        logits = llm.get_logits_from_input_ids(ids[0].tolist())
        max_log = numpy.argmax(logits)
        decoded: str = llm.decode([max_log])

        for c in decoded:
            print("decoded: ", decoded)
            print(tmp_name)
            name = matches_uniq_str(tmp_name + decoded, function_names)
            print("name:", name)

            if name:
                json_output += name + '",'
                exit()
                return (name, json_output)

            elif name == "":
                tmp_name += decoded
                print("Not precise enough")
                break

            elif name is None:
                logits.pop(max_log)
                break
        # else:
        #     continue

    return (name, json_output)


if __name__ == "__main__":
    # start(input("Prompt: "))
    start("What is 5+5")
    # print("nothing done...")