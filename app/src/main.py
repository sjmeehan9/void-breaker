"""Application entry point for VoidBreaker."""

import os

import arcade
from asterax.app.src.states.combat import CombatPhaseState
from asterax.app.src.window import VoidBreakerWindow


def main() -> None:
    """Create the game window and start the Arcade event loop."""
    window = VoidBreakerWindow()
    if os.environ.get("VOIDBREAKER_PERF_MODE", "0") == "1":
        perf_duration = float(os.environ.get("VOIDBREAKER_PERF_DURATION", "60"))
        perf_output_path = os.environ.get("VOIDBREAKER_PERF_OUTPUT")
        perf_seed = int(os.environ.get("VOIDBREAKER_PERF_SEED", "1337"))
        window.state_machine.switch_state(
            CombatPhaseState(
                window.state_machine,
                perf_stress_mode=True,
                perf_duration_seconds=perf_duration,
                perf_output_path=perf_output_path,
                perf_seed=perf_seed,
            )
        )
    arcade.run()


if __name__ == "__main__":
    main()
