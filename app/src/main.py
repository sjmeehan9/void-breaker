"""Application entry point for VoidBreaker."""

import arcade
from asterax.app.src.window import VoidBreakerWindow


def main() -> None:
    """Create the game window and start the Arcade event loop."""
    VoidBreakerWindow()
    arcade.run()


if __name__ == "__main__":
    main()
