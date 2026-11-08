.PHONY: verify install test

verify: install test

install:
	python -m pip install -e ".[dev]"

test:
	python -m pytest -q
