def get_llm_instruction(prompt: str, function_def: list[str]):
    t_instruction_prefix = '''\
<|im_start|>system
You are provided with function signatures \
within <tools></tools> XML tags you will pick a function that you think makes in the context of what the user has given you. Make sure that if you are unsure about or dont know what function to pick to default to none. Also make sure that you pick the function in a sense that as an example if the user gives in a int and a float to add together to pick a function that supports it or cast both to the same type without losing data:
<tools>\n
'''

    t_instruction_suffix = '''\
</tools>\n
For each function call, return a json
object within <tool_call></tool_call> tags:\n
<tool_call>\n
{"name": <function-name>, "arguments": <args-json-object>}\n
</tool_call>\n
<|im_end|>\n
'''

    text = f'''\
<|im_start|>user {prompt} <|im_end|>\n'\
<|im_start|>assistant\n'\
<tool_call>\n'''

    return t_instruction_prefix + function_def + t_instruction_suffix + text
