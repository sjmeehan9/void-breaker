"""Phase 5 particle pooling and cap behavior tests."""

from __future__ import annotations

import random

from asterax.app.src.rendering.particle_system import ParticleSystem


def test_particle_pool_cap_and_recycle_behavior() -> None:
    """Particle pool enforces cap and recycles oldest slots when saturated."""
    system = ParticleSystem(rng=random.Random(7), max_particles=30)

    assert system.max_particles == 30
    assert len(system.particles) == 30

    for _ in range(10):
        system.emit_explosion(100.0, 200.0, "large")

    assert system.active_particle_count <= 30
    system.update(10.0)
    assert system.active_particle_count == 0
