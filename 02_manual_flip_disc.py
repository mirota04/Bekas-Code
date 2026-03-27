import math

from bootstrap_venv import ensure_local_python

ensure_local_python()

from rigid_body_core import BaseSimulationApp, mat_identity, mat_mul, orthonormalize, rotation_matrix


class ManualFlipSimulation(BaseSimulationApp):
    def __init__(self) -> None:
        super().__init__("Manual Flip: Rotate Any Axis")
        self.step_speed = math.radians(120.0)

    def on_key_press(self, key: str) -> None:
        if key == "r":
            self.orientation = mat_identity()

    def update(self, dt: float) -> None:
        angle = self.step_speed * dt
        if "a" in self.pressed_keys:
            self.orientation = orthonormalize(mat_mul(self.orientation, rotation_matrix((1.0, 0.0, 0.0), angle)))
            self.highlight_axis = 0
        elif "d" in self.pressed_keys:
            self.orientation = orthonormalize(mat_mul(self.orientation, rotation_matrix((1.0, 0.0, 0.0), -angle)))
            self.highlight_axis = 0
        elif "w" in self.pressed_keys:
            self.orientation = orthonormalize(mat_mul(self.orientation, rotation_matrix((0.0, 1.0, 0.0), angle)))
            self.highlight_axis = 1
        elif "s" in self.pressed_keys:
            self.orientation = orthonormalize(mat_mul(self.orientation, rotation_matrix((0.0, 1.0, 0.0), -angle)))
            self.highlight_axis = 1
        elif "q" in self.pressed_keys:
            self.orientation = orthonormalize(mat_mul(self.orientation, rotation_matrix((0.0, 0.0, 1.0), angle)))
            self.highlight_axis = 2
        elif "e" in self.pressed_keys:
            self.orientation = orthonormalize(mat_mul(self.orientation, rotation_matrix((0.0, 0.0, 1.0), -angle)))
            self.highlight_axis = 2

    def status_lines(self) -> list[str]:
        return [
            "Manual control in the body frame.",
            "A/D: rotate around x   W/S: rotate around y   Q/E: rotate around z",
            "R resets the disc. Esc closes the window.",
        ]


if __name__ == "__main__":
    ManualFlipSimulation().run()
