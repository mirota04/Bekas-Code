from __future__ import annotations

import math
import os
import time
from dataclasses import dataclass

try:
    import pygame
except ModuleNotFoundError as exc:
    raise SystemExit(
        "This project now uses pygame. Run it with the local environment:\n"
        "  .venv/bin/python 01_setup_simulation.py"
    ) from exc


Vec3 = tuple[float, float, float]
Mat3 = tuple[Vec3, Vec3, Vec3]


BG = "#ffffff"
FG = "#334155"
LIGHT_A = "#8ee7ef"
LIGHT_B = "#8f82ff"
X_COLOR = "#ef6d9a"
Y_COLOR = "#7b90ff"
Z_COLOR = "#a878ef"
L_COLOR = "#facc15"
HIGHLIGHT = "#ffb11f"

WORLD_X: Vec3 = (1.0, 0.0, 0.0)
WORLD_Y: Vec3 = (0.0, 1.0, 0.0)
WORLD_Z: Vec3 = (0.0, 0.0, 1.0)
WORLD_PLANES: tuple[tuple[Vec3, Vec3], ...] = (
    (WORLD_X, WORLD_Y),
    (WORLD_X, WORLD_Z),
    (WORLD_Y, WORLD_Z),
)
AXIS_DEFS: tuple[tuple[int, str, str, Vec3], ...] = (
    (0, X_COLOR, "X", WORLD_X),
    (1, Y_COLOR, "Y", WORLD_Y),
    (2, Z_COLOR, "Z", WORLD_Z),
)
SPECIAL_KEYS: dict[str, str] = {
    "=": "equal",
    "+": "plus",
    "-": "minus",
    "_": "underscore",
}


def pg_color(value: str) -> pygame.Color:
    return pygame.Color(value)


def with_alpha(value: str, alpha: int) -> tuple[int, int, int, int]:
    color = pg_color(value)
    return (color.r, color.g, color.b, alpha)


def v_add(a: Vec3, b: Vec3) -> Vec3:
    return (a[0] + b[0], a[1] + b[1], a[2] + b[2])


def v_scale(v: Vec3, s: float) -> Vec3:
    return (v[0] * s, v[1] * s, v[2] * s)


def dot(a: Vec3, b: Vec3) -> float:
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


def cross(a: Vec3, b: Vec3) -> Vec3:
    return (
        a[1] * b[2] - a[2] * b[1],
        a[2] * b[0] - a[0] * b[2],
        a[0] * b[1] - a[1] * b[0],
    )


def length(v: Vec3) -> float:
    return math.sqrt(dot(v, v))


def normalize(v: Vec3) -> Vec3:
    mag = length(v)
    if mag == 0.0:
        return (0.0, 0.0, 0.0)
    return v_scale(v, 1.0 / mag)


def mat_identity() -> Mat3:
    return (
        (1.0, 0.0, 0.0),
        (0.0, 1.0, 0.0),
        (0.0, 0.0, 1.0),
    )


def mat_vec(m: Mat3, v: Vec3) -> Vec3:
    return (
        dot(m[0], v),
        dot(m[1], v),
        dot(m[2], v),
    )


def mat_mul(a: Mat3, b: Mat3) -> Mat3:
    cols = (
        (b[0][0], b[1][0], b[2][0]),
        (b[0][1], b[1][1], b[2][1]),
        (b[0][2], b[1][2], b[2][2]),
    )
    return (
        (dot(a[0], cols[0]), dot(a[0], cols[1]), dot(a[0], cols[2])),
        (dot(a[1], cols[0]), dot(a[1], cols[1]), dot(a[1], cols[2])),
        (dot(a[2], cols[0]), dot(a[2], cols[1]), dot(a[2], cols[2])),
    )


def rotation_matrix(axis: Vec3, angle: float) -> Mat3:
    ax = normalize(axis)
    x, y, z = ax
    c = math.cos(angle)
    s = math.sin(angle)
    t = 1.0 - c
    return (
        (t * x * x + c, t * x * y - s * z, t * x * z + s * y),
        (t * x * y + s * z, t * y * y + c, t * y * z - s * x),
        (t * x * z - s * y, t * y * z + s * x, t * z * z + c),
    )


def orthonormalize(m: Mat3) -> Mat3:
    x = normalize((m[0][0], m[1][0], m[2][0]))
    y_guess = (m[0][1], m[1][1], m[2][1])
    z = normalize(cross(x, y_guess))
    y = normalize(cross(z, x))
    return (
        (x[0], y[0], z[0]),
        (x[1], y[1], z[1]),
        (x[2], y[2], z[2]),
    )


