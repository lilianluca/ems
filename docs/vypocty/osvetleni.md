# Osvětlení

Osvětlení odhaduje, **kolik domácnost spotřebuje na svícení v každé
čtvrthodině.** Výsledek se přičte k [predikci spotřeby](spotreba.md) ze
spotřebičů.

Svícení se do spotřebičů nehodí. Spotřebič má okno, ve kterém běží, a to okno
je každý den stejné. Svítí se ale jen tehdy, když je **někdo doma a zároveň je
tma**. Doma se bývá pořád ve stejnou dobu, ale tma přichází v zimě o pět hodin
dřív než v létě. Proto má svícení vlastní výpočet, navázaný na **dům**, ne na
spotřebič.

## Co o domě víme

Dům se nastavuje na stránce **Nastavení**, ve skupině **Dům**.

| Parametr          | Jednotka         | Význam                                           |
| ----------------- | ---------------- | ------------------------------------------------ |
| Výkon osvětlení   | W                | kolik odebírají světla, která se večer rozsvítí  |
| Doba, kdy je doma | okna od–do hodin | kdy je někdo vzhůru doma, stejně každý den       |
| Poloha lokality   | zem. šířka/délka | už ji lokalita má, podle ní se počítá tma        |

**Výkon osvětlení** je součet příkonů světel, která obvykle svítí zároveň.
Například obývák 40 W, kuchyň 30 W, chodba a koupelna 30 W, další místnosti
50 W, dohromady 150 W. Zadává se přímo ve wattech, bez rozpisu po místnostech.

**Doba, kdy je doma** je jedno nebo víc oken po celých hodinách, například 6–8
a 16–23. Okno smí přecházet přes půlnoc (22–1), stejně jako u spotřebičů.
Víkend se nerozlišuje, okna platí pro všechny dny.

## Výpočet krok za krokem

Výkon osvětlení v jedné čtvrthodině je součin tří čísel:

$$
P_\text{svícení} = \text{výkon osvětlení} \times \text{obsazenost} \times \text{tma}
$$

### 1. Obsazenost

Obsazenost je 1, když čtvrthodina začíná v některém okně, a 0 jinak.

### 2. Tma

Tma je číslo od 0 do 1 a určuje se z **výšky slunce nad obzorem**. Výška se
počítá knihovnou pvlib, kterou systém už používá pro výrobu fotovoltaiky, pro
souřadnice lokality a **střed čtvrthodiny**.

$$
\text{tma} = \min\left(1,\ \max\left(0,\ \frac{6^\circ - \text{výška slunce}}{12^\circ}\right)\right)
$$

| Výška slunce   | Tma           | Co to znamená                               |
| -------------- | ------------- | ------------------------------------------- |
| nad +6°        | 0             | slunce je nad obzorem, nesvítí se           |
| od +6° do −6°  | lineárně 0→1  | soumrak, světla se rozsvěcují postupně      |
| pod −6°        | 1             | konec občanského soumraku, svítí se naplno  |

Proč postupně, a ne naráz při západu slunce:

- **Domácnost nerozsvítí všechna světla najednou.** Nejdřív kuchyň, kam se
  nedostane světlo z okna, obývák až o půl hodiny později.
- **Predikce je očekávaná hodnota**, stejně jako u spotřebičů. Kdy přesně kdo
  rozsvítí, nevíme, a postupný náběh to vyjadřuje.

Odkud jsou hranice:

