# Saliency maps and calibration on PneumoniaMNIST

Code and results for two notes:

- *Do saliency maps explain anything? Randomization tests on chest X-rays*
- *Calibrating a CNN on chest X-rays: how much temperature scaling fixes, and where it stops*

Data: PneumoniaMNIST from MedMNIST v2 (`pip install medmnist`), sizes 28, 64 and 128.

| File | What it does |
|---|---|
| `train.py` | ResNet-18 from scratch at 128 px. `--seed 0..4` real labels, `--seed 0..2 --shuffle` shuffled labels |
| `sanity.py` | Cascading randomization, shuffled-label and seed-to-seed comparisons for four saliency methods |
| `summarize.py` | Means and 95% bootstrap intervals → `results/sanity_summary.json` |
| `calibration.py` | ECE before and after temperature scaling, at 128, 64 and 28 px |
| `calibration_check.py` | Errors by class, prevalence correction, and the half-test-set oracle |
| `figures.py` | The figures of both notes, in English and Spanish |

Checkpoints are written outside this folder (`RUNS` in `train.py`) because of their size.
GPU operations on Apple silicon are not fully deterministic, so a rerun gives close numbers, not identical ones.
