# Ohřev vody

Výpočet odhaduje, **kolik elektřiny spotřebuje bojler s tepelným čerpadlem v
každé čtvrthodině.** Výsledek se přičte k [predikci spotřeby](spotreba.md).

Bojler s tepelným čerpadlem je zásobník teplé vody, typicky na 200 až 300 litrů,
s malým tepelným čerpadlem nahoře. Teplo bere ze vzduchu v místnosti, kde stojí,
obvykle ve sklepě nebo v technické místnosti. Je to samostatné zařízení, nezávislé
na [tepelném čerpadle pro vytápění](tepelne-cerpadlo.md). To je typu
vzduch-vzduch a vodu ohřívat neumí.

Spotřeba bojleru nezávisí na venkovní teplotě, ale na tom, **kolik teplé vody
domácnost spotřebuje a kdy.**

## Co potřebujeme vědět

Parametr domu, zadává se na stránce **Nastavení** v kartě **Dům**:

| Parametr   | Jednotka | Význam                             |
| ---------- | -------- | ---------------------------------- |
| Počet osob | –        | kolik lidí v domácnosti žije       |

Nová lokalita má 2 osoby.

Parametry bojleru, zadávají se na stránce **Zařízení**:

| Parametr     | Jednotka | Význam                                                   |
| ------------ | -------- | -------------------------------------------------------- |
| Topný faktor | –        | COP podle normy EN 16147 z technického listu             |
| Topný výkon  | kW       | kolik tepla tepelné čerpadlo bojleru dodá, z téhož listu |

Výrobci uvádějí COP podle EN 16147 pro různé teploty nasávaného vzduchu,
například A7, A15 nebo A20 (7, 15 nebo 20 °C). Zadává se hodnota, která nejlépe
odpovídá místnosti, kde bojler stojí: A15 pro chladnější sklep, A20 pro vytápěný
prostor.

Spotřeba bojleru se počítá, jen když má lokalita bojler a aspoň jednu osobu.

Bojler s tepelným čerpadlem se zadává jen na stránce Zařízení. Kdyby byl zadaný
i jako [spotřebič](spotreba.md), ohřev vody by se v predikci započítal dvakrát.
Obyčejný elektrický bojler bez tepelného čerpadla se dál zadává jako spotřebič.

## Výpočet krok za krokem

### 1. Kolik tepla domácnost denně spotřebuje

