# Tepelné čerpadlo

Výpočet odhaduje, **kolik elektřiny spotřebuje tepelné čerpadlo v každé
čtvrthodině.** Výsledek se přičte k [predikci spotřeby](spotreba.md).

Čerpadlo se nedá popsat jako běžný spotřebič, protože jeho spotřeba závisí na
počasí. Čím je venku chladněji, tím víc tepla dům potřebuje a tím méně účinně ho
čerpadlo vyrábí. Model se týká čerpadla **vzduch-vzduch**, které jen vytápí.
Neohřívá vodu a chlazení v létě se nepočítá.

## K čemu slouží topný faktor

Tepelné čerpadlo teplo nevyrábí, ale přenáší ho zvenku dovnitř. **Topný faktor
(COP)** říká, kolik tepla dodá z jedné kilowatthodiny elektřiny:

$$
\text{COP} = \frac{\text{dodané teplo}}{\text{spotřebovaná elektřina}}
$$

Při COP 4 vznikne z 1 kWh elektřiny 4 kWh tepla. Zbylé 3 kWh čerpadlo vezme z
venkovního vzduchu.

## Co potřebujeme vědět

Parametry domu, zadávají se na stránce **Nastavení** v kartě **Dům**:

| Parametr                    | Jednotka | Význam                                                       |
| --------------------------- | -------- | ------------------------------------------------------------ |
| Tepelná ztráta              | kW       | kolik tepla vytápěná část domu ztrácí při výpočtové teplotě  |
| Výpočtová venkovní teplota  | °C       | teplota, pro kterou je tepelná ztráta spočítaná              |
| Vnitřní teplota             | °C       | na kolik se dům vytápí                                       |

