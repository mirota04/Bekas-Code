import math

from bootstrap_venv import ensure_local_python

ensure_local_python()

from rigid_body_core import BaseSimulationApp, mat_identity, mat_mul, orthonormalize, rotation_matrix

ROTATION_CONTROLS = (
    ("a", 0),
    ("d", 0),
    ("w", 1),
    ("s", 1),
    ("q", 2),
    ("e", 2),
)


class ManualFlipSimulation(BaseSimulationApp):
    def __init__(self) -> None:
        super().__init__("Manual Flip: Rotate Any Axis")
        self.step_speed = math.radians(120.0)

    def on_key_press(self, key: str) -> None:
        if key == "r":
            self.orientation = mat_identity()

    def update(self, dt: float) -> None:
        angle = self.step_speed * dt
        rotation_by_key = {
            "a": rotation_matrix((1.0, 0.0, 0.0), angle),
            "d": rotation_matrix((1.0, 0.0, 0.0), -angle),
            "w": rotation_matrix((0.0, 1.0, 0.0), angle),
            "s": rotation_matrix((0.0, 1.0, 0.0), -angle),
            "q": rotation_matrix((0.0, 0.0, 1.0), angle),
            "e": rotation_matrix((0.0, 0.0, 1.0), -angle),
        }
        for key, highlight in ROTATION_CONTROLS:
            if key in self.pressed_keys:
                self.orientation = orthonormalize(mat_mul(self.orientation, rotation_by_key[key]))
                self.highlight_axis = highlight
                break

    def status_lines(self) -> list[str]:
        return [
            "Manual control in the body frame.",
            "A/D: rotate around x   W/S: rotate around y   Q/E: rotate around z",
            "R resets the disc. Esc closes the window.",
        ]


if __name__ == "__main__":
    ManualFlipSimulation().run()
