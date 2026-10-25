# Predikce spotřeby

Predikce spotřeby odhaduje, **kolik bude domácnost odebírat v každé čtvrthodině
příštích 48 hodin.** Plán baterie z ní pozná, kdy bude energie chybět a kdy jí
bude přebývat.

Systém nemá měření skutečné spotřeby. Predikci proto skládá ze **seznamu
spotřebičů**, které uživatel zadá na stránce Spotřebiče: u každého řekne, jaký má
příkon a kdy obvykle běží.

## Očekávaná hodnota, ne simulace

Predikce neříká, kdy přesně se co zapne. Říká, **kolik spotřebič průměrně
odebírá** v dané hodině, když se vezme v úvahu, jak často a jak dlouho běží.

Rychlovarná konvice má příkon 2 000 W a vaří tři minuty, jednou za ráno někdy
mezi šestou a osmou. Skutečná spotřeba je krátká špička 2 000 W, ale nikdo neví,
ve kterou minutu. Predikce místo toho rozprostře energii té jedné várky rovnoměrně
přes celé okno 6–8 hodin. Vyjde nízká, ale stálá hodnota.

Pro plán baterie je to správná otázka. Ten nepotřebuje vědět, ve kterou minutu
se zapne konvice. Potřebuje vědět, kolik energie domácnost v dané době spotřebuje.

## Co o spotřebiči víme

| Parametr            | Jednotka | Význam                                                               |
| ------------------- | -------- | -------------------------------------------------------------------- |
| Příkon              | W        | kolik odebírá, když běží                                             |
| Pohotovostní příkon | W        | kolik odebírá, když neběží, ale je zapojený                          |
| Chování             | –        | jeden ze čtyř druhů popsaných níže                                   |
| Priorita            | 1–4      | jak moc je pro domácnost důležitý, viz [režim úspor](rezim-uspor.md) |

Příkon se zadává ve **wattech**, protože tak je uvedený na štítku spotřebiče.
Zbytek systému počítá v kilowattech, převod je na konci výpočtu.

## Čtyři druhy chování

### Stálý odběr

Spotřebič běží pořád se stejným příkonem. Typicky router nebo oběhové čerpadlo.

$$
P = \text{příkon}
$$

Router s příkonem 10 W počítá predikce jako 10 W v každé hodině. Pohotovostní
příkon se u stálého odběru nepoužívá, protože spotřebič nikdy nestojí.

### Cyklický

Spotřebič střídá běh a klid. Typicky lednice nebo mraznička: kompresor chvíli
běží, pak stojí.

Uživatel zadá, jak dlouho běh a klid trvají, vždy jako rozsah od–do v minutách.
Z průměrných délek se spočítá, jakou část času spotřebič běží:

$$
\text{podíl běhu} = \frac{\text{průměrný běh}}{\text{průměrný běh} + \text{průměrný klid}}
$$

Po zbytek času odebírá pohotovostní příkon:

$$
P = \text{příkon} \times \text{podíl běhu} + \text{pohotovostní příkon} \times (1 - \text{podíl běhu})
$$

**Špičky.** V hodinách, kdy je doma víc lidí a lednice se častěji otvírá, běží
kompresor víc. Podíl běhu se v nich vynásobí 1,3, nejvýš však na 1, tedy na stálý
běh.

| Den        | Hodiny špiček      |
| ---------- | ------------------ |
| Všední den | 6–8, 17–20         |
| Víkend     | 8–10, 11–13, 17–20 |

**Příklad.** Lednice 120 W, pohotovostní příkon 5 W, běh 20–30 minut, klid
40–50 minut.

| Krok                 | Výpočet                 | Výsledek   |
| -------------------- | ----------------------- | ---------- |
| Průměrný běh         | (20 + 30) / 2           | 25 min     |
| Průměrný klid        | (40 + 50) / 2           | 45 min     |
| Podíl běhu           | 25 / (25 + 45)          | 0,357      |
| Mimo špičku          | 120 × 0,357 + 5 × 0,643 | **46,1 W** |
| Podíl běhu ve špičce | 0,357 × 1,3             | 0,464      |
| Ve špičce            | 120 × 0,464 + 5 × 0,536 | **58,4 W** |

### Plánovaný

Spotřebič běží v daných časových oknech. Typicky bojler v nočním proudu nebo
nabíjení auta.

Uživatel zadá jedno nebo víc oken. U každého:

- **od a do:** celé hodiny, ve kterých spotřebič může běžet,
- **pravděpodobnost:** jak často v okně opravdu poběží, v procentech,
- **délka běhu:** rozsah od–do v minutách.

