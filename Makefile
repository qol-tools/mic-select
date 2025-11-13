.PHONY: install uninstall test test-unit test-integration test-coverage clean format lint type-check check build-raycast test-macos

# OS detection
UNAME := $(shell uname)

# Universal installer - detects OS and runs appropriate script
install:
	@if [ "$(UNAME)" = "Linux" ]; then \
		./scripts/install-linux.sh; \
	elif [ "$(UNAME)" = "Darwin" ]; then \
		./scripts/install-macos.sh; \
	else \
		echo "Error: Unsupported OS: $(UNAME)"; \
		echo "Supported: Linux (Ulauncher), macOS (Raycast)"; \
		exit 1; \
	fi

# Universal uninstaller
uninstall:
	@if [ "$(UNAME)" = "Linux" ]; then \
		./scripts/uninstall-linux.sh; \
	elif [ "$(UNAME)" = "Darwin" ]; then \
		./scripts/uninstall-macos.sh; \
	else \
		echo "Error: Unsupported OS: $(UNAME)"; \
		exit 1; \
	fi

# Build Raycast extension (macOS only)
build-raycast:
	@if [ "$(UNAME)" != "Darwin" ]; then \
		echo "Error: Raycast is only available on macOS"; \
		exit 1; \
	fi
	@echo "Building Raycast extension..."
	@cd macos/raycast && npm install --silent && npm run build
	@echo "✓ Build complete"

test:
	@echo "Running all tests..."
	@if [ -f .venv/bin/pytest ]; then \
		echo "Running Python unit tests..."; \
		.venv/bin/pytest; \
	elif command -v pytest >/dev/null 2>&1; then \
		echo "Running Python unit tests..."; \
		pytest; \
	else \
		echo "⊘ Skipping Python unit tests (pytest not found)"; \
	fi
	@if [ "$(UNAME)" = "Darwin" ]; then \
		echo ""; \
		echo "Running Raycast extension tests..."; \
		cd macos/raycast && python3 test_raycast_cli.py && \
		if [ -f node_modules/.bin/jest ]; then npm run test:unit; else echo "⊘ Skipping Jest tests (not installed)"; fi; \
	fi
	@echo ""
	@echo "✓ All tests completed"

test-unit:
	@if [ -f .venv/bin/pytest ]; then \
		.venv/bin/pytest tests/unit -v; \
	elif command -v pytest >/dev/null 2>&1; then \
		pytest tests/unit -v; \
	else \
		echo "Error: pytest not found. Run 'pip install -r requirements.txt'"; \
		exit 1; \
	fi

test-integration:
	@if [ -f .venv/bin/pytest ]; then \
		.venv/bin/pytest tests/integration -v; \
	elif command -v pytest >/dev/null 2>&1; then \
		pytest tests/integration -v; \
	else \
		echo "Error: pytest not found. Run 'pip install -r requirements.txt'"; \
		exit 1; \
	fi

test-macos:
	@if [ "$$(uname)" = "Darwin" ]; then \
		if [ -f .venv/bin/pytest ]; then \
			.venv/bin/pytest tests/unit/test_macos_audio_service.py -v; \
		elif command -v pytest >/dev/null 2>&1; then \
			pytest tests/unit/test_macos_audio_service.py -v; \
		else \
			echo "Error: pytest not found"; \
			exit 1; \
		fi; \
	else \
		echo "Skipping macOS tests (not on macOS)"; \
	fi

test-coverage:
	@if [ -f .venv/bin/pytest ]; then \
		.venv/bin/pytest --cov=src --cov-report=html --cov-report=term; \
	elif command -v pytest >/dev/null 2>&1; then \
		pytest --cov=src --cov-report=html --cov-report=term; \
	else \
		echo "Error: pytest not found. Run 'pip install -r requirements.txt'"; \
		exit 1; \
	fi

format:
	@.venv/bin/black src tests main.py macos/cli/raycast_cli.py
	@.venv/bin/isort src tests main.py macos/cli/raycast_cli.py

lint:
	@.venv/bin/ruff check src tests main.py macos/cli/raycast_cli.py

type-check:
	@.venv/bin/mypy src main.py macos/cli/raycast_cli.py --ignore-missing-imports

check: format lint type-check test
	@echo "All checks passed"

clean:
	@rm -rf .pytest_cache htmlcov .coverage .mypy_cache .ruff_cache
	@rm -rf macos/raycast/node_modules macos/raycast/dist
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