Rodinný dům spotřebuje podle normy ČSN EN 15316-3-1 **40 až 50 litrů teplé vody
o 60 °C na osobu a den**. Norma počítá se studenou vodou o 13,5 °C
[[1]](#zdroje). Bereme střed rozsahu, 45 litrů.

Ohřát 1 litr vody o 1 °C stojí 1,163 Wh. Je to měrná tepelná kapacita vody
4,186 kJ/(kg·K) převedená na watthodiny, 1 litr vody váží 1 kg. Na jednu osobu
tedy připadá:

$$
Q_\text{osoba} = 45\ \text{l} \times 1{,}163\ \tfrac{\text{Wh}}{\text{l} \cdot \text{K}} \times (60 - 13{,}5)\ \text{K} \approx 2{,}43\ \text{kWh za den}
$$

$$
Q_\text{den} = \text{počet osob} \times 2{,}43\ \text{kWh}
$$

### 2. Kdy se voda odebírá

Rozložení odběrů během dne přebíráme z evropského nařízení o ekodesignu
ohřívačů vody [[2]](#zdroje). To pro zkoušky ohřívačů definuje **odběrové
profily**: v jakém čase se odebere kolik teplé vody. Používáme profil **M**:

| Odběr   | Čas                         | Energie jednoho odběru |
| ------- | --------------------------- | ---------------------: |
| velký   | 7:05 a 21:30                |              1,400 kWh |
| střední | 20:30                       |              0,735 kWh |
| střední | 12:45                       |              0,315 kWh |
| malý    | 19 odběrů mezi 7:00 a 21:15 |              0,105 kWh |

Malé odběry jsou v 7:00, 7:30, 8:01, 8:15, 8:30, 8:45, 9:00, 9:30, 10:30, 11:30,
11:45, 14:30, 15:30, 16:30, 18:00, 18:15, 18:30, 19:00 a 21:15.

Celkem je to 5,845 kWh tepla za den, což podle kroku 1 odpovídá zhruba 2,4
osobám. Profil se proto vynásobí poměrem skutečné potřeby domácnosti k profilu:

$$
\text{odběr} = \text{odběr z profilu} \times \frac{Q_\text{den}}{5{,}845\ \text{kWh}}
$$

Pro 3 osoby je poměr 7,30 / 5,845 ≈ 1,25. Ranní velký odběr tak má 1,75 kWh.
Časy jsou v pražském čase a stejné pro všechny dny.

### 3. Kdy bojler vodu dohřívá

Odebraná teplá voda se v zásobníku nahradí studenou a bojler ji ohřeje. Dohřívá
**hned po odběru, svým plným topným výkonem**, dokud nedodá všechno odebrané
teplo. Velký odběr proto rozloží spotřebu do několika čtvrthodin. V každé
čtvrthodině:

$$
\text{dluh} = \text{dluh z minulé čtvrthodiny} + \text{odběr}
$$

$$
Q = \min(\text{dluh},\ \text{topný výkon} \times 0{,}25\ \text{h})
$$

O dodané teplo $Q$ se dluh sníží a zbytek se přenese do další čtvrthodiny.

Výpočet začíná vždy o půlnoci prvního dne predikce, i když predikce začíná
později. Jinak by se zapomněl dohřev odběru těsně před jejím začátkem.

### 4. Kolik elektřiny to stojí

$$
P_\text{elektřina} = \frac{Q}{0{,}25\ \text{h} \times \text{COP}}
$$

### Režim úspor

Bojler se chová jako spotřebič s prioritou **nezbytné** (1), takže ho žádný
[režim úspor](rezim-uspor.md) nevypne. Teplá voda na mytí se vynechat nedá.

## Příklad

Hodnoty bojleru jsou ze skutečného technického listu Ochsner Europa N 200 CA
[[3]](#zdroje): COP 4,27 při nasávaném vzduchu 20 °C a průměrný topný výkon
1,85 kW. Bojler tedy při ohřevu odebírá 1,85 / 4,27 ≈ 0,43 kW.

Spotřeba za den podle počtu osob:

| Osob | Teplo     | Elektřina |
| ---: | --------: | --------: |
|    1 |  2,43 kWh |  0,57 kWh |
|    2 |  4,87 kWh |  1,14 kWh |
|    3 |  7,30 kWh |  1,71 kWh |
|    4 |  9,73 kWh |  2,28 kWh |

Den tříčlenné domácnosti:

| Čas         | Co se děje                                         |    Elektřina |
| ----------- | -------------------------------------------------- | -----------: |
| 7:00–7:59   | ranní velký odběr 1,75 kWh a malé odběry           |      0,43 kW |
| 8:00–8:14   | dohřev doběhne                                     |      0,27 kW |
| přes den    | malý odběr 0,13 kWh, dohřeje se ve své čtvrthodině |      0,12 kW |
| 12:45       | střední odběr 0,39 kWh                             |      0,37 kW |
| 20:30–20:59 | střední odběr 0,92 kWh                             |      0,43 kW |
| 21:30–22:29 | večerní velký odběr 1,75 kWh                       | 0,34–0,43 kW |
| noc         | nic se neodebírá                                   |         0 kW |

Domácnost z [příkladu u predikce spotřeby](spotreba.md#příklad-domácnost-se-čtyřmi-spotřebiči)
ohřívá vodu obyčejným elektrickým bojlerem zadaným jako spotřebič. Ten spotřebuje
5,00 kWh za den. Bojler s tepelným čerpadlem by pro tři osoby spotřeboval
1,71 kWh, tedy asi třetinu, protože z kilowatthodiny elektřiny dodá přes 4 kWh
tepla.

## Kde v kódu

| Co                        | Kde                                                                                                              |
| ------------------------- | ---------------------------------------------------------------------------------------------------------------- |
| Spotřeba po čtvrthodinách | `generate_water_heater_forecast` v [appliances/water_heater.py](../../server/src/appliances/water_heater.py)     |
| Teplo na osobu            | `DAILY_HEAT_PER_PERSON_KWH`, `LITRES_PER_PERSON` tamtéž                                                          |
| Odběrový profil M         | `PROFILE_M`, `heat_drawn_kwh` tamtéž                                                                             |
| Přičtení ke spotřebě      | `ApplianceService.generate_and_store_forecast` v [appliances/service.py](../../server/src/appliances/service.py) |
| Parametry bojleru         | `WaterHeaterDevice` v [devices/models.py](../../server/src/devices/models.py)                                    |
| Počet osob                | `occupants` lokality v [sites/models.py](../../server/src/sites/models.py)                                       |
| Formulář bojleru          | [water-heater-device-form.tsx](../../client/src/features/devices/components/water-heater-device-form.tsx)        |
| Formulář domu             | [house-form.tsx](../../client/src/features/sites/components/house-form.tsx)                                      |
| Testy podle příkladů výše | [tests/test_water_heater.py](../../server/tests/test_water_heater.py)                                            |

Predikce se přepočítá hned po uložení domu a po přidání, úpravě nebo smazání
bojleru.

## Předpoklady a omezení

- **Spotřeba vody je normová, ne změřená.** 45 litrů na osobu je střed
  orientačního rozsahu z normy. Skutečná domácnost může spotřebovat výrazně víc
  nebo méně.
- **Každý den je stejný.** Profil nezná víkend, dovolenou ani roční období.
  V zimě je studená voda chladnější a její ohřev stojí víc.
- **Bojler dohřívá hned po každém odběru.** Skutečný bojler čeká, až voda v
  zásobníku vychladne o několik stupňů, a pak ohřívá déle najednou. Denní
  spotřeba vychází stejně, jen je jinak rozložená.
- **COP je stálý.** Ve skutečnosti závisí na teplotě vzduchu v místnosti a na
  teplotě vody v zásobníku. COP podle EN 16147 je průměr přes celý zkušební den,
  takže okamžitý příkon při ohřevu bývá vyšší. U bojleru z příkladu uvádí
  výrobce průměrný příkon 0,52 kW, model počítá s 0,43 kW.
- **Tepelné ztráty zásobníku a rozvodů** samostatně nepočítáme.
- **Záložní elektrická spirála se nepočítá.** Bojler ji zapíná při nízké teplotě
  vzduchu nebo při velkém odběru. Model předpokládá, že vše zvládne tepelné
  čerpadlo.
- **Ochlazování místnosti se nepočítá.** Bojler bere teplo ze vzduchu v
  místnosti. Stojí-li ve vytápěném prostoru, musí toto teplo nahradit vytápění.
- **Plán bojler neřídí.** Zásobník vody je vlastně zásobník tepla, takže by šlo
  ohřívat vodu předem, třeba z přebytku fotovoltaiky. Tuto možnost zatím
  nevyužíváme.
- **Jeden bojler na lokalitu.** Má-li lokalita víc bojlerů, počítá se jen první.

## Zdroje

1. VRÁNA, Jakub. [Potřeba vody a tepla pro přípravu teplé vody](https://www.tzb-info.cz/energeticka-narocnost-budov/6839-potreba-vody-a-tepla-pro-pripravu-teple-vody).
   TZB-info, 11. 10. 2010. Tabulka 1 se specifickou potřebou teplé vody o 60 °C
   podle ČSN EN 15316-3-1 a teplota studené vody 13,5 °C.
2. Nařízení Komise (EU) č. 814/2013 o ekodesignu ohřívačů vody a zásobníků teplé
   vody, příloha III, tabulka 1, [konsolidované znění](https://www.legislation.gov.uk/eur/2013/814/pdfs/eur_20130814_2017-01-09_en.pdf).
   Odběrové profily ohřívačů vody, profil M.
3. Ochsner: [Europa N 200 CA](https://www.ochsner.com/en/heat-pumps/hot-water-heat-pumps/europa-n/europa-n-200-ca/).
   COP, profil L, průměrný topný výkon a příkon.