- **−6° je ustálená definice.** Je to konec **občanského soumraku**
  [[1]](#zdroje). Venku je během občanského soumraku ještě většinou vidět bez
  umělého světla. Pod −6° už ne, a proto tam počítáme se svícením naplno.
- **+6° je vlastní odhad, zdroj pro něj nemáme.** Uvnitř domu je tma dřív než
  venku, takže se rozsvěcuje ještě před západem slunce. Hranice +6° je zvolená
  souměrně k −6°.
- **Skladba „obsazenost × venkovní světlo"** odpovídá uznávanému modelu
  spotřeby na svícení v domácnostech [[2]](#zdroje). Ten bere venkovní světlo
  z měřeného slunečního záření, nebere ho z polohy slunce. Rozsvěcuje se
  v něm, když záření klesne pod práh. Náš výpočet je jeho zjednodušení: místo
  záření bere polohu slunce, a proto nepotřebuje oblačnost.

### 3. Výsledek

Výkon ve wattech se převede na kilowatty a přičte se ke spotřebě ze
spotřebičů v téže čtvrthodině.

Na rozdíl od spotřebičů se svícení **mění po čtvrthodinách**, ne po hodinách.
Soumrak trvá v Praze zhruba hodinu a po celých hodinách by se z něj stal
schod.

### Režim úspor

Svícení se chová jako spotřebič s prioritou **důležité** (2). Vypne ho jen
režim **extrémní**, ostatní režimy ho nechávají. Do neomezené spotřeby
(`unrestricted_load_kw`) se počítá vždy. Viz [režim úspor](rezim-uspor.md).

Priorita svícení je pevná a uživatel ji nemění.

## Příklad

Dům v Praze (50,08° s. š., 14,42° v. d.), výkon osvětlení **150 W**, doma
**6–8** a **16–23**. Čísla jsou spočítaná pvlib a vzorcem výše.

### Zimní odpoledne, 21. prosince

| Čtvrthodina | Výška slunce | Tma  | Doma | Svícení |
| ----------- | -----------: | ---: | :--: | ------: |
| 15:30       |        2,5°  | 0,29 |  ne  |    0 W  |
| 15:45       |        0,8°  | 0,43 |  ne  |    0 W  |
| 16:00       |       −1,5°  | 0,63 |  ano |   94 W  |
| 16:15       |       −3,5°  | 0,79 |  ano |  119 W  |
| 16:30       |       −5,5°  | 0,96 |  ano |  144 W  |
| 16:45       |       −7,6°  | 1,00 |  ano |  150 W  |

Před čtvrtou už se stmívá, ale nikdo není doma, takže se nesvítí. Od čtvrté
svítí skoro naplno a od 16:45 naplno až do 23:00.

### Celý den v různých ročních obdobích

| Den          | Ráno 6–8                  | Večer 16–23            | Za den    |
| ------------ | ------------------------- | ---------------------- | --------- |
| 21. prosince | tma celé ráno             | svítí se od 16:00      | 1,30 kWh  |
| 20. března   | jen kolem šesté (74 W)    | rozsvěcuje se od 18:00 | 0,76 kWh  |
| 21. června   | nesvítí se                | rozsvěcuje se od 21:00 | 0,27 kWh  |

V zimě spotřebuje svícení **pětkrát víc** než v létě, i když domácnost žije
stejně. To je přesně ten rozdíl, který okno u spotřebiče zachytit neumí.

## Kde v kódu

| Co                              | Kde                                                                                                              |
| ------------------------------- | ---------------------------------------------------------------------------------------------------------------- |
| Tma z výšky slunce              | `darkness` v [appliances/lighting.py](../../server/src/appliances/lighting.py)                                   |
| Hranice ±6°                     | `FULL_LIGHT_ELEVATION`, `FULL_DARK_ELEVATION` tamtéž                                                             |
| Svícení po čtvrthodinách        | `generate_lighting_forecast` tamtéž                                                                              |
| Priorita a režim úspor          | `LIGHTING_PRIORITY`, `lighting_runs_in` tamtéž                                                                   |
| Přičtení ke spotřebě            | `ApplianceService.generate_and_store_forecast` v [appliances/service.py](../../server/src/appliances/service.py) |
| Nastavení domu                  | `lighting_power_w`, `occupancy_windows` lokality v [sites/models.py](../../server/src/sites/models.py)           |
| Okno obsazenosti                | `OccupancyWindow` v [sites/schemas.py](../../server/src/sites/schemas.py)                                        |
| Formulář na stránce Nastavení   | [house-form.tsx](../../client/src/features/sites/components/house-form.tsx)                                      |
| Testy podle příkladů výše       | [tests/test_lighting.py](../../server/tests/test_lighting.py)                                                    |

Nová lokalita má výkon osvětlení 0 W a žádná okna, takže se v ní nesvítí, dokud
dům někdo nenastaví. Predikce se přepočítá hned po uložení domu nebo změně
souřadnic.

## Předpoklady a omezení

- **Oblačnost se nepočítá.** Za zamračeného dne se svítí dřív, než říká
  poloha slunce. Předpověď oblačnosti systém má, ale vazba mezi oblačností a
  rozsvícením by byla další odhadnutý parametr.
- **Hranice +6° je odhad bez zdroje.** Skutečný okamžik rozsvícení závisí na
  oknech, orientaci domu a okolní zástavbě.
- **Jeden výkon pro celý dům.** Ve skutečnosti se světla rozsvěcují a zhasínají
  po místnostech, podle toho, kde kdo je.
- **Obsazenost je stejná každý den.** Víkendy, dovolená ani nemoc se
  nerozlišují.
- **Obsazenost je 0, nebo 1.** Doma buď někdo je, nebo není. Kolik lidí, se
  nesleduje.

## Zdroje

1. National Weather Service: [Twilight types](https://www.weather.gov/lmk/twilight-types).
   Definice občanského, nautického a astronomického soumraku (−6°, −12°, −18°).
2. Richardson, I., Thomson, M., Infield, D., Delahunty, A.: _Domestic lighting:
   A high-resolution energy demand model._ Energy and Buildings 41 (7), 2009,
   s. 781–789. DOI [10.1016/j.enbuild.2009.02.010](https://doi.org/10.1016/j.enbuild.2009.02.010).
   Volně dostupná verze v [repozitáři Loughborough University](https://repository.lboro.ac.uk/articles/journal_contribution/Domestic_lighting_a_high-resolution_energy_demand_model/9567218).
