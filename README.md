# Symulator okrążenia bolidu F1

Numeryczny symulator ruchu bolidu Formuły 1 napisany w Pythonie.

## Instalacja

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Uruchomienie

```bash
python main.py                 # symulacja toru domyślnego z wykresami
python main.py --no-plot       # bez wykresów
python main.py --track data/tracks.json --dt 0.005
```

## Model fizyczny

- **II zasada Newtona:** `a = F / m`
- **Opór aerodynamiczny:** `F_drag = 0.5 · ρ · Cd · A · v²`
