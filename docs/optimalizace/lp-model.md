# Optimalizace řízení baterie (LP)

EMS má z predikcí a cen odvodit **plán**: kdy nabíjet baterii, kdy ji vybíjet, kdy
odebírat ze sítě a kdy do ní dodávat. Tenhle dokument shrnuje volbu přístupu,
formulaci úlohy a pasti, na kterých takový model obvykle padne.

## Volba přístupu

| Přístup                          | Hodí se na                          | Proč (ne)                                                    |
| -------------------------------- | ----------------------------------- | ------------------------------------------------------------ |
| Pravidla (`nabíjej pod cenou X`) | rychlý hack                         | nedívá se dopředu, prahy jsou arbitrární, špatně se obhajuje |
| **Lineární programování (LP)**   | plánování na den dopředu            | ✅ pro daný model **prokazatelně optimální**, řeší se v ms   |
| Dynamické programování           | nelineární modely                   | zbytečná složitost, hůř škáluje na víc úložišť               |
| Genetika, PSO, RL                | nekonvexní úlohy s neznámým modelem | u konvexní úlohy horší výsledek než LP a těžká obhajoba      |

Úloha je lineární — bilance, dynamika nabití i účelová funkce jsou lineární
kombinace rozhodovacích proměnných. LP tedy najde optimum daného modelu a
diskuse se přesouvá tam, kam patří: k tomu, jak dobrý je ten model.

**MPC (model predictive control)** není jiný optimalizátor, ale způsob použití:
plán se přepočítá s každou aktualizací predikce a použije se jen jeho začátek.
V tomhle projektu to zajistí Celery beat, který už predikce obnovuje.

## Formulace

Horizont je rozdělen na kroky délky `Δt`. Indexy `t = 1..T`.

### Vstupy

| Symbol                             | Jednotka | Zdroj                                         |
| ---------------------------------- | -------- | --------------------------------------------- |
| `price_import_t`, `price_export_t` | Kč/kWh   | `ote_spot_price` + tarifní koeficienty        |
| `pv_t`                             | kW       | `pv_generation_forecast`                      |
| `load_t`                           | kW       | `load_forecast`                               |
| `C`                                | kWh      | `BatteryDevice.capacity_kwh`                  |
| `soc_min`, `soc_max`               | –        | `BatteryDevice.min/max_state_of_charge`       |
| `P_ch_max`, `P_dis_max`            | kW       | `BatteryDevice.max_charge/discharge_power_kw` |
| `η`                                | –        | `BatteryDevice.round_trip_efficiency`         |
| `soc_0`                            | kWh      | parametr (neměříme, viz omezení níže)         |
| `P_grid`                           | kW       | limit přípojky                                |

### Rozhodovací proměnné

Pro každý krok, všechny nezáporné:

```
charge_t, discharge_t     [kW]   nabíjecí a vybíjecí výkon
import_t, export_t        [kW]   odběr ze sítě a dodávka do sítě
soc_t                     [kWh]  stav nabití na konci kroku
```

### Omezení

```
energetická bilance:  pv_t + discharge_t + import_t = load_t + charge_t + export_t
stav nabití:          soc_t = soc_{t-1} + (√η · charge_t − discharge_t / √η) · Δt
meze nabití:          C · soc_min ≤ soc_t ≤ C · soc_max
výkon baterie:        charge_t ≤ P_ch_max        discharge_t ≤ P_dis_max
přípojka:             import_t ≤ P_grid          export_t ≤ P_grid
koncová podmínka:     soc_T ≥ soc_0
```

Účinnost cyklu se dělí na `√η` při nabíjení a `√η` při vybíjení. Je to běžné
zjednodušení — obě větve stejně nelze změřit odděleně.

### Účelová funkce

```
min Σ (price_import_t · import_t − price_export_t · export_t) · Δt
```

## Nástroj

**PuLP** (`uv add pulp`) — model se zapisuje skoro jako matematika výše a veze si
solver CBC. Čitelnost je tu argument sama o sobě, protože kód půjde do přílohy práce.

Bez nové závislosti by šla použít `scipy.optimize.linprog(method="highs")`
(scipy je v projektu kvůli pvlib), ale matici omezení si tam skládáte ručně a
výsledek je nečitelná změť indexů.

