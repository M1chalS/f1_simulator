# Symulator okrążenia bolidu F1

Symulator ruchu bolidu Formuły 1 napisany w Pythonie z pełną fizyką zakrętów, hamowaniem i siłami aerodynamicznymi.

## 🎯 Cel projektu

Symulator demonstruje praktyczne zastosowanie:
- Kinematyki i dynamiki ruchu
- Sił aerodynamicznych (opór i docisk)
- Ruchu po okręgu (siła dośrodkowa)
- Ograniczeń przyczepności

## 📦 Instalacja

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## 🚀 Uruchomienie

### Symulacja podstawowa

Tor domyślny z wykresami:
```bash
python main.py
```
Bez wykresów:
```bash
python main.py --no-plot
```
Wybór toru:
```bash
python main.py --track data/monaco.json
```
Krok czasowy 5ms:
```bash
python main.py --dt 0.005
```

### Narzędzia pomocnicze
Ogólna demonstracja symulatora:
```bash
python demo.py
```
Analiza prędkości w zakrętach:
```bash
python test_corner_speeds.py
```
Porównanie wszystkich torów:
```bash
python compare_tracks.py
```

## 🏁 Dostępne tory

| Tor                | Długość | Charakterystyka                    |
|--------------------|---------|------------------------------------|
| `data/tracks.json` | 1978 m  | Tor testowy (2 zakręty)            |
| `data/monaco.json` | 2478 m  | Wolny, techniczny (6 zakrętów)     |
| `data/monza.json`  | 4906 m  | Szybki, długie proste (5 zakrętów) |

## 🔬 Model fizyczny

### Podstawowe wzory:
- **II zasada Newtona:** `a = F / m`
- **Opór aerodynamiczny:** `F_drag = 0.5 · ρ · Cd · A · v²`
- **Docisk aerodynamiczny:** `F_downforce = 0.5 · ρ · CL · A · v²`
- **Maksymalna prędkość w zakręcie:** `mv²/r ≤ μ(mg + F_downforce)`
- **Droga hamowania:** `s = (v_f² - v_i²) / (2a)`

### Zasady ruchu:
- **Ruch po prostej:** przyspieszanie z uwzględnieniem oporu
- **Automatyczne hamowanie** przed zakrętami
- **Regulacja prędkości** w zakręcie (przyspieszanie/hamowanie)

### Parametry bolidu (klasa `Car`)
```python
mass = 798.0 kg                    # masa minimalna F1
engine_force = 8000.0 N            # siła napędowa
drag_coefficient = 0.9             # współczynnik oporu
lift_coefficient = 3.0             # współczynnik docisku
frontal_area = 1.5 m²              # pole czołowe
tire_friction = 1.7                # przyczepność opon
max_braking_force = 40000.0 N      # max siła hamowania
```