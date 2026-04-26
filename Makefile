.PHONY: format lint check install install-dev

format:
	@python3 -m ruff format .
	@python3 -m ruff check --fix .

lint:
	@python3 -m ruff check .

check: lint

install:
	@python3 -m pip install -r requirements.txt

install-dev:
	@python3 -m pip install -r requirements-dev.txt
