*This project has been created as part of the 42 curriculum by ascheufe.*

# Call Me Maybe

[!NOTE] This project was fully done without AI usage. Meaning no AI has been used for help in the coding process or research.

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

### FSM

#### The finite state machine walks trough the specific nodes in order to figure out what the next valid character should be.
![overview](docs/draw.io/fsm.drawio.svg)

This approach is not what constrained decoding would do. Constrained decoding would validate the tokens from the LLM before letting it pick them. With this approach that picks the usual best token while going trough it character by character and is more flexible that filtering out tokens beforehand.





## Resources

#### LLM in general
- [How does a LLM work](https://en.wikipedia.org/wiki/Maze_generation_algorithm)

**AI usage:** AI (an LLM assistant) was used as a learning tool to understand
concepts needed for the project (e.g. graph/spanning-tree algorithms, A* search,
mypy/flake8 configuration) while the team wrote the code themselves, and to
generate the initial skeleton of this README, which was then filled in and
corrected with project-specific details by the team.
