# Režim úspor

Režim úspor říká, **jak moc je domácnost ochotná omezit spotřebu, aby
ušetřila.** V běžném režimu běží všechny spotřebiče jako obvykle. V extrémním
běží jen to nejnutnější, tedy lednice a router, a třeba vaření nebo televize ne.

Vedoucí práce tuto funkci označil jako **úrovně rizika**. V aplikaci se jmenuje
režim úspor, protože popisuje, kolik se šetří, ne co se riskuje. V kódu se
úrovně jmenují LOW, MEDIUM, HIGH a EXTREME.

Systém spotřebiče neovládá. Režim úspor je **simulace** toho, co by se stalo,
kdyby se domácnost takhle chovala. Nikomu nic nevypne.

## Úrovně

| Úroveň v kódu | V aplikaci    | Co běží                   |
| ------------- | ------------- | ------------------------- |
| `LOW`         | Běžný         | všechny spotřebiče        |
| `MEDIUM`      | Úsporný       | všechno kromě komfortních |
| `HIGH`        | Velmi úsporný | jen nezbytné a důležité   |
| `EXTREME`     | Extrémní      | jen nezbytné              |

Výchozí úroveň je **LOW**. Lokalita, která režim nikdy nenastavila, se chová
přesně jako dosud.

## Priorita spotřebiče

Která úroveň co vypne, se pozná podle **priority**, kterou má každý spotřebič.
Priorita už v aplikaci existuje, ale dosud neměla význam a nic ji nepoužívalo.
Režim úspor jí význam dává:

| Priorita | Význam    | Příklad                 | LOW | MEDIUM | HIGH | EXTREME |
| -------: | --------- | ----------------------- | :-: | :----: | :--: | :-----: |
|        1 | nezbytné  | lednice, router         |  ✓  |   ✓    |  ✓   |    ✓    |
|        2 | důležité  | vaření, osvětlení       |  ✓  |   ✓    |  ✓   |    –    |
|        3 | běžné     | pračka, myčka           |  ✓  |   ✓    |  –   |    –    |
|        4 | komfortní | televize, herní konzole |  ✓  |   –    |  –   |    –    |

Každé úrovni tedy odpovídá **nejvyšší povolená priorita**:

| Úroveň    | Nejvyšší povolená priorita |
| --------- | -------------------------: |
| `LOW`     |                          4 |
| `MEDIUM`  |                          3 |
| `HIGH`    |                          2 |
| `EXTREME` |                          1 |

Které spotřebiče do které priority patří, rozhoduje uživatel ve formuláři
spotřebiče. Tabulka výše je jen příklad.

**Nový spotřebič má prioritu 3 (běžné).** Přísnější režimy ho tedy vypínají,
dokud uživatel neřekne, že je důležitější. Kdyby výchozí byla 1, každý nově
přidaný spotřebič by byl nezbytný a režim úspor by na něj neměl vliv.

### Jak je priorita uložená

V databázi je priorita celé číslo od 1 do 4, které hlídá i databázové omezení.
Číslo je vhodné, protože se s ním **porovnává**: pravidlo režimu úspor zní
„priorita nejvýš 2" a to se s číslem zapíše přímo.

Aby číslo nebylo záhadné, má každá hodnota v kódu jméno:

| Číslo | Jméno v kódu | Význam    |
| ----: | ------------ | --------- |
|     1 | `ESSENTIAL`  | nezbytné  |
|     2 | `IMPORTANT`  | důležité  |
|     3 | `NORMAL`     | běžné     |
|     4 | `COMFORT`    | komfortní |

Režim úspor naopak je databázový výčet, stejně jako role uživatele nebo typ
zařízení. Neporovnává se přímo, jen se převádí na nejvyšší povolenou prioritu.

## Výpočet

Režim úspor mění jedinou věc: **predikci spotřeby**. Ta se počítá jako součet
očekávaného příkonu všech spotřebičů lokality. Nově se do součtu započítají jen
spotřebiče, které daná úroveň povoluje.

$$
\text{spotřeba} = \sum_{\text{spotřebiče s prioritou } \leq p_{\max}} \text{očekávaný příkon spotřebiče}
$$

kde $p_{\max}$ je nejvyšší povolená priorita úrovně.

Jak se počítá očekávaný příkon jednoho spotřebiče, popisuje dokument o
[predikci spotřeby](spotreba.md). Režim úspor do toho nezasahuje, jen vybírá,
které spotřebiče se sečtou.

Všechno další už funguje beze změny. [Plán podle pravidel](plan-rule-based.md),
[simulace](simulace.md) i [úspory](uspory.md) dostanou nižší spotřebu a počítají
s ní stejně jako dosud.