Očekávaná doba běhu se rozprostře rovnoměrně přes celé okno. V každé hodině okna
pak spotřebič odebírá:

$$
P = \text{příkon} \times \frac{\text{pravděpodobnost} \times \text{průměrná délka běhu}}{\text{délka okna}} + \text{pohotovostní příkon}
$$

Zlomek je **podíl hodiny, po který spotřebič v průměru běží.** Nemůže být větší
než 1. Spotřebič neběží víc než celou hodinu, i kdyby zadané hodnoty vyšly jinak.

Mimo okna odebírá jen pohotovostní příkon.

**Příklad.** Bojler 2 000 W, okno 22–6 hodin, pravděpodobnost 100 %, běh
120–180 minut.

| Krok                | Výpočet              | Výsledek  |
| ------------------- | -------------------- | --------- |
| Délka okna          | od 22 do 6 hodin     | 8 h       |
| Průměrná délka běhu | (120 + 180) / 2 / 60 | 2,5 h     |
| Podíl hodiny        | 1,0 × 2,5 / 8        | 0,3125    |
| V každé hodině okna | 2 000 × 0,3125       | **625 W** |
| Mimo okno           |                      | **0 W**   |

### Na vyžádání

Spotřebič spouští člověk, když ho potřebuje. Typicky myčka, pračka nebo trouba.

Počítá se stejně jako plánovaný spotřebič. Jediný rozdíl je **počet spuštění v
okně**: kolikrát se v jednom okně spotřebič nejvýš spustí.

$$
P = \text{příkon} \times \frac{\text{pravděpodobnost} \times \text{počet spuštění} \times \text{průměrná délka běhu}}{\text{délka okna}} + \text{pohotovostní příkon}
$$

**Příklad.** Myčka 1 500 W, pohotovostní příkon 2 W, okno 19–23 hodin,
pravděpodobnost 80 %, jedno spuštění, běh 90–120 minut.

| Krok                | Výpočet             | Výsledek  |
| ------------------- | ------------------- | --------- |
| Délka okna          | od 19 do 23 hodin   | 4 h       |
| Průměrná délka běhu | (90 + 120) / 2 / 60 | 1,75 h    |
| Podíl hodiny        | 0,8 × 1 × 1,75 / 4  | 0,35      |
| V každé hodině okna | 1 500 × 0,35 + 2    | **527 W** |
| Mimo okno           |                     | **2 W**   |

### Kontrola: kolik spotřebič spotřebuje za den

U plánovaných spotřebičů a spotřebičů na vyžádání jde výsledek snadno ověřit.
Energie za den nezávisí na délce okna, protože se jen rozprostře:

$$
\text{energie za den} = \text{příkon} \times \text{pravděpodobnost} \times \text{počet spuštění} \times \text{průměrná délka běhu} + 24 \times \text{pohotovostní příkon}
$$

U myčky: 1 500 × 0,8 × 1 × 1,75 + 24 × 2 = 2 100 + 48 = **2 148 Wh**. Tolik vyjde
i součtem 24 hodinových hodnot.

### Časová okna

- **Okno může přecházet přes půlnoc.** Okno „22–6" znamená od 22 hodin do 6
  ráno, tedy 8 hodin. Okno se stejným začátkem a koncem zadat nejde, protože by
  nebylo jasné, jestli znamená nic, nebo celý den.
- **Okna se sčítají.** Má-li spotřebič dvě okna, která se překrývají, v
  překryvu se započítá obojí.
- **Pohotovostní příkon platí pořád**, v oknech i mimo ně, a započítá se jednou.

## Spotřeba celé lokality

### Krok 1: spotřebiče, které se počítají

Do predikce se započítají spotřebiče, které povoluje [režim úspor](rezim-uspor.md)
lokality. V běžném režimu všechny.

Zároveň se spočítá i **neomezená spotřeba**, tedy se všemi spotřebiči. Plán
pracuje s omezenou, neomezená slouží k výpočtu toho, kolik režim úspor ušetřil.

### Krok 2: součet

Pro každou čtvrthodinu se sečte očekávaný příkon všech započítaných spotřebičů a
převede se na kilowatty:

$$
\text{spotřeba [kW]} = \frac{\sum_{\text{spotřebiče}} P \text{ [W]}}{1000}
$$

Rozhoduje **pražská** hodina a den v týdnu. Čtyři čtvrthodiny jedné hodiny mají
stejnou hodnotu, protože všechny parametry modelu jsou po hodinách.

### Krok 3: osvětlení

