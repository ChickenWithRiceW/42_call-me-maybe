def get_llm_instruction(prompt: str, function_def: str) -> str:
    t_instruction_prefix = '''\
<|im_start|>system
You are a function calling AI system.
You are provided with function signatures \
within <tools></tools> XML tags you will pick a function from the list,
When provided with a prompt, you will pick a function, \
that matches the requirements of the prompt.
IF there is no clear function to pick, pick the function called none,
as a fallback function.
IF Pick the appropriate function out the function definition list.

In the function definition there are types. One time is called a number,
which is a float, meaning you will need to treat the input numbers as float.
You will then write a function call in json format.


<tools>\n
'''

    t_instruction_suffix = '''\
</tools>\n
For each function call, return a json
object within <tool_call></tool_call> tags:\n
<tool_call>\n
{"name": <function-name>, "arguments": <args-json-object>}\n
</tool_call>\n
MAKE SURE THAT A NUMBER NEEDS A FLOAT POINT.
<|im_end|>\n
'''

    text = f'''\
<|im_start|>user {prompt} <|im_end|>\n'\
<|im_start|>assistant\n'\
<tool_call>\n'''

    return t_instruction_prefix + function_def + t_instruction_suffix + text
