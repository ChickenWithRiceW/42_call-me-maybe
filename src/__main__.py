from src.instruction.llm_instruction import get_llm_instruction
from .loader.loader import func_def_loader, get_arguments_from_func, \
    prompt_json_loader
from src.fsm.fsm import fsm_node_creator, fsm_node_walker, matches_uniq_str
import numpy
import argparse
import json
import llm_sdk
from typing import Any

JSON_START = '{"name":"'


def main() -> None:
    """Entry point for loading json definitons and walking trough given prompts"""
    p = argparse.ArgumentParser(
        prog="Call me maybe",
        description="Function calling LLM"
    )

    p.add_argument(
        "--input",
        help="[<input_file>]",
        default="data/input/function_calling_tests.json",
        metavar=""
    )

    p.add_argument(
        "--output",
        help="[<output_file>]",
        default="data/output/function_calls.json",
        metavar=""
    )

    p.add_argument(
        "--functions_definition",
        help="[<function_definition_file>]",
        default="data/input/functions_definition.json",
        metavar=""
    )

    p.add_argument(
        "-m",
        help="Enter own prompt",
        action='store_true'
    )

    args = p.parse_args()

    # Load function definitions
    func_def_list = func_def_loader(args.functions_definition)

    # Extract only function names
    func_names = [i["name"] for i in func_def_list]

    if not args.m:
        # Get prompts
        prompts = prompt_json_loader(args.input)
    else:
        prompts = [input("Prompt: ")]

    llm = llm_sdk.Small_LLM_Model()

    json_result = []
    for prompt in prompts:
        result = {"prompt": prompt}

        result.update(prompt_parser(prompt, func_def_list, func_names, llm))
        json_result.append(result)

    try:
        with open(args.output, 'w') as f:
            f.write(json.dumps(json_result, indent=2))
    except PermissionError as e:
        print(e)
        exit(1)
    # Idk yet


def prompt_parser(
        prompt: str,
        func_def_list: list[str],
        func_names: list[str],
        llm: llm_sdk.Small_LLM_Model
        ) -> Any:
    """Parses all given prompts and outputs a list of the finished json function call

    Args:
        prompt (str): The user prompt
        func_def_list (list[str]): A list of all the function definitions
        func_names (list[str]): A list of only function names
        llm (llm_sdk.Small_LLM_Model): LLM instance

    Returns:
        Any: Json in the function calling schema
    """
    # Construct system prompt with function definitions
    sys_instruction = get_llm_instruction(prompt, str(func_def_list))

    # Let LLM select function to call
    print(f"\nAI selecting function for prompt: '{prompt}'")
    selected_name, json_output = select_function(
        sys_instruction,
        JSON_START,
        func_names,
        llm
    )

    # Extract parameters of selected function
    args = get_arguments_from_func(selected_name, func_def_list)

    # Create FSM nodes
    nodes = []
    for i, t in enumerate(args, start=1):
        isfirst = i == 1
        islast = i == len(args)
        nodes.append(fsm_node_creator(t, isfirst, islast))

    # Walk the FSM nodes
    tmp = fsm_node_walker(nodes, sys_instruction, json_output, llm)

    return json.loads(tmp)


def select_function(
        sys_instruction: str,
        json_output: str,
        function_names: list[str],
        llm: llm_sdk.Small_LLM_Model
        ) -> tuple[str, str]:
    """Lets the LLM pick out a function name and returns its selection

    Args:
        sys_instruction (str): The system instructions for the LLM
        json_output (str): Blueprint for the json output
        function_names (list[str]): A list of all given function names
        llm (llm_sdk.Small_LLM_Model): the llm instance

    Returns:
        tuple[str, str]: Tuple containing the selected function name with the json output
    """
    name_build = ""
    tok_sys_prompt = llm.encode(text=sys_instruction)[0].tolist()

    ids = llm.encode(json_output + name_build)
    logits = llm.get_logits_from_input_ids(tok_sys_prompt + list(ids[0]))
    while True:
        max_log = numpy.argmax(logits)
        decoded: str = llm.decode([int(max_log)])

        for i, c in enumerate(decoded):
            print(json_output + name_build)
            name = matches_uniq_str(name_build + c, function_names)

            # If only one function matches, autocomplete it.
            if name:
                json_output += name + '",'
                print(json_output)
                return (name, json_output)

            # If not uniq yet, keep building name
            elif name == "":
                name_build += c

            # Does not match anything wrong token from LLM
            elif name is None:
                # When the first token is completely wrong skip it
                if i == 0:
                    logits[max_log] = float("-inf")
                    break
                else:
                    ids = llm.encode(json_output + name_build)
                    logits = llm.get_logits_from_input_ids(
                        tok_sys_prompt + list(ids[0])
                        )
                    break
        else:
            ids = llm.encode(json_output + name_build)
            logits = llm.get_logits_from_input_ids(
                tok_sys_prompt + list(ids[0])
                )


if __name__ == "__main__":
    main()
