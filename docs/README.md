# Dokumentace – EMS (diplomová práce)

Osobní poznámky a studijní dokumentace k vývoji Energy Management Systemu.

## Obsah

### Energetika (doména)

- [Základy FVE](energetika/fve-zaklady.md) – modely slunečního záření, teploty a výkonu

### Influxdb3

- `influxdb3@dc9d4f677ac1:/$ influxdb3 query --database ems "SHOW TABLES" --token $token`

### Alembic

#### Vytvoření migračního skriptu

- `uv run alembic revision --autogenerate -m "Your message."`

### Aplikace migrace

- `uv run alembic upgrade head`

Poznámky:

- Brát aktuální počasí v simulaci PV

  OTE, predikce spotřeby, teplota v domě,
  výroba energie, agregát, akumulovaná teplota v domě
  baterie (písková, elektromobil) -> optimalizace
