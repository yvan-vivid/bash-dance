tooling_venv = "tooling-venv"
poetry = "$(tooling_venv)/bin/poetry"

venv = ".venv"
pytest = ".venv/bin/pytest"
pylint = ".venv/bin/pylint"

.PHONY: all clean test lint

all: test lint

test: .dev
	$(pytest)

lint: .dev
	$(pylint) src/bash_dance tests/bash_dance

.dev: .tooling pyproject.toml poetry.toml
	$(poetry) install
	touch .dev

.tooling: tooling-requirements.txt
	bash setup
	touch .tooling

clean:
	rm -f .tooling .dev
	rm -rf $(venv) $(tooling_venv)
	find . -type d -name '__pycache__'   -prune -exec rm -rf "{}" \+	
	find . -type d -name '.mypy_cache'   -prune -exec rm -rf "{}" \+	
	find . -type d -name '.pytest_cache' -prune -exec rm -rf "{}" \+	
	find . -type d -name '*.egg-info'    -prune -exec rm -rf "{}" \+	
