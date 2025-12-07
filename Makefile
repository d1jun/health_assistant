PYTHON ?= python
VENV ?= .venv

.PHONY: install-backend run-backend test backend-format frontend-install frontend-dev

install-backend:
	$(PYTHON) -m venv $(VENV)
	. $(VENV)/bin/activate && pip install -r requirements.txt

run-backend:
	. $(VENV)/bin/activate && uvicorn src.backend.main:app --reload --port 8000

test:
	. $(VENV)/bin/activate && pytest -q

frontend-install:
	cd src/frontend && npm install

frontend-dev:
	cd src/frontend && npm run dev
