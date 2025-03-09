# Space Invaders Game

PYTHON = python3
VENV_DIR = .venv

all: check-venv install run

check-venv:
	@if [ ! -d "$(VENV_DIR)" ]; then \
		echo "Virtual environment not found. Creating..."; \
		$(PYTHON) -m venv $(VENV_DIR); \
	fi

install: check-venv
	@echo "Installing dependencies..."
	$(VENV_DIR)/bin/python -m pip install pygame

run: check-venv
	@echo "Running Space Invaders game..."
	$(VENV_DIR)/bin/python space-invaders.py

clean:
	rm -rf __pycache__ $(VENV_DIR)