### Omezení platí pořád

V této verzi platí omezení **celý den**. V režimu EXTREME se televize nepočítá
ani v poledne, kdy svítí slunce a elektřiny je dost. Chytřejší varianta, která
omezuje jen ve chvílích, kdy by se muselo kupovat ze sítě, je možné rozšíření.

## Příklad: domácnost se sedmi spotřebiči

Čísla jsou spočítaná funkcí z kódu, která dnes počítá predikci spotřeby, pro
všední den.

| Spotřebič   | Priorita |   Za den |
| ----------- | -------: | -------: |
| Lednice     |        1 | 1,17 kWh |
| Router      |        1 | 0,23 kWh |
| Varná deska |        2 | 2,50 kWh |
| Osvětlení   |        2 | 0,68 kWh |
| Pračka      |        3 | 1,80 kWh |
| Myčka       |        3 | 2,15 kWh |
| Televize    |        4 | 0,25 kWh |

Spotřeba v jednotlivých úrovních:

| Úroveň    | Započítané spotřebiče             |   Za den | V 19 hodin |
| --------- | --------------------------------- | -------: | ---------: |
| `LOW`     | všech sedm                        | 8,77 kWh |    0,90 kW |
| `MEDIUM`  | bez televize                      | 8,52 kWh |    0,86 kW |
| `HIGH`    | lednice, router, deska, osvětlení | 4,57 kWh |    0,18 kW |
| `EXTREME` | lednice, router                   | 1,40 kWh |    0,07 kW |

Rozdíl mezi úrovněmi závisí na tom, kolik spotřeby mají spotřebiče s nízkou
prioritou. V příkladu ušetří přechod z LOW na MEDIUM jen televizi, tedy málo.
Přechod na HIGH vypne pračku a myčku a spotřeba klesne skoro na polovinu.

## Kolik režim ušetřil

Dnešní úspora říká, kolik ušetřila **baterie** při stejné spotřebě. Režim úspor
ale mění spotřebu samotnou, a to dnešní úspora nezachytí. Kdyby se nic
nezměnilo, ukázal by graf úspor po zapnutí přísnějšího režimu menší úsporu
(baterie má méně co pokrývat), přestože domácnost platí méně.

Proto se celková úspora rozdělí na dvě části:

$$
\underbrace{N_{\text{LOW, bez baterie}} - N_{\text{s baterií}}}_{\text{celkem ušetřeno}}
=
\underbrace{N_{\text{LOW, bez baterie}} - N_{\text{bez baterie}}}_{\text{ušetřeno omezením}}
+
\underbrace{N_{\text{bez baterie}} - N_{\text{s baterií}}}_{\text{ušetřeno baterií}}
$$

| Symbol                        | Význam                                                                            |
| ----------------------------- | --------------------------------------------------------------------------------- |
| $N_{\text{s baterií}}$        | náklad čtvrthodiny se zvoleným režimem a s baterií, jako dosud                    |
| $N_{\text{bez baterie}}$      | náklad se zvoleným režimem, ale bez baterie, jako dosud                           |
| $N_{\text{LOW, bez baterie}}$ | náklad bez baterie a bez omezení, tedy kdyby běžely všechny spotřebiče. **Nové.** |

- **Ušetřeno baterií** je stejné číslo jako dosud. Jeho výpočet se nemění.
- **Ušetřeno omezením** je nové. Říká, kolik domácnost ušetřila tím, že
  spotřebiče nepoužila.
- Obě části se sečtou na **celkovou úsporu**.

V režimu LOW je ušetřeno omezením vždy nula, protože se nic neomezuje.

### Příklad: jedna čtvrthodina

Domácnost z příkladu výše je v režimu HIGH. Je 19:00, fotovoltaika nevyrábí,
nákupní cena je 8,59 Kč/kWh. Baterie má dost energie na to, aby omezenou
spotřebu pokryla celou.

|                          |                Spotřeba |               Náklad čtvrthodiny |
| ------------------------ | ----------------------: | -------------------------------: |
| Bez omezení, bez baterie |                 0,90 kW | 0,90 × 0,25 × 8,59 = **1,94 Kč** |
| S omezením, bez baterie  |                 0,18 kW | 0,18 × 0,25 × 8,59 = **0,39 Kč** |
| S omezením, s baterií    | 0,18 kW, celá z baterie |                         **0 Kč** |

| Část úspory       | Výpočet     |       Kč |
| ----------------- | ----------- | -------: |
| Ušetřeno omezením | 1,94 − 0,39 |     1,55 |
| Ušetřeno baterií  | 0,39 − 0    |     0,39 |
| **Celkem**        | 1,94 − 0    | **1,94** |