@dataclass
class DiscModel:
    radius: float = 1.0
    heavy_mass: float = 3.0
    light_mass: float = 1.0

    @property
    def heavy_points(self) -> list[Vec3]:
        r = self.radius
        return [(-r, 0.0, 0.0), (r, 0.0, 0.0)]

    @property
    def light_points(self) -> list[Vec3]:
        r = self.radius
        return [(0.0, -r, 0.0), (0.0, r, 0.0)]

    @property
    def principal_moments(self) -> Vec3:
        r2 = self.radius * self.radius
        i_x = 2.0 * self.light_mass * r2
        i_y = 2.0 * self.heavy_mass * r2
        i_z = 2.0 * (self.heavy_mass + self.light_mass) * r2
        return (i_x, i_y, i_z)

    def rim_points(self, steps: int = 80) -> list[Vec3]:
        pts = []
        for idx in range(steps + 1):
            angle = (2.0 * math.pi * idx) / steps
            pts.append((self.radius * math.cos(angle), self.radius * math.sin(angle), 0.0))
        return pts


class DiscRenderer:
    def __init__(self, surface: pygame.Surface, model: DiscModel, width: int, height: int) -> None:
        self.surface = surface
        self.model = model
        self.width = width
        self.height = height
        self.scale = 175.0
        self.center = (width * 0.52, height * 0.52)
        self.axis_extent = 4.6
        self.plane_extent = 3.7
        self.grid_step = 0.28
        self.title_font = pygame.font.SysFont("Helvetica", 22, bold=True)
        self.body_font = pygame.font.SysFont("Helvetica", 18)
        self.small_font = pygame.font.SysFont("Helvetica", 20, bold=True)
        self.label_font = pygame.font.SysFont("Helvetica", 30, bold=True)

    def _screen_basis(self, world_point: Vec3) -> tuple[float, float]:
        x, y, z = world_point
        sx = self.center[0] + self.scale * (0.92 * x + 0.92 * y)
        sy = self.center[1] + self.scale * (-0.54 * x + 0.54 * y - 1.10 * z)
        return (sx, sy)

    def project(self, world_point: Vec3) -> tuple[float, float, float]:
        x, y = self._screen_basis(world_point)
        depth = 0.35 * world_point[0] - 0.35 * world_point[1] + 1.1 * world_point[2]
        return (x, y, depth)

    def draw_line_alpha(
        self,
        start: tuple[float, float],
        end: tuple[float, float],
        color: tuple[int, int, int, int],
        width: int,
    ) -> None:
        x1, y1 = start
        x2, y2 = end
        pad = width + 2
        min_x = int(math.floor(min(x1, x2) - pad))
        max_x = int(math.ceil(max(x1, x2) + pad))
        min_y = int(math.floor(min(y1, y2) - pad))
        max_y = int(math.ceil(max(y1, y2) + pad))
        local_w = max(1, max_x - min_x + 1)
        local_h = max(1, max_y - min_y + 1)

        overlay = pygame.Surface((local_w, local_h), pygame.SRCALPHA)
        pygame.draw.line(overlay, color, (x1 - min_x, y1 - min_y), (x2 - min_x, y2 - min_y), width)
        self.surface.blit(overlay, (min_x, min_y))

    def draw_vector(self, start: Vec3, end: Vec3, color: str, width: int = 3, dash: tuple[int, int] | None = None) -> None:
        x1, y1, _ = self.project(start)
        x2, y2, _ = self.project(end)
        if dash is None:
            self.draw_line_alpha((x1, y1), (x2, y2), with_alpha(color, 160), width)
            return

        dash_on, dash_off = dash
        total = math.hypot(x2 - x1, y2 - y1)
        if total == 0.0:
            return
        dx = (x2 - x1) / total
        dy = (y2 - y1) / total
        distance = 0.0
        while distance < total:
            seg_start = distance
            seg_end = min(distance + dash_on, total)
            start_pt = (x1 + dx * seg_start, y1 + dy * seg_start)
            end_pt = (x1 + dx * seg_end, y1 + dy * seg_end)
            self.draw_line_alpha(start_pt, end_pt, with_alpha(color, 160), width)
            distance += dash_on + dash_off

    def draw_text(
        self,
        text: str,
        position: tuple[float, float],
        color: str,
        font: pygame.font.Font,
        center: bool = False,
    ) -> None:
        image = font.render(text, True, pg_color(color))
        rect = image.get_rect()
        if center:
            rect.center = (int(position[0]), int(position[1]))
        else:
            rect.topleft = (int(position[0]), int(position[1]))
        self.surface.blit(image, rect)

    def draw_polygon_alpha(self, points: list[tuple[float, float]], fill: tuple[int, int, int, int]) -> None:
        if not points:
            return
        xs = [point[0] for point in points]
        ys = [point[1] for point in points]
        min_x = int(math.floor(min(xs)))
        max_x = int(math.ceil(max(xs)))
        min_y = int(math.floor(min(ys)))
        max_y = int(math.ceil(max(ys)))
        width = max(1, max_x - min_x + 2)
        height = max(1, max_y - min_y + 2)
        temp = pygame.Surface((width, height), pygame.SRCALPHA)
        shifted = [(point[0] - min_x, point[1] - min_y) for point in points]
        pygame.draw.polygon(temp, fill, shifted)
        self.surface.blit(temp, (min_x, min_y))

    def draw_disc(self, orientation: Mat3) -> None:
        rim = [self.project(mat_vec(orientation, body_point)) for body_point in self.model.rim_points(120)]
        pts = [(x, y) for x, y, _ in rim]
        self.draw_polygon_alpha(pts, (255, 211, 71, 255))

        highlight = []
        for point in self.model.rim_points(48):
            local = (
                0.72 * point[0] + 0.18,
                0.58 * point[1] - 0.08,
                0.0,
            )
            highlight.append(self.project(mat_vec(orientation, local)))
        highlight_pts = [(x, y) for x, y, _ in highlight]
        self.draw_polygon_alpha(highlight_pts, (255, 240, 179, 138))

    def draw_plane_grid(self, basis_a: Vec3, basis_b: Vec3) -> None:
        corners_world = [
            v_add(v_scale(basis_a, -self.plane_extent), v_scale(basis_b, -self.plane_extent)),
            v_add(v_scale(basis_a, self.plane_extent), v_scale(basis_b, -self.plane_extent)),
            v_add(v_scale(basis_a, self.plane_extent), v_scale(basis_b, self.plane_extent)),
            v_add(v_scale(basis_a, -self.plane_extent), v_scale(basis_b, self.plane_extent)),
        ]
        corners_screen = [self.project(point) for point in corners_world]
        polygon = [(x, y) for x, y, _ in corners_screen]

        xs = [point[0] for point in polygon]
        ys = [point[1] for point in polygon]
        min_x = int(math.floor(min(xs)))
        max_x = int(math.ceil(max(xs)))
        min_y = int(math.floor(min(ys)))
        max_y = int(math.ceil(max(ys)))
        width = max(1, max_x - min_x + 2)
        height = max(1, max_y - min_y + 2)

        overlay = pygame.Surface((width, height), pygame.SRCALPHA)
        shifted_polygon = [(point[0] - min_x, point[1] - min_y) for point in polygon]
        pygame.draw.polygon(overlay, (246, 247, 251, 180), shifted_polygon)
        pygame.draw.polygon(overlay, (222, 225, 233, 210), shifted_polygon, 1)

        steps = int(round((2.0 * self.plane_extent) / self.grid_step))
        for idx in range(steps + 1):
            value = -self.plane_extent + idx * self.grid_step
            start1 = v_add(v_scale(basis_a, -self.plane_extent), v_scale(basis_b, value))
            end1 = v_add(v_scale(basis_a, self.plane_extent), v_scale(basis_b, value))
            start2 = v_add(v_scale(basis_b, -self.plane_extent), v_scale(basis_a, value))
            end2 = v_add(v_scale(basis_b, self.plane_extent), v_scale(basis_a, value))

            p1 = self.project(start1)
            p2 = self.project(end1)
            p3 = self.project(start2)
            p4 = self.project(end2)

            pygame.draw.line(
                overlay,
                (208, 212, 222, 135),
                (p1[0] - min_x, p1[1] - min_y),
                (p2[0] - min_x, p2[1] - min_y),
                1,
            )
            pygame.draw.line(
                overlay,
                (208, 212, 222, 135),
                (p3[0] - min_x, p3[1] - min_y),
                (p4[0] - min_x, p4[1] - min_y),
                1,
            )

        self.surface.blit(overlay, (min_x, min_y))

    def draw_axis_label(self, text: str, point: Vec3, color: str) -> None:
        sx, sy, _ = self.project(point)
        image = self.label_font.render(text, True, pg_color("#ffffff"))
        rect = image.get_rect(center=(int(sx), int(sy)))
        rect.inflate_ip(22, 12)
        pygame.draw.rect(self.surface, (*pg_color(color)[:3], 230), rect, border_radius=10)
        self.surface.blit(image, image.get_rect(center=rect.center))

    def draw_cube(self, orientation: Mat3, center_body: Vec3, half_size: float = 0.25) -> None:
        corners: list[Vec3] = []
        for dx in (-half_size, half_size):
            for dy in (-half_size, half_size):
                for dz in (-half_size, half_size):
                    local = (center_body[0] + dx, center_body[1] + dy, center_body[2] + dz)
                    corners.append(mat_vec(orientation, local))

        projected = [self.project(point) for point in corners]
        faces = [
            (0, 1, 3, 2),
            (4, 5, 7, 6),
            (0, 1, 5, 4),
            (2, 3, 7, 6),
            (0, 2, 6, 4),
            (1, 3, 7, 5),
        ]
        visible_faces: list[tuple[float, list[tuple[float, float]]]] = []
        for face in faces:
            polygon = [projected[idx] for idx in face]
            depth = sum(point[2] for point in polygon) / len(polygon)
            visible_faces.append((depth, [(point[0], point[1]) for point in polygon]))

        for _, polygon in sorted(visible_faces, key=lambda item: item[0]):
            self.draw_polygon_alpha(polygon, (217, 209, 204, 76))
            pygame.draw.polygon(self.surface, (255, 255, 255, 145), polygon, 1)

    def draw_light_marker(self, orientation: Mat3, point_body: Vec3, color: str) -> None:
        sx, sy, _ = self.project(mat_vec(orientation, point_body))
        radius = 8
        points = []
        for idx in range(6):
            angle = math.pi / 6.0 + idx * (math.pi / 3.0)
            points.append((sx + radius * math.cos(angle), sy + radius * math.sin(angle)))
        self.draw_polygon_alpha(points, (*pg_color(color)[:3], 220))
        pygame.draw.polygon(self.surface, pg_color("#ffffff"), points, 1)

    def draw(
        self,
        orientation: Mat3,
        title: str,
        lines: list[str],
        highlight_axis: int | None = None,
        angular_momentum_world: Vec3 | None = None,
        show_overlay: bool = False,
    ) -> None:
        self.surface.fill(pg_color(BG))
        for basis_a, basis_b in WORLD_PLANES:
            self.draw_plane_grid(basis_a, basis_b)

        self.draw_disc(orientation)
        for point in self.model.heavy_points:
            self.draw_cube(orientation, point, half_size=0.26)
        self.draw_light_marker(orientation, self.model.light_points[0], LIGHT_A)
        self.draw_light_marker(orientation, self.model.light_points[1], LIGHT_B)

        for axis_index, color, label, axis_dir in AXIS_DEFS:
            color_to_use = HIGHLIGHT if highlight_axis == axis_index else color
            width = 3 if highlight_axis == axis_index else 2
            self.draw_vector(v_scale(axis_dir, -self.axis_extent), v_scale(axis_dir, self.axis_extent), color_to_use, width=width)
            self.draw_axis_label(label, v_scale(axis_dir, self.axis_extent * 0.88), color)

        if angular_momentum_world is not None and length(angular_momentum_world) > 0.0 and show_overlay:
            l_dir = normalize(angular_momentum_world)
            self.draw_vector((0.0, 0.0, 0.0), v_scale(l_dir, 1.8), L_COLOR, width=3, dash=(10, 6))
            lx, ly, _ = self.project(v_scale(l_dir, 2.0))
            self.draw_text("angular momentum", (lx, ly), "#946200", self.small_font, center=True)

        if show_overlay:
            panel = pygame.Rect(18, 18, 520, 38 + 24 * len(lines))
            pygame.draw.rect(self.surface, (255, 255, 255, 232), panel, border_radius=12)
            pygame.draw.rect(self.surface, (220, 224, 232), panel, 1, border_radius=12)
            self.draw_text(title, (32, 28), FG, self.title_font)
            for idx, line in enumerate(lines):
                self.draw_text(line, (32, 60 + idx * 24), FG, self.body_font)


