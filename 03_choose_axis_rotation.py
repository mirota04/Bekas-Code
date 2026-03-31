from bootstrap_venv import ensure_local_python

ensure_local_python()

from rigid_body_core import BaseSimulationApp, mat_identity, mat_mul, orthonormalize, rotation_matrix


AXES = {
    0: ((1.0, 0.0, 0.0), "x / smallest inertia"),
    1: ((0.0, 1.0, 0.0), "y / intermediate inertia"),
    2: ((0.0, 0.0, 1.0), "z / largest inertia"),
}
AXIS_BY_KEY = {"1": 0, "2": 1, "3": 2}
SPEED_STEP = 0.5
MIN_SPEED = 0.5
DEFAULT_SPEED = 3.0


class ChosenAxisRotation(BaseSimulationApp):
    def __init__(self) -> None:
        super().__init__("Chosen Axis Rotation")
        self.axis_index = 0
        self.current_axis = AXES[self.axis_index][0]
        self.current_axis_label = AXES[self.axis_index][1]
        self.speed = DEFAULT_SPEED
        self.paused = False
        self.highlight_axis = self.axis_index

    def on_key_press(self, key: str) -> None:
        if key in AXIS_BY_KEY:
            self.axis_index = AXIS_BY_KEY[key]
            self.current_axis = AXES[self.axis_index][0]
            self.current_axis_label = AXES[self.axis_index][1]
            self.highlight_axis = self.axis_index
        elif key in {"plus", "equal"}:
            self.speed += SPEED_STEP
        elif key in {"minus", "underscore"}:
            self.speed = max(MIN_SPEED, self.speed - SPEED_STEP)
        elif key == "space":
            self.paused = not self.paused
        elif key == "r":
            self.orientation = mat_identity()

    def update(self, dt: float) -> None:
        if self.paused:
            return
        self.orientation = orthonormalize(mat_mul(self.orientation, rotation_matrix(self.current_axis, self.speed * dt)))

    def status_lines(self) -> list[str]:
        return [
            f"Current axis: {self.current_axis_label}",
            f"Spin speed: {self.speed:.1f} rad/s",
            "1 / 2 / 3 chooses the axis. +/- changes speed. Space pauses. R resets.",
        ]


if __name__ == "__main__":
    ChosenAxisRotation().run()
