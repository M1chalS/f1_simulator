# Symulator okrążenia bolidu F1

Symulator ruchu bolidu Formuły 1 napisany w Pythonie z pełną fizyką zakrętów, hamowaniem i zaawansowaną aerodynamiką.

## 🎯 Cel projektu

Symulator demonstruje praktyczne zastosowanie:
- Kinematyki i dynamiki ruchu
- Sił aerodynamicznych (opór i docisk)
- Ruchu po okręgu (siła dośrodkowa)
- Ograniczeń przyczepności
- Konfiguracji aerodynamicznych dostosowanych do torów

## ✨ Funkcje

- ✅ **Pełna fizyka:** II zasada Newtona, siły aerodynamiczne, przyczepność
- ✅ **3 konfiguracje aerodynamiczne:** HIGH DOWNFORCE, LOW DRAG, BALANCED
- ✅ **Telemetria:** prędkość, przyspieszenie, siły aerodynamiczne, stan pojazdu
- ✅ **Wizualizacja:** wykresy prędkości, przyspieszenia, drag, downforce
- ✅ **Porównania:** analiza wpływu setupu aero na czasy okrążeń

## 📦 Instalacja

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## 🚀 Uruchomienie

### Symulacja podstawowa

Tor domyślny (balanced setup):
```bash
python main.py
```

Wybór konfiguracji aerodynamicznej:
```bash
python main.py --aero-config high_downforce
python main.py --aero-config low_drag
python main.py --aero-config balanced
```

Wybór toru:
```bash
python main.py --track data/monaco.json
python main.py --track data/monza.json
```

Wykresy sił aerodynamicznych:
```bash
python main.py --show-aero
```

Precyzyjna symulacja (krok 5ms):
```bash
python main.py --dt 0.005
```

### Narzędzia analizy

Porównanie wszystkich konfiguracji aero na danym torze:
```bash
python compare_aero.py data/monaco.json
python compare_aero.py data/monza.json
```

Porównanie wszystkich torów:
```bash
python compare_tracks.py
```

Analiza prędkości w zakrętach:
```bash
python test_corner_speeds.py
```

Demonstracja ogólna:
```bash
python demo.py
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
- **Regulacja prędkości** w zakręcie (przyspieszanie/hamowanie/utrzymywanie)
- **Wpływ docisku** na maksymalną prędkość w zakrętach