class BaseSimulationApp:
    def __init__(self, title: str, width: int = 1040, height: int = 780) -> None:
        self.model = DiscModel()
        self.width = width
        self.height = height
        self.title = title

        pygame.init()
        pygame.display.set_caption(title)
        self.surface = pygame.display.set_mode((width, height))

        self.renderer = DiscRenderer(self.surface, self.model, width, height)
        self.orientation: Mat3 = mat_identity()
        self.highlight_axis: int | None = None
        self.lines: list[str] = []
        self.angular_momentum_world: Vec3 | None = None
        self.pressed_keys: set[str] = set()
        self.show_overlay = False
        self.clock = pygame.time.Clock()
        self.running = True
        self.autoclose_seconds = float(os.environ.get("SIM_AUTOCLOSE_SECONDS", "0") or "0")
        self.start_time = time.perf_counter()

        self.last_time = time.perf_counter()

    def _normalize_key(self, key: int) -> str:
        if key == pygame.K_ESCAPE:
            return "escape"
        if key == pygame.K_SPACE:
            return "space"
        name = pygame.key.name(key).lower()
        if name in SPECIAL_KEYS:
            return SPECIAL_KEYS[name]
        if 32 <= key <= 126:
            return chr(key).lower()
        return name

    def _on_key_press(self, key_code: int) -> None:
        key = self._normalize_key(key_code)
        self.pressed_keys.add(key)
        if key == "h":
            self.show_overlay = not self.show_overlay
        self.on_key_press(key)

    def _on_key_release(self, key_code: int) -> None:
        self.pressed_keys.discard(self._normalize_key(key_code))

    def on_key_press(self, key: str) -> None:
        del key

    def update(self, dt: float) -> None:
        del dt

    def status_lines(self) -> list[str]:
        return []

    def tick(self) -> None:
        now = time.perf_counter()
        dt = min(now - self.last_time, 0.035)
        self.last_time = now
        self.update(dt)
        self.lines = self.status_lines()
        self.renderer.draw(
            orientation=self.orientation,
            title=self.title,
            lines=self.lines,
            highlight_axis=self.highlight_axis,
            angular_momentum_world=self.angular_momentum_world,
            show_overlay=self.show_overlay,
        )
        pygame.display.flip()

    def run(self) -> None:
        try:
            while self.running:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.running = False
                    elif event.type == pygame.KEYDOWN:
                        self._on_key_press(event.key)
                        if event.key == pygame.K_ESCAPE:
                            self.running = False
                    elif event.type == pygame.KEYUP:
                        self._on_key_release(event.key)

                if self.autoclose_seconds > 0.0 and time.perf_counter() - self.start_time >= self.autoclose_seconds:
                    self.running = False

                self.tick()
                self.clock.tick(60)
        finally:
            pygame.quit()


