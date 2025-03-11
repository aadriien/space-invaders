# Space Invaders Game

PYTHON = python3
VENV_DIR = .venv

all: install run 

check-venv:
	@if [ ! -d "$(VENV_DIR)" ]; then \
		$(PYTHON) -m venv $(VENV_DIR); \
	fi

install: check-venv
	@$(VENV_DIR)/bin/python -m pip install --upgrade pip -q
	@$(VENV_DIR)/bin/python -m pip show pygame > /dev/null 2>&1 || { \
		$(VENV_DIR)/bin/python -m pip install -q pygame; \
	}

run: check-venv
	@$(VENV_DIR)/bin/python space-invaders.py > /dev/null 2>&1

clean:
	rm -rf __pycache__ $(VENV_DIR)