## Co se ukládá

**U lokality** nový údaj: zvolená úroveň.

**V predikci spotřeby** (tabulka `load_forecast`) se ke každé čtvrthodině ukládá
vedle omezené spotřeby `load_kw` i neomezená `unrestricted_load_kw`. Plán pracuje
s omezenou, neomezená slouží k vyúčtování.

**Ke každé čtvrthodině** v tabulce `site_energy_balance` tři nové sloupce:

| Sloupec                          | Význam                                    |
| -------------------------------- | ----------------------------------------- |
| `saving_mode`                    | úroveň, která v té čtvrthodině platila    |
| `unrestricted_load_kw`           | spotřeba, kdyby běžely všechny spotřebiče |
| `unrestricted_baseline_cost_czk` | náklad bez baterie a bez omezení          |

Úroveň se ukládá ze stejného důvodu jako strategie: až se bude měnit, půjde
zpětně zjistit, která platila kdy, a úspory porovnat.

Neomezená spotřeba se počítá zároveň s omezenou, stejnou funkcí, jen se všemi
spotřebiči. Ukládá se proto, že predikce spotřeby se každou hodinu přepisuje a
zpětně by už dopočítat nešla.

## Kde se režim nastavuje

Na stránce **Nastavení** lokality, v části Režim úspor. Na stejné stránce je i
název a souřadnice lokality.

- Měnit ho smí **vlastník a správce** lokality. Divákovi server změnu odmítne.
- **Změna platí od teď.** Predikce spotřeby se hned přepočítá a další plán už
  s ní počítá. Minulé čtvrthodiny zůstanou tak, jak byly.

## Kde se výsledek zobrazí

- **Stránka Spotřebiče:** u každého spotřebiče je vidět jeho priorita a jestli
  ho aktuální režim vypíná.
- **Stránka Úspory:** sloupec každého dne je složený z úspory baterií a úspory
  omezením. Nad grafem je součet za měsíc i s rozdělením.
- **Dashboard:** „Dnes ušetřeno" je součet obou částí, s rozdělením pod ním.

V měsíci, kdy režim úspor nic neomezil, se rozdělení neukazuje. Je tam jen
úspora baterií, stejně jako dřív.

## Kde to je v kódu

| Co                                   | Kde                                                                                                                                              |
| ------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------ |
| Úrovně a převod na nejvyšší prioritu | `SavingMode` v [sites/enums.py](../../server/src/sites/enums.py)                                                                                 |
| Priority spotřebičů                  | `AppliancePriority` v [appliances/enums.py](../../server/src/appliances/enums.py)                                                                |
| Výběr spotřebičů podle režimu        | `appliances_running_in` v [appliances/forecast.py](../../server/src/appliances/forecast.py)                                                      |
| Omezená a neomezená predikce         | `ApplianceService.generate_and_store_forecast` v [appliances/service.py](../../server/src/appliances/service.py)                                 |
| Přepočet predikce po změně režimu    | `SiteService.update_site` v [sites/service.py](../../server/src/sites/service.py)                                                                |
| Rozdělení úspory v čtvrthodině       | `step_balance` a `StepBalance.restriction_savings_czk` v [savings/balance.py](../../server/src/savings/balance.py)                               |
| Součty za den a od začátku           | [savings/service.py](../../server/src/savings/service.py)                                                                                        |
| Stránka Nastavení                    | [settings.tsx](../../client/src/routes/_authenticated/sites/$siteId/settings.tsx)                                                                |
| Testy                                | [tests/test_saving_mode.py](../../server/tests/test_saving_mode.py), [tests/test_savings_balance.py](../../server/tests/test_savings_balance.py) |

## Předpoklady a omezení

- **Systém spotřebiče neovládá.** Režim úspor ukazuje, co by se stalo, kdyby se
  domácnost omezila. Skutečné chování domácnosti nezná.
- **Omezení platí celý den**, i ve chvílích, kdy je elektřiny dost.
- **Spotřebič je buď zapnutý, nebo vypnutý.** Režim neumí spotřebič jen omezit,
  například svítit méně.
- **Výsledek stojí na prioritách.** Když má každý spotřebič prioritu 1, režim
  nic nevypne. Spotřebiče přidané před zavedením režimu úspor mají prioritu 1,
  protože to tehdy byla výchozí hodnota, a zůstane jim. Aby na ně režim měl
  vliv, je potřeba jejich priority projít a nastavit.
- **Omezená spotřeba se nepřesouvá.** Vypnutá pračka se neodloží na jindy, její
  spotřeba prostě zmizí. Ve skutečnosti by domácnost prádlo vyprala později.
  Úspora omezením je proto spíš horní odhad.
