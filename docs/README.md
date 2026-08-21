# Dokumentace – EMS (diplomová práce)

Osobní poznámky a studijní dokumentace k vývoji Energy Management Systemu.

## Obsah

### Energetika (doména)

- [Základy FVE](energetika/fve-zaklady.md) – modely slunečního záření, teploty a výkonu

### Influxdb3

- `influxdb3@dc9d4f677ac1:/$ influxdb3 query --database ems "SHOW TABLES" --token $token`

Poznámky:

- Brát aktuální počasí v simulaci PV

  OTE, predikce spotřeby, teplota v domě,
  výroba energie, agregát, akumulovaná teplota v domě
  baterie (písková, elektromobil) -> optimalizace
