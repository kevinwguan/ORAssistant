.PHONY: init
init:
	@python3 -m venv .venv && \
		. .venv/bin/activate && \
		pip install -r requirements.txt

.PHONY: init-dev
init-dev: init
	@. .venv/bin/activate && \
		pip install -r requirements-test.txt

.PHONY: format
format:
	@. .venv/bin/activate && \
		ruff format

.PHONY: check
check:
	@. .venv/bin/activate && \
		mypy . && \
		ruff check