K součtu se přičte [osvětlení](osvetleni.md) domu. Do neomezené spotřeby vždy,
do omezené jen v režimech, které svícení nechávají, tedy ve všech kromě
extrémního. Osvětlení jako jediné mění hodnotu i uvnitř hodiny, protože se řídí
soumrakem.

## Příklad: domácnost se čtyřmi spotřebiči

Lednice, router, bojler a myčka z příkladů výše, všední den. Hodnoty jsou v
wattech a jsou spočítané funkcí z kódu.

| Hodiny         | Lednice | Router | Bojler | Myčka |    Celkem |
| -------------- | ------: | -----: | -----: | ----: | --------: |
| 0–6            |      46 |     10 |    625 |     2 |   **683** |
| 6–8 (špička)   |      58 |     10 |      – |     2 |    **70** |
| 8–17           |      46 |     10 |      – |     2 |    **58** |
| 17–19 (špička) |      58 |     10 |      – |     2 |    **70** |
| 19–20 (špička) |      58 |     10 |      – |   527 |   **595** |
| 20–22          |      46 |     10 |      – |   527 |   **583** |
| 22–23          |      46 |     10 |    625 |   527 | **1 208** |
| 23–24          |      46 |     10 |    625 |     2 |   **683** |

Za celý den to dělá **8,56 kWh**: lednice 1,17, router 0,24, bojler 5,00 a myčka
2,15 kWh.

Profil ukazuje, jak predikce vypadá: hladké schody po hodinách, žádné špičky. Noc
táhne bojler, večer myčka, přes den skoro nic.

## Kdy se predikce počítá

- **Každou hodinu v :15** pro všechny lokality.
- **Hned po změně režimu úspor**, nastavení domu nebo souřadnic lokality.
- **Ručně** tlačítkem pro přepočet predikcí.

Pokaždé se spočítá 48 hodin od aktuální čtvrthodiny a přepíše předchozí hodnoty
pro tytéž čtvrthodiny. Ukládá se do tabulky `load_forecast`, sloupce `load_kw` a
`unrestricted_load_kw`.

## Kde to je v kódu

| Co                                      | Kde                                                                                                              |
| --------------------------------------- | ---------------------------------------------------------------------------------------------------------------- |
| Příkon jednoho spotřebiče v dané hodině | `expected_hourly_power_w` v [appliances/forecast.py](../../server/src/appliances/forecast.py)                    |
| Plánované a na vyžádání                 | `_windowed_expected_power` tamtéž                                                                                |
| Hodiny špiček                           | `WEEKDAY_PEAKS`, `WEEKEND_PEAKS`, `PEAK_FACTOR` tamtéž                                                           |
| Součet za lokalitu                      | `generate_load_forecast` tamtéž                                                                                  |
| Výběr podle režimu úspor                | `appliances_running_in` tamtéž                                                                                   |
| Osvětlení                               | `generate_lighting_forecast` v [appliances/lighting.py](../../server/src/appliances/lighting.py)                 |
| Výpočet a uložení                       | `ApplianceService.generate_and_store_forecast` v [appliances/service.py](../../server/src/appliances/service.py) |
| Pravidelné spouštění                    | `forecast-load` v [core/celery_app.py](../../server/src/core/celery_app.py)                                      |
| Parametry chování                       | [appliances/schemas.py](../../server/src/appliances/schemas.py)                                                  |

Výpočet příkonu spotřebičů zatím nemá vlastní testy. Testovaný je výběr
spotřebičů podle režimu úspor a osvětlení.

## Předpoklady a omezení

- **Spotřeba je jen tak dobrá, jak dobře jsou zadané spotřebiče.** Co uživatel
  nezadá, v predikci není. Typicky drobné spotřebiče, které nikdo nepočítá.
- **Spotřebiče neznají roční období ani počasí.** Spotřebič odebírá v lednu
  stejně jako v červenci. Roční období zná jen [osvětlení](osvetleni.md); topení
  zatím chybí úplně.
- **Víkend ovlivňuje jen cyklické spotřebiče**, a to jen tím, že mají jiné hodiny
  špiček. Plánované spotřebiče a spotřebiče na vyžádání mají stejná okna každý
  den.
- **Hodiny špiček jsou pevné** a stejné pro všechny domácnosti.
- **Rozlišení je po hodinách.** Okna začínají a končí v celých hodinách a
  čtvrthodiny jedné hodiny mají stejnou hodnotu.
- **Z rozsahu se bere jen průměr.** Délka běhu 90–120 minut se počítá jako 105
  minut. Rozptyl kolem průměru predikce nezná.
- **Zadaný příkon se bere doslova.** Štítkový příkon bývá maximum a skutečný
  odběr nižší. Kdo chce počítat se skutečným odběrem, musí ho zadat.