Tepelnou ztrátu uvádí výpočet tepelných ztrát domu od projektanta nebo topenáře.
Zadává se jen za část domu, kterou čerpadlo vytápí. Vzduch-vzduch často nevytopí
celý dům, protože teplý vzduch fouká jen z vnitřních jednotek. Výpočtová teplota
závisí na místě: v tabulkách je například −12 °C pro Prahu a −18 °C pro Liberec
[[1]](#zdroje).

Parametry čerpadla, zadávají se na stránce **Zařízení**:

| Parametr            | Jednotka | Význam                                                |
| ------------------- | -------- | ----------------------------------------------------- |
| COP při −7 °C       | –        | řádek `Tj = -7 °C`, hodnota `COPd`                    |
| COP při 2 °C        | –        | řádek `Tj = 2 °C`, hodnota `COPd`                     |
| COP při 7 °C        | –        | řádek `Tj = 7 °C`, hodnota `COPd`                     |
| COP při 12 °C       | –        | řádek `Tj = 12 °C`, hodnota `COPd`                    |
| Maximální výkon     | kW       | řádek `Tj = operating limit`, hodnota `Pdh`           |

Tyto hodnoty najdeš v technickém listu čerpadla. Výrobci klimatizací do 12 kW je
uvádějí ve stejné tabulce podle evropského nařízení [[2]](#zdroje), takže se dají
přímo opsat. Příklad takového listu je ve zdroji [[3]](#zdroje).

Venkovní teplotu po čtvrthodinách už systém má z předpovědi počasí.

Spotřeba čerpadla se počítá, jen když má lokalita čerpadlo i nenulovou tepelnou
ztrátu. Nová lokalita má ztrátu 0 kW.

## Výpočet krok za krokem

### 1. Kolik tepla dům ztrácí na jeden stupeň

Tepelná ztráta je přímo úměrná rozdílu teplot uvnitř a venku [[4]](#zdroje). Ze
zadané ztráty proto jde spočítat, kolik tepla dům ztrácí na každý stupeň rozdílu:

$$
H\ [\text{kW/K}] = \frac{\text{tepelná ztráta}}{\text{vnitřní teplota} - \text{výpočtová teplota}}
$$

### 2. Kolik tepla musí čerpadlo dodat

Dům se částečně hřeje sám: lidmi, spotřebiči, světly a sluncem. Proto se netopí
až do vnitřní teploty, ale jen pod **vyrovnávací teplotou**. To je venkovní
teplota, při které tyto zisky pokryjí ztráty domu [[4]](#zdroje). Volíme 15 °C.

$$
Q_\text{potřeba} = H \times \max(0,\ 15^\circ\text{C} - T_\text{venku})
$$

Teplo, které čerpadlo dodá, je omezené jeho maximálním výkonem:

$$
Q = \min(Q_\text{potřeba},\ \text{maximální výkon})
$$

Teplo nad tento výkon by musel dodat jiný zdroj, který do spotřeby elektřiny
nepočítáme.

Odkud jsou 15 °C: pro začátek a konec otopného období se v českých tabulkách
používají teploty 12, 13 a 15 °C [[1]](#zdroje). Volba 15 °C z tohoto rozsahu je
náš odhad, přesnou hodnotu pro konkrétní dům neznáme. Dobře zateplený dům ji má
nižší [[4]](#zdroje).

### 3. Jaký je topný faktor

COP se určí z venkovní teploty a čtyř hodnot z technického listu. Mezi nimi se
hodnota dopočítá lineárně. Pod −7 °C a nad 12 °C se použije krajní hodnota.

### 4. Kolik elektřiny to stojí

$$
P_\text{elektřina} = \frac{Q}{\text{COP}}
$$

Výsledek se přičte ke spotřebě ve stejné čtvrthodině. Hodnota se mění po
čtvrthodinách, protože po čtvrthodinách je i předpověď teploty.

### Když předpověď teploty chybí

Předpověď počasí končí půlnocí zítřejšího dne (UTC), predikce spotřeby ale
sahá 48 hodin dopředu. Pro čtvrthodiny bez předpovědi se použije **poslední
známá teplota**. Plán do těchto čtvrthodin většinou nesahá a další přepočet je
přepíše skutečnou předpovědí. Teplota starší než jeden den se nepoužije, aby
výpadek stahování nenechal čerpadlo počítat se starým počasím. Když teplota
chybí úplně, spotřeba čerpadla je 0.

### Režim úspor

Čerpadlo se chová jako spotřebič s prioritou **nezbytné** (1), takže ho žádný
[režim úspor](rezim-uspor.md) nevypne. Vytápění se v zimě vynechat nedá.

## Příklad

Hodnoty COP jsou ze skutečného technického listu klimatizace Samsung AC035RXADKG
[[3]](#zdroje):

| Venkovní teplota | −7 °C | 2 °C | 7 °C | 12 °C |
| ---------------- | ----: | ---: | ---: | ----: |
| COP              |   2,5 |  4,1 |  4,9 |   6,3 |

Její maximální výkon je 2,3 kW. Dům je vymyšlený: tepelná ztráta vytápěné části
**3 kW** při −12 °C, vnitřní teplota 20 °C. Z toho:

$$
H = \frac{3}{20 - (-12)} = 0{,}09375\ \text{kW/K}
$$

Výpočet při několika venkovních teplotách:

| Venku  | Potřeba tepla | Dodané teplo |  COP | Elektřina |
| -----: | ------------: | -----------: | ---: | --------: |
| −12 °C |       2,53 kW |      2,30 kW | 2,50 |   0,92 kW |
|  −7 °C |       2,06 kW |      2,06 kW | 2,50 |   0,83 kW |
|   0 °C |       1,41 kW |      1,41 kW | 3,74 |   0,38 kW |
|   7 °C |       0,75 kW |      0,75 kW | 4,90 |   0,15 kW |
|  13 °C |       0,19 kW |      0,19 kW | 6,30 |   0,03 kW |
|  18 °C |          0 kW |         0 kW |    – |      0 kW |

Při −12 °C čerpadlo nestačí: chybí 0,23 kW tepla, které musí dodat jiný zdroj.

Spotřeba za celý den, pro vymyšlené dny s teplotou plynule se měnící mezi
minimem a maximem:

| Den          | Teplota v průběhu dne | Dodané teplo | Elektřina | Průměrný COP |
| ------------ | --------------------: | -----------: | --------: | -----------: |
| silný mráz   |          −10 až −2 °C |     47,1 kWh |  17,2 kWh |         2,74 |
| běžná zima   |            −3 až 3 °C |     33,8 kWh |   9,2 kWh |         3,65 |
| jaro         |            2 až 12 °C |     18,0 kWh |   3,9 kWh |         4,66 |
| teplý duben  |            8 až 18 °C |      6,1 kWh |   1,1 kWh |         5,56 |
| léto         |           15 až 28 °C |        0 kWh |     0 kWh |            – |

Domácnost z [příkladu u predikce spotřeby](spotreba.md#příklad-domácnost-se-čtyřmi-spotřebiči)
spotřebuje za den 8,56 kWh. V běžný zimní den tedy čerpadlo její spotřebu zhruba
zdvojnásobí a v silném mrazu víc než ztrojnásobí.

## Kde v kódu

| Co                        | Kde                                                                                                                     |
| ------------------------- | ----------------------------------------------------------------------------------------------------------------------- |
| Spotřeba po čtvrthodinách | `generate_heat_pump_forecast` v [appliances/heat_pump.py](../../server/src/appliances/heat_pump.py)                     |
| Ztráta na stupeň          | `heat_loss_per_kelvin_kw` tamtéž                                                                                        |
| Potřeba tepla             | `heat_demand_kw`, `BALANCE_TEMPERATURE_C` tamtéž                                                                        |
| COP podle teploty         | `cop_at`, `COP_TEMPERATURES_C` tamtéž                                                                                   |
| Přičtení ke spotřebě      | `ApplianceService.generate_and_store_forecast` v [appliances/service.py](../../server/src/appliances/service.py)        |
| Parametry čerpadla        | `HeatPumpDevice` v [devices/models.py](../../server/src/devices/models.py)                                              |
| Parametry domu            | `heat_loss_kw`, `design_outdoor_temp_c`, `indoor_temp_c` lokality v [sites/models.py](../../server/src/sites/models.py) |
| Formulář čerpadla         | [heat-pump-device-form.tsx](../../client/src/features/devices/components/heat-pump-device-form.tsx)                     |
| Formulář domu             | [house-form.tsx](../../client/src/features/sites/components/house-form.tsx)                                             |
| Testy podle příkladů výše | [tests/test_heat_pump.py](../../server/tests/test_heat_pump.py)                                                         |

Predikce se přepočítá hned po uložení domu a po přidání, úpravě nebo smazání
čerpadla.

## Předpoklady a omezení

- **Dům nemá tepelnou setrvačnost.** Skutečný dům chladne a nahřívá se postupně.
  Model počítá, jako by se teplo muselo dodat ve stejné čtvrthodině, kdy se
  ztrácí. Spotřeba proto kopíruje venkovní teplotu těsněji než ve skutečnosti.
- **Jedno čerpadlo na lokalitu.** Má-li lokalita víc čerpadel, počítá se jen
  první.
- **Plán čerpadlo neřídí.** Dům by šlo vytopit víc, když je elektřina levná, a
  v drahých hodinách topit méně. Tuto možnost zatím nevyužíváme, čerpadlo je jen
  předpovězená spotřeba.
- **Vyrovnávací teplota je pevná a je to odhad.** Ve skutečnosti se mění s
  obsazeností domu, sluncem a zateplením [[4]](#zdroje). Slunce ani počet lidí
  doma výpočet nezohledňuje.
- **Vnitřní teplota je stálá.** Výpočet nezná noční útlum ani topení podle
  obsazenosti.
- **COP pod −7 °C je nadhodnocený.** Technický list z příkladu uvádí 1,8 při
  −20 °C, model bere 2,5. Podobně nad 12 °C se COP dál nezvyšuje, tam je ale
  spotřeba zanedbatelná.
- **COP z listu platí pro částečný výkon.** Hodnoty `COPd` jsou změřené při
  výkonu určeném pro danou teplotu. Při jiném výkonu se skutečný COP liší.
- **Maximální výkon je stálý.** Hodnota z listu platí pro nejnižší provozní
  teplotu, za tepla bývá skutečný výkon jiný. Limit se tak použije jen v mrazech.
- **Odmrazování a pohotovostní příkon** samostatně nepočítáme.
- **Jiné zdroje tepla se nepočítají.** Krb ani jiné topení potřebu tepla
  nesnižují.

## Zdroje

1. TZB-info: [Venkovní výpočtové teploty a otopná období dle lokalit](https://www.tzb-info.cz/tabulky-a-vypocty/25-venkovni-vypoctove-teploty-a-otopna-obdobi-dle-lokalit).
   Výpočtové teploty českých měst a teploty pro začátek a konec otopného období.
   Tabulka vychází ze starších norem ČSN 38 3350 a ČSN 06 0210, pro návrh skutečné
   otopné soustavy je potřeba ověřit aktuální hodnoty.
2. Nařízení Komise (EU) č. 206/2012 o ekodesignu klimatizátorů a komfortních
   ventilátorů, [konsolidované znění](https://eur-lex.europa.eu/eli/reg/2012/206/2017-01-09/eng).
3. Samsung: [technický list AC035RN1DKG / AC035RXADKG](https://images.samsung.com/is/content/samsung/p6/common/energylabel/common-energylabel-ac035rxadkg-eu-ecodesign.pdf).
   Hodnoty `Pdh` a `COPd` pro průměrné klima.
4. MIT OpenCourseWare: [4.401 Environmental Technologies in Buildings, přednáška 16](https://ocw.mit.edu/courses/4-401-environmental-technologies-in-buildings-fall-2018/5b9e24cbf2abd05c5e06a263a85b61f9_MIT4_401F18_lec16.pdf).
   Tepelná bilance budovy a vyrovnávací teplota.
