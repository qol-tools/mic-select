"""Main entry point for Ulauncher extension."""
from src.dependency_injection.container import Container
from src.presentation.ulauncher_adapter import MicSwitcherExtension


def create_extension() -> MicSwitcherExtension:
    """Create and configure the extension."""
    container = Container()
    presenter = container.presenter()
    return MicSwitcherExtension(presenter)


if __name__ == "__main__":
    extension = create_extension()
    extension.run()
