"""Tests for the top-level application entry point."""

import asterax.app.src.main as main_module


def test_main_creates_window_and_runs_arcade(monkeypatch) -> None:
    """main should construct the window and start Arcade's run loop."""
    calls: list[str] = []

    class FakeWindow:
        def __init__(self) -> None:
            calls.append("window")

    def fake_run() -> None:
        calls.append("run")

    monkeypatch.setattr(main_module, "VoidBreakerWindow", FakeWindow)
    monkeypatch.setattr(main_module.arcade, "run", fake_run)

    main_module.main()

    assert calls == ["window", "run"]
