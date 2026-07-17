*This project has been created as part of the 42 curriculum by ascheufe.*

# Call Me Maybe

> [!NOTE]
> This project was fully done without AI usage. Meaning no AI has been used for help in the coding process or research.

## Description

Call me maybe is a python program that uses a local small `LLM` to generate function calls in a json output. It's goal is to generate 100% valid json output. Our subject wanted us to use constrained decoding, tho in my research I found a different way to do it that I used. 

My design is fundamentally different, as I see a better alternative approach by using something called a `compressed FSM` as referred to by this [article](https://www.lmsys.org/blog/2024-02-05-compressed-fsm/?ref=aidancooper.co.uk).

One of the constrains about this project is that we can only use a wrapper called `llm-sdk` provided by the 42 school to interact with the LLM model. By having this constrain we are limited to handling logits by ourselves and not being able to use handy build in functions of the hugging face library.

## Instructions

Requirements: Python 3.10+ and `uv` (Used to manage the virtual environment and dependencies).

There are two ways to run the project

### 1. Directly with `uv`


```sh
uv sync
uv run -m src
```

### 2. With the Makefile

```sh
make install       # Installs everything needed
make run            # Runs the program normally
make run-manual		# Runs the program with user input prompt
make debug          # same, but under Python's pdb
make lint           # flake8 + mypy
make lint-strict    # same, but with `mypy --strict`
make clean          # removes __pycache__ / .mypy_cache / .pytest_cache
```

### 3. Command line arguments

The programm supports multiple arguments on run


| Key | Value|
|-----|-------------------------------------------|
| `--functions_definition`	| [function definition file]	Default: "data/input/functions_definition.json"		|
| `--input`					| [prompt input file]			Default: "data/input/function_calling_tests.json"	|
| `--output`				| [prompt results] Default: "data/output/function_calls.json"	|
| `-m` | [Manual prompt input] No value required (Flag)                                       |

| Use of command line arguments | |
|---------|-----|
| `make run [--functions_definition <function_definition_file>] [--input <input_file>] [--output <output_file>]` |
| `uv run -m src [--functions_definition <function_definition_file>] [--input <input_file>] [--output <output_file>]` |

## Json Schema

### Function Definition

#### Schema

```json
[
	{
		"name": "[Name of the function]]",
		"description": "[What the function does]]",
		"parameters": {
			"a": {
				"type": "[Supported: integer, string, float, boolean]"
			}
			...
		},
		"returns": {
			"type": "[Supported: integer, string, float, boolean]"
		}
	},
	...
]
```

#### Example
```json
[
	{
		"name": "fn_add_int",
		"description": "Add two numbers together and return their sum.",
		"parameters": {
			"a": {
				"type": "integer"
			},
			"b": {
				"type": "integer"
			}
		},
		"returns": {
			"type": "integer"
		}
	}
]
```
------
### Prompt Json

#### Schema
```json
[
	{
	"prompt": "[Prompt]"
	},
	...
]
```

#### Example
```json
[
	{
	"prompt": "What is the sum of 2 and 3?"
	},
	{
	"prompt": "What is the sum of 265 and 345?"
	},
	{
	"prompt": "Greet shrek"
	},
	{
	"prompt": "Greet john"
	},
	{
	"prompt": "Reverse the string 'hello'"
	}
]
```

### Json Result

#### Schema
```json
[
  {
    "prompt": "[User Prompt]}",
    "name": "[Name of function]",
    "parameters": {
      "a": [value],
	...
	}
  },
  ...
]
```

#### Example
```json
[
  {
    "prompt": "What is the sum of 2 and 3?",
    "name": "fn_add_int",
    "parameters": {
      "a": 2,
      "b": 3
    }
  }
]
```


## How Does It work?

#### Rough overview
![overview](docs/draw.io/overview.drawio.svg)
-----

### FSM

#### The finite state machine walks trough the specific nodes constraining what the next valid character would be.
If the character is fully invalid it sets the logit to `-inf` in order to mark it as invalid and move on with the next selection.

![overview](docs/draw.io/fsm.drawio.svg)

#### This approach is not what constrained decoding is about. Constrained decoding would validate the tokens from the LLM before letting it pick them.
--------
![Progress](docs/draw.io/explain.drawio.svg)

### Why am I doing it differently?
If you would do the tradition constrained decoding you would use more tokens as you DO NOT autocomplete known keys but only constrain the LLM to write them correctly. Trough this approach you use more tokens other then autocompleting keys that you already know about.
Also when validating the tokens beforehand there can be problems in the sense of defining which tokens are invalid and which once aren't.

#### One example would be this:

Token: `Hello",`
Valid: `Hello"}`

In this scenario the LLM might wants to autocomplete the field with a `Hello,` thinking there is more to write when it should be the end. The problem about this is if you discard the token you are wasting a possible longer token for a unknown possible smaller token like: `He` whereby you now consume more tokens then if you would just picked the best one and discarded the end.

I think that the approach of just parsing them in general gives a better outcome then limiting the tokens drastically and potentially needing significantly more tokens. 

## Resources

### LLM in general
- [How does a LLMs work - YT](https://www.youtube.com/watch?v=aircAruvnKk&list=PLZHQObOWTQDNU6R1_67000Dx_ZCJB-3pi)

### Constrained decoding
- [Nerdy paper](https://arxiv.org/pdf/2307.09702)
- [SGLang LMSY](https://www.lmsys.org/blog/2024-02-05-compressed-fsm/?ref=aidancooper.co.uk)
- [One of the best articles explaining it](https://blog.dottxt.ai/coalescence.html?ref=aidancooper.co.uk)
