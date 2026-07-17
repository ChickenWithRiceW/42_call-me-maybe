ENTRY = src

install:
	uv sync

run: install
	uv run python -m $(ENTRY)

run-prompt: install
	uv run python -m $(ENTRY) -m

debug: install
	uv run python -m pdb $(ENTRY)

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type d -name .mypy_cache -exec rm -rf {} +
	find . -type d -name .pytest_cache -exec rm -rf {} +

lint:
	uv run flake8 $(ENTRY)
	uv run mypy $(ENTRY)

lint-strict:
	uv run flake8 $(ENTRY)
	uv run mypy --strict $(ENTRY)
