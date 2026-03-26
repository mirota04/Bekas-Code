from bootstrap_venv import ensure_local_python

ensure_local_python()

from rigid_body_core import BaseSimulationApp, mat_identity


class SetupSimulation(BaseSimulationApp):
    def __init__(self) -> None:
        super().__init__("Setup: Asymmetric Disc")
        self.orientation = mat_identity()
        self.highlight_axis = 1
        self.mode = 1

    def on_key_press(self, key: str) -> None:
        if key in {"1", "2", "3"}:
            self.mode = int(key) - 1
            self.highlight_axis = self.mode

    def status_lines(self) -> list[str]:
        i_x, i_y, i_z = self.model.principal_moments
        return [
            "Terry Tao model from the video: two heavy masses on x, two light masses on y.",
            f"Principal moments: I_x={i_x:.1f}, I_y={i_y:.1f}, I_z={i_z:.1f}",
            "Press 1 / 2 / 3 to highlight the smallest, intermediate, or largest inertia axis.",
            "Orange masses are heavy. Blue masses are light. Esc closes the window.",
        ]


if __name__ == "__main__":
    SetupSimulation().run()
