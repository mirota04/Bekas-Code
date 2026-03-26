# Intermediate Axis Simulations

Python recreations of the asymmetric disc model described in Veritasium's
video segment from 6:50 to 9:50:

- `01_setup_simulation.py` shows the disc, masses, and principal axes.
- `02_manual_flip_disc.py` lets you rotate the disc around any body axis manually.
- `03_choose_axis_rotation.py` spins the disc around whichever principal axis you choose.
- `04_tennis_racket_effect.py` runs the full torque-free intermediate-axis simulation.

## Run

```bash
python3 01_setup_simulation.py
python3 02_manual_flip_disc.py
python3 03_choose_axis_rotation.py
python3 04_tennis_racket_effect.py
```

A local `.venv` with `pygame` has been prepared in this workspace. The entry
scripts automatically re-launch themselves into that environment, so you can
still start them with `python3`.

If you want to run the interpreter directly, use:

```bash
.venv/bin/python 01_setup_simulation.py
```
