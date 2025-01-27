# OreSat GPS Software

Software for OreSat GPS card.

## Quickstart

Install dependenies

```bash
pip install .[dev]
```

Generate Code

```bash
./gen.py
```

Run the GPS app

```bash
python3 -m oresat_gps
```

Run the GPS app with mocked hardware

```bash
python3 -m oresat_gps -m