## Krok horizontu

Krok je **čtvrthodinový** (`STEP` v `core/timerange.py`), tedy 192 kroků na dva
dny. Následuje trh: od října 2025 se denní aukce vypořádává ve čtvrthodinových
blocích a ve stejných blocích se zúčtovává odchylka, takže je to rozlišení, ve
kterém se skutečně pohybují peníze.

Původně se počítalo hodinově a ceny se do hodin průměrovaly. To zahazovalo právě
ten vnitrohodinový rozptyl, kvůli kterému baterie existuje: model, který vidí jen
hodinový průměr, rozprostře vybíjení rovnoměrně přes celou hodinu, místo aby ho
poslal do té jedné drahé čtvrthodiny.

Počasí dodává Open-Meteo ve stejném kroku (nad střední Evropou nativně z ICON-D2,
ne interpolací hodiny), takže i predikce výroby je čtvrthodinová. Jediná řada,
která zůstává hodinová **tvarem**, je predikce spotřeby — všechny její parametry
jsou per hodina dne, takže se hodnota ve čtyřech krocích zopakuje. Není to ztráta
přesnosti při převodu, je to všechno, co ten model ví. Špičatý průběh nevznikne
zjemněním střední hodnoty, ale losováním konkrétních událostí — a to je úloha
simulace domu, ne prediktoru.

## Výstup

Na každý krok `charge`, `discharge`, `soc`, `import`, `export`, souhrnně náklad plánu.

**Součástí výstupu musí být srovnání s referencí** — týž horizont bez baterie:

```
import_t = max(0, load_t − pv_t)
export_t = max(0, pv_t − load_t)
```

Rozdíl nákladů je úspora. Bez ní čísla nic neříkají: „plán je optimální" není
tvrzení, které by šlo obhájit, „za dva dny ušetří 43 Kč oproti provozu bez
řízení" ano.

## Pasti

**Chybějící koncová podmínka.** Bez `soc_T ≥ soc_0` optimalizátor baterii na konci
horizontu vyprázdní — nevidí za horizont, takže je to pro něj energie zadarmo.
Chová se to jako chyba, ale vypadá to jako chytré rozhodnutí.

**Cena odběru ≠ cena dodávky.** Spot je jen část ceny odběru; přičítá se
distribuce, poplatky a DPH. Za dodávku dostáváte typicky jen spot nebo výkupní
cenu. Když se do modelu dosadí obě strany stejné, arbitráž vyjde výrazně
výnosněji, než ve skutečnosti je.

**Chybějící limit přípojky.** Kdyby výkupní cena někdy převýšila nákupní, LP by
odebíral a dodával současně bez omezení. `P_grid` to utne.

**Neznámý počáteční stav nabití.** SoC se neměří. Prototyp ho bere jako parametr
s výchozí hodnotou `C · soc_min`. Je to reálné omezení práce, ne detail — řeší
ho až integrace se střídačem.

**Jednotky.** Ceny Kč/MWh, výkony kW, energie kWh. Jeden faktor tisíc a výsledek
je nesmysl, který přitom vypadá věrohodně. Ceny se převádějí na Kč/kWh hned na
vstupu a dál se v modelu nepřepočítávají.

## Postup implementace

1. **Čistý modul** `src/optimization/model.py` — funkce, která bere seznamy čísel
   a parametry baterie a vrací plán. Bez databáze, bez FastAPI, bez Celery.
2. **Testy na vymyšlených vstupech**, kde je výsledek zřejmý předem:
   konstantní cena → baterie nedělá nic; jedna levná a jedna drahá hodina →
   nabije a vybije; nulová účinnost → nedělá nic.
3. Služba, která načte ceny a predikce z InfluxDB a plán tam uloží
   (měření `optimization_plan`, tag `site_id`).
4. `GET /sites/{site_id}/optimization` pro dashboard.
5. Úloha v Celery beatu po obnovení predikcí.

Body 1 a 2 jsou ta část, která musí být správně. Zbytek je propojení stejného
tvaru, jaký už v projektu existuje u cen a predikcí.
