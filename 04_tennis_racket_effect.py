from bootstrap_venv import ensure_local_python

ensure_local_python()

from rigid_body_core import BaseSimulationApp, TorqueFreeBody


class TennisRacketEffect(BaseSimulationApp):
    def __init__(self) -> None:
        super().__init__("Full Tennis Racket Effect")
        self.paused = False
        self.time_elapsed = 0.0
        self.reset_mode("tennis")

    def reset_mode(self, mode: str) -> None:
        moments = self.model.principal_moments
        if mode == "x":
            omega = (4.0, 0.08, 0.0)
            self.highlight_axis = 0
        elif mode == "z":
            omega = (0.0, 0.08, 3.2)
            self.highlight_axis = 2
        else:
            omega = (0.12, 4.6, 0.0)
            self.highlight_axis = 1
        self.body = TorqueFreeBody(moments, omega)
        self.orientation = self.body.orientation
        self.angular_momentum_world = self.body.angular_momentum_world()
        self.time_elapsed = 0.0

    def on_key_press(self, key: str) -> None:
        if key == "space":
            self.paused = not self.paused
        elif key == "r":
            self.reset_mode("tennis")
        elif key == "1":
            self.reset_mode("x")
        elif key == "2":
            self.reset_mode("tennis")
        elif key == "3":
            self.reset_mode("z")

    def update(self, dt: float) -> None:
        if self.paused:
            return
        self.time_elapsed += dt
        substeps = 6
        step = dt / substeps
        for _ in range(substeps):
            self.body.step(step)
        self.orientation = self.body.orientation
        self.angular_momentum_world = self.body.angular_momentum_world()

    def status_lines(self) -> list[str]:
        w1, w2, w3 = self.body.omega_body
        return [
            "Torque-free rigid body with a small perturbation off the intermediate axis.",
            f"body omega = ({w1:.2f}, {w2:.2f}, {w3:.2f})   t = {self.time_elapsed:.1f}s",
            "Press 2 for the unstable intermediate-axis flip, 1 or 3 for stable cases.",
            "Dashed yellow vector is angular momentum. Space pauses. R resets. Esc closes.",
        ]


if __name__ == "__main__":
    TennisRacketEffect().run()
