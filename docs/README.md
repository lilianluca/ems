# Dokumentace – EMS (diplomová práce)

Osobní poznámky a studijní dokumentace k vývoji Energy Management Systemu.

## Obsah

### Energetika (doména)

- [Základy FVE](energetika/fve-zaklady.md) – modely slunečního záření, teploty a výkonu

### Optimalizace

- [LP model řízení baterie](optimalizace/lp-model.md) – volba přístupu, formulace úlohy, pasti

### Influxdb3

- `influxdb3@dc9d4f677ac1:/$ influxdb3 query --database ems "SHOW TABLES" --token $token`

## Úkolníček

### Vyhodnocení (chybějící kapitola práce)

Implementace stojí, vyhodnocení ne. Úspora 52 Kč spočítaná z predikcí na jednom
dvoudenním okně je ukázka, ne výsledek. V InfluxDB je přitom **historie
spotových cen od 10. 7. 2026** (přes 3 400 čtvrthodin), takže všechno níž jde
udělat bez jediného čidla.

- [ ] **Zpětný test** – přehrát optimalizátorem každý uplynulý den a spočítat
      úsporu za celé období. Výstup je rozdělení, ne jedno číslo: průměr na den,
      nejlepší a nejhorší den.
- [ ] **Srovnání s heuristikou** – naimplementovat triviální pravidlo
      („nabíjej 0–5 h, vybíjej ve špičce") a pustit ho na stejných vstupech.
      Odpovídá na otázku, o kolik je optimalizace lepší než zdravý rozum.
- [ ] **Citlivostní analýza** – jak se úspora mění s kapacitou baterie,
      s účinností a s výší distribučních poplatků. Odpovídá na „vyplatí se
      baterie", což je praktičtější otázka než „je plán optimální".

### Provoz

- [ ] **Zálohy Postgresu a InfluxDB** – zatím žádné. Jediný dluh, který může
      zničit všechno naráz; s rostoucí historií roste i sázka.
- [ ] Historie běhů optimalizace (tabulka `job_run` nebo obdoba) – bez ní nejde
      doložit, že systém dlouhodobě šetří.

### Model a data

- [ ] **Import naměřených dat** (CSV z distribuce nebo z portálu výrobce
      střídače) – bez skutečných hodnot nejde ověřit, jestli model sedí, ani
      odhalit špatně zadaný azimut.
- [ ] Skutečné počáteční SoC baterie místo parametru – vyžaduje integraci se
      střídačem.
- [ ] `level` u `ote_spot_price` je tag, ne field – při přepisu hrozí vznik
      druhé série místo aktualizace.
- [ ] Střídač je modelovaný na každém poli FVE zvlášť – u východo-západní
      instalace se sdíleným měničem model nadhodnotí výkon.
- [ ] Optimalizace řídí jen **první** baterii lokality; společné plánování víc
      úložišť (domácí, písková, elektromobil) je rozšíření.
- [ ] Krok optimalizace je hodinový, ceny jsou čtvrthodinové – zjemnění je jen
      převzorkování vstupů.

### Aplikace

- [ ] Role uživatele na lokalitě chybí v `SiteRead` – `VIEWER` proto vidí
      tlačítka, která mu server odmítne.
- [ ] Tokeny `--chart-*` mají stejné hodnoty ve světlém i tmavém motivu –
      první graf s víc sériemi na to narazí.
- [ ] Tarifní parametry jsou globální v `Settings`; patří na lokalitu, protože
      distributor a sazba se liší dům od domu.
- [ ] Předvolby typických spotřebičů (lednice, myčka, bojler…) – nikdo nezná
      duty cycle své lednice zpaměti.
- [ ] `pragueMarketWindow` v klientovi duplikuje `default_market_window` ze
      serveru – čistší by bylo vracet okno v odpovědi API.

Poznámky:

- Brát aktuální počasí v simulaci PV

  OTE, predikce spotřeby, teplota v domě,
  výroba energie, agregát, akumulovaná teplota v domě
  baterie (písková, elektromobil) -> optimalizace