class TorqueFreeBody:
    def __init__(self, moments: Vec3, omega_body: Vec3) -> None:
        self.moments = moments
        self.omega_body = omega_body
        self.orientation: Mat3 = mat_identity()

    def euler_rhs(self, omega: Vec3) -> Vec3:
        i1, i2, i3 = self.moments
        w1, w2, w3 = omega
        return (
            ((i2 - i3) / i1) * w2 * w3,
            ((i3 - i1) / i2) * w3 * w1,
            ((i1 - i2) / i3) * w1 * w2,
        )

    def step(self, dt: float) -> None:
        o1 = self.omega_body
        k1 = self.euler_rhs(o1)
        k2 = self.euler_rhs(v_add(o1, v_scale(k1, 0.5 * dt)))
        k3 = self.euler_rhs(v_add(o1, v_scale(k2, 0.5 * dt)))
        k4 = self.euler_rhs(v_add(o1, v_scale(k3, dt)))

        omega_next = (
            o1[0] + (dt / 6.0) * (k1[0] + 2.0 * k2[0] + 2.0 * k3[0] + k4[0]),
            o1[1] + (dt / 6.0) * (k1[1] + 2.0 * k2[1] + 2.0 * k3[1] + k4[1]),
            o1[2] + (dt / 6.0) * (k1[2] + 2.0 * k2[2] + 2.0 * k3[2] + k4[2]),
        )

        omega_mid = v_scale(v_add(o1, omega_next), 0.5)
        angle = length(omega_mid) * dt
        if angle > 0.0:
            delta = rotation_matrix(omega_mid, angle)
            self.orientation = orthonormalize(mat_mul(self.orientation, delta))
        self.omega_body = omega_next

    def angular_momentum_body(self) -> Vec3:
        i1, i2, i3 = self.moments
        w1, w2, w3 = self.omega_body
        return (i1 * w1, i2 * w2, i3 * w3)

    def angular_momentum_world(self) -> Vec3:
        return mat_vec(self.orientation, self.angular_momentum_body())
