# Intermediate Axis Simulations

Python recreations of the asymmetric disc model described in Veritasium's
video segment from 6:50 to 9:50:

- `01_setup_simulation.py` shows the disc, masses, and principal axes.
- `02_manual_flip_disc.py` lets you rotate the disc around any body axis manually.
- `03_choose_axis_rotation.py` spins the disc around whichever principal axis you choose.
- `04_tennis_racket_effect.py` runs the full torque-free intermediate-axis simulation.

## Run

```bash
cd "/Users/irakli/Progamming/Simulations/Beka/RAGACA"
.venv/bin/python 01_setup_simulation.py
.venv/bin/python 02_manual_flip_disc.py
.venv/bin/python 03_choose_axis_rotation.py
.venv/bin/python 04_tennis_racket_effect.py
```

A local `.venv` with `pygame` has been prepared in this workspace. The entry
scripts automatically re-launch themselves into that environment, so you can
still start them with `python3`.

If you want to run the interpreter directly, use:

```bash
.venv/bin/python 01_setup_simulation.py
```

## Controls

Common:

- `Esc`: close window
- `H`: toggle help/info overlay

`01_setup_simulation.py`:

- `1` / `2` / `3`: highlight small/intermediate/large principal axis

`02_manual_flip_disc.py`:

- `A` / `D`: rotate around x axis
- `W` / `S`: rotate around y axis
- `Q` / `E`: rotate around z axis
- `R`: reset orientation

`03_choose_axis_rotation.py`:

- `1` / `2` / `3`: choose spin axis
- `+` / `-`: increase/decrease angular speed
- `Space`: pause/resume
- `R`: reset orientation

`04_tennis_racket_effect.py`:

- `1`: stable x-axis-biased case
- `2`: unstable intermediate-axis case (tennis-racket effect)
- `3`: stable z-axis-biased case
- `Space`: pause/resume
- `R`: reset to intermediate-axis mode
