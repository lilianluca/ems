# Dokumentace – EMS (diplomová práce)

Osobní poznámky a studijní dokumentace k vývoji Energy Management Systemu.

## Obsah

### Energetika (doména)

- [Základy FVE](energetika/fve-zaklady.md) – modely slunečního záření, teploty a výkonu

### Optimalizace

- [LP model řízení baterie](optimalizace/lp-model.md) – volba přístupu, formulace úlohy, pasti

### Úložiště časových řad

Ceny, počasí, predikce a stav baterie jsou od 29. 9. 2026 v Postgresu jako
hypertabulky TimescaleDB (`ote_spot_price`, `weather_forecast`,
`pv_generation_forecast`, `load_forecast`, `battery_state`).

Původně byly v InfluxDB 3 Core. Ten nemá kompakci: každý přepis stejného
časového okna (predikce se přepisují každou hodinu na 48 h dopředu) přidal
nové Parquet soubory a dotaz na „dnes + zítra“ po čase narazil na limit
souborů (`--query-file-limit`) – dashboard i simulace baterie přestaly
fungovat. V Postgresu je přepis obyčejný upsert podle `(…_id, time)`.

- Přehled hypertabulek: `SELECT * FROM timescaledb_information.hypertables;`

## Úkolníček

### Vyhodnocení (chybějící kapitola práce)

Implementace stojí, vyhodnocení ne. Úspora 52 Kč spočítaná z predikcí na jednom
dvoudenním okně je ukázka, ne výsledek. V tabulce `ote_spot_price` je přitom
**historie spotových cen od 10. 7. 2026**, takže všechno níž jde udělat bez
jediného čidla.

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

- [ ] **Automatické zálohy Postgresu** – zatím jen ruční `pg_dump` (29. 9. 2026,
      před přechodem na TimescaleDB). Jediný dluh, který může zničit všechno
      naráz; s rostoucí historií roste i sázka.
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
- [ ] Predikce spotřeby zůstává tvarem hodinová – parametry modelu jsou per
      hodina dne, takže se hodnota ve čtyřech krocích opakuje. Zjemnit ji lze až
      lepším tvarem (lichoběžník místo obdélníku přes okno), ne kratším krokem.

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

### Poznámky

#### Výpočet nákupní ceny

doplnit...

#### Výpočet prodejní ceny

spot_czk_mwh / 1000 \* settings.export_factor

1. Převod mwh na kwh
2. Distribuční poplatky platíme za to, že nám elektřinu někdo dopraví - když dodáváme elektřinu do sítě tuto službu nevyužíváme, takže neplatíme - a ani nedostáváme zaplaceno za nic jiného než samotnou dodávanou elektřinu
3. DPH ve vzorečku není protože běžná domácnost s fotovoltaikou není plátce DPH
4. Kde se export_factor vezme v reálu?

   | Tvar výkupu                | Typicky                          |
   | :------------------------- | :------------------------------- |
   | Spot × koeficient          | 0,80 až 0,95                     |
   | Spot mínus pevný poplatek  | spot – 0,10 až 0,30 Kč/kWh       |
   | Pevná výkupní cena         | 1 až 2 Kč/kWh bez ohledu na spot |
   | Bez výkupu, přetoky zdarma | –                                |

#### Energetická bilance

- Co do domu přitéká, musí z něj odtéct:

#### Další

Simulovaný dům se řídí predikcí, ne skutečností. Výsledek tedy říká, kolik by strategie ušetřila, kdyby predikce platily. Kolik ušetří doopravdy, řekne až měření ze skutečného střídače. Pro práci je to legitimní, jen to musí být tak pojmenované.

- Brát aktuální počasí v simulaci PV

  OTE, predikce spotřeby, teplota v domě,
  výroba energie, agregát, akumulovaná teplota v domě
  baterie (písková, elektromobil) -> optimalizace
