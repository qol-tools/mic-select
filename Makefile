.PHONY: install uninstall test clean

PLATFORM := $(shell uname | tr '[:upper:]' '[:lower:]')

ifeq (test,$(firstword $(MAKECMDGOALS)))
  TEST_ARGS := $(wordlist 2,$(words $(MAKECMDGOALS)),$(MAKECMDGOALS))
  $(eval $(TEST_ARGS):;@:)
endif

install:
	@if [ "$(PLATFORM)" = "linux" ]; then \
		./linux/ulauncher/install.sh; \
	elif [ "$(PLATFORM)" = "darwin" ]; then \
		./macos/raycast/install.sh; \
	else \
		echo "Error: Unsupported platform: $(PLATFORM)"; \
		exit 1; \
	fi

uninstall:
	@if [ "$(PLATFORM)" = "linux" ]; then \
		./linux/ulauncher/uninstall.sh; \
	elif [ "$(PLATFORM)" = "darwin" ]; then \
		./macos/raycast/uninstall.sh; \
	else \
		echo "Error: Unsupported platform: $(PLATFORM)"; \
		exit 1; \
	fi

PYTHON := $(shell if [ -f .venv/bin/python3 ]; then echo .venv/bin/python3; else echo python3; fi)

test:
	@$(PYTHON) scripts/run-tests.py $(TEST_ARGS)

clean:
	@find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name "node_modules" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name "dist" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
