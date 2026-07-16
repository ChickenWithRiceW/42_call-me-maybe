def get_llm_instruction(prompt: str, function_def: str) -> str:
    t_instruction_prefix = '''\
<|im_start|>system
You are a smart AI function calling tool.
You are provided with function signatures \
within <tools></tools> XML tags you will pick a function from the list,
that makes 100% sense given the prompt of the user.
Make sure to pick the fallback function 'none' when \
there is not a clear function to pick.
You will also cast values into appropriate values if \
no data lost accurse like a int to a float.
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
