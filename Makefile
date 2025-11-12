.PHONY: install uninstall test clean

EXTENSION_DIR := $(HOME)/.local/share/ulauncher/extensions/mic-switcher.kmrh47
ICON_URL := https://cdn-icons-png.flaticon.com/512/107/107831.png

install:
	@mkdir -p $(EXTENSION_DIR)
	@cp manifest.json main.py $(EXTENSION_DIR)/
	@cp -r src $(EXTENSION_DIR)/
	@[ -f $(EXTENSION_DIR)/icon.png ] || wget -q -O $(EXTENSION_DIR)/icon.png $(ICON_URL) 2>/dev/null || true
	@echo "Installed. Restart Ulauncher: killall ulauncher && ulauncher &"

uninstall:
	@rm -rf $(EXTENSION_DIR)
	@echo "Uninstalled"

test:
	@.venv/bin/pytest

clean:
	@rm -rf .pytest_cache htmlcov .coverage
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
