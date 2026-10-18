# Bilance a úspory

Tento dokument odpovídá na otázku, kvůli které celý systém existuje: **kolik
baterie ušetřila?**

Odpověď stojí na jednom jednoduchém výpočtu, **bilanci čtvrthodiny**. Pro každou
čtvrthodinu, kterou baterie provedla, se spočítá, kolik stála s baterií a kolik
by stála bez ní. Rozdíl je úspora té čtvrthodiny. Úspora za den nebo měsíc je
součet.

## Dvě různá čísla o úspoře

V aplikaci jsou dvě čísla, která se snadno spletou.

|                | Odhadovaná úspora plánu                   | Skutečná úspora                                        |
| -------------- | ----------------------------------------- | ------------------------------------------------------ |
| Co říká        | co plán slibuje od teď do konce horizontu | co baterie ušetřila v čtvrthodinách, které už proběhly |
| Kdy se počítá  | pokaždé znovu, s každým plánem            | jednou, když čtvrthodina proběhne                      |
| Ukládá se      | ne                                        | ano                                                    |
| Dá se sčítat   | ne                                        | ano                                                    |
| Kde je popsaná | [plán podle pravidel](plan-rule-based.md) | tento dokument                                         |

### Proč odhad plánu nejde sčítat

Plán se každou čtvrthodinu počítá znovu a pokaždé pokrývá všechno od teď dál.
Horizonty se proto překrývají:

| Kdy plán vznikl | Co pokrývá           | Odhad |
| --------------- | -------------------- | ----: |
| 10:00           | 10:00 až zítra 24:00 | 30 Kč |
| 10:15           | 10:15 až zítra 24:00 | 29 Kč |
| 14:00           | 14:00 až zítra 24:00 | 33 Kč |

Kdyby se tato čísla sečetla, zítřejší večer by byl započítaný v každém z nich.
Odhad plánu je předpověď, ne účetnictví.

Skutečná úspora se proto počítá jinak: z čtvrthodin, které už proběhly. Každá je
započítaná právě jednou.

## Bilance čtvrthodiny

### Vstupy a výstupy

| Vstup          | Jednotka | Odkud                                                               |
| -------------- | -------- | ------------------------------------------------------------------- |
| Výroba         | kW       | [predikce výroby](fve-vyroba.md)                                    |
| Spotřeba       | kW       | [predikce spotřeby](spotreba.md)                                    |
| Nabíjecí výkon | kW       | co baterie skutečně provedla, viz [model baterie](model-baterie.md) |
| Vybíjecí výkon | kW       | tamtéž                                                              |
| Nákupní cena   | Kč/kWh   | [ceny](ceny.md)                                                     |
| Prodejní cena  | Kč/kWh   | [ceny](ceny.md)                                                     |

| Výstup             | Jednotka |
| ------------------ | -------- |
| Odběr ze sítě      | kW       |
| Dodávka do sítě    | kW       |
| Náklad s baterií   | Kč       |
| Náklad bez baterie | Kč       |

### Krok 1: co jde přes síť

V domě musí energie vždy sedět. Co se vyrobí a nespotřebuje ani neuloží, odteče
do sítě. Co chybí, přiteče ze sítě.

$$
\text{zbytek} = \text{výroba} - \text{spotřeba} - P_{\text{nab}} + P_{\text{vyb}}
$$

- Kladný zbytek je **dodávka do sítě**.
- Záporný zbytek je **odběr ze sítě**.

Nabíjení se odečítá, protože baterie energii z domu bere. Vybíjení se přičítá,
protože ji do domu dodává.

### Krok 2: kolik to stálo

$$
\text{náklad} = \left(
P_{\text{ze sítě}} \times c_{\text{nákup}} - P_{\text{do sítě}} \times c_{\text{prodej}}
\right) \times \Delta t
$$

Za odběr se platí, za dodávku se dostává. Záporný náklad znamená výdělek.

Násobení délkou kroku $\Delta t$ převádí výkon na energii. Platí se za
kilowatthodiny, ne za kilowatty.

### Krok 3: kolik by to stálo bez baterie

Stejný výpočet, jen bez baterie. Nabíjení i vybíjení je nula:

$$
\text{zbytek bez baterie} = \text{výroba} - \text{spotřeba}
$$

Z něj se stejným vzorcem spočítá **náklad bez baterie**.

### Krok 4: úspora

$$
\text{úspora} = \text{náklad bez baterie} - \text{náklad s baterií}
$$

## Příklad: dvě čtvrthodiny

Spot je 2 500 Kč/MWh, tedy nákup 5,566 Kč/kWh a prodej 2,50 Kč/kWh.

### Odpoledne baterie nabíjí

Výroba 3 kW, spotřeba 1 kW, baterie nabíjí 2 kW.

|          | S baterií        | Bez baterie                 |
| -------- | ---------------- | --------------------------- |
| Zbytek   | 3 − 1 − 2 = 0 kW | 3 − 1 = 2 kW                |
| Přes síť | nic              | dodávka 2 kW                |
| Náklad   | 0 Kč             | −2 × 2,50 × 0,25 = −1,25 Kč |

$$
\text{úspora} = -1{,}25 - 0 = -1{,}25\ \text{Kč}
$$

Úspora je **záporná**. Bez baterie by domácnost přebytek prodala a vydělala
1,25 Kč. S baterií neprodala nic.

### Večer baterie vybíjí

Výroba 0 kW, spotřeba 1,5 kW, baterie vybíjí 1,5 kW.

|          | S baterií            | Bez baterie                  |
| -------- | -------------------- | ---------------------------- |
| Zbytek   | 0 − 1,5 + 1,5 = 0 kW | 0 − 1,5 = −1,5 kW            |
| Přes síť | nic                  | odběr 1,5 kW                 |
| Náklad   | 0 Kč                 | 1,5 × 5,566 × 0,25 = 2,09 Kč |

$$
\text{úspora} = 2{,}09 - 0 = 2{,}09\ \text{Kč}
$$

### Dohromady

$$
-1{,}25 + 2{,}09 = 0{,}84\ \text{Kč}
$$

## Úspora jedné čtvrthodiny nic neříká

Z příkladu plyne nejdůležitější pravidlo pro čtení úspor:

- **Když baterie nabíjí z přebytku, úspora je záporná.** Domácnost přichází o
  prodej.
- **Když baterie vybíjí, úspora je kladná.** Domácnost nemusí kupovat.

Nabití je investice, která se vrátí až při vybití. Smysl proto dává jen součet
za dobu, ve které se obojí stihne. Proto aplikace ukazuje úspory po dnech a
měsících, nikdy po čtvrthodinách.

Dobře je to vidět na dni z dokumentu o [plánu podle pravidel](plan-rule-based.md).
Stejných osm hodin, tentokrát s bilancí každé z nich:

| Hodina | Co baterie dělá        | Náklad s baterií | Náklad bez baterie |    Úspora |
| ------ | ---------------------- | ---------------: | -----------------: | --------: |
| 6      | stojí (prázdná)        |             6,17 |               6,17 |      0,00 |
| 9      | nabíjí                 |             0,00 |              −2,00 |     −2,00 |
| 11     | nabíjí                 |             0,00 |              −5,00 |     −5,00 |
| 13     | nabíjí, zbytek do sítě |            −1,52 |              −3,00 |     −1,48 |
| 15     | stojí (plná)           |            −3,00 |              −3,00 |      0,00 |
| 18     | vybíjí                 |             0,00 |              25,77 |     25,77 |
| 20     | vybíjí                 |             0,00 |              39,20 |     39,20 |
| 22     | vybíjí, zbytek ze sítě |             6,91 |              14,76 |      7,85 |
|        | **Celkem**             |         **8,56** |          **72,91** | **64,35** |

Částky jsou v Kč. Až do 15 hodin je baterie ve ztrátě 8,48 Kč. Vydělá až večer.

Všimni si také dvou řádků s nulovou úsporou. V 6 hodin je baterie prázdná a v
15 hodin plná. V obou případech nemůže nic udělat a čtvrthodina dopadne stejně
jako bez ní.

## Kolik ušetří jedna přesunutá kilowatthodina

Z bilance se dá odvodit, kdy se nabití a pozdější vybití vyplatí.

Představ si 1 kWh přebytku. Jsou dvě možnosti:

- **Prodat ji hned.** Domácnost dostane prodejní cenu v době nabíjení.
- **Uložit ji a spotřebovat později.** Z baterie se kvůli ztrátám vrátí jen
  0,9 kWh (při účinnosti cyklu 90 %). Za tolik domácnost později nemusí kupovat.

$$
\text{zisk na 1 kWh} = \eta_{\text{cyklus}} \times c_{\text{nákup později}} - c_{\text{prodej teď}}
$$

| Situace                                    | Prodej teď | Nákup později | Výpočet           |         Zisk |
| ------------------------------------------ | ---------: | ------------: | ----------------- | -----------: |
| Stejná cena celý den (spot 2 500)          |       2,50 |          5,57 | 0,9 × 5,57 − 2,50 |  **2,51 Kč** |
| Levné poledne, drahý večer (500 a 6 000)   |       0,50 |          9,80 | 0,9 × 9,80 − 0,50 |  **8,32 Kč** |
| Drahé poledne, levný večer (4 000 a 1 000) |       4,00 |          3,75 | 0,9 × 3,75 − 4,00 | **−0,62 Kč** |

Z tabulky plyne:

- **Většinou se uložení vyplatí**, i když je cena celý den stejná. Nákup je
  dražší než prodej o poplatky, viz [ceny](ceny.md).
- **Nejvíc se vyplatí**, když je při nabíjení levno a při vybíjení draho.
- **Může se i nevyplatit.** Když je v poledne draho a večer levno, je lepší
  přebytek prodat. Plán podle pravidel to nepozná a nabije i tak, protože se na
  ceny nedívá.

## Co se ukládá

Každá provedená čtvrthodina má jeden řádek v tabulce `site_energy_balance`.

| Sloupec                                        | Význam                         |
| ---------------------------------------------- | ------------------------------ |
| `site_id`, `time`                              | lokalita a začátek čtvrthodiny |
| `strategy`                                     | který plán baterii řídil       |
| `pv_kw`, `load_kw`                             | výroba a spotřeba              |
| `charge_kw`, `discharge_kw`                    | co baterie skutečně provedla   |
| `grid_import_kw`, `grid_export_kw`             | odběr a dodávka                |
| `price_import_czk_kwh`, `price_export_czk_kwh` | ceny v té čtvrthodině          |
| `cost_czk`                                     | náklad s baterií               |
| `baseline_cost_czk`                            | náklad bez baterie             |

Tři rozhodnutí, která za tabulkou stojí:

- **Ukládají se i ceny.** Když se později změní nastavení poplatků, minulé
  čtvrthodiny zůstanou tak, jak tehdy platilo.
- **Ukládá se strategie.** Až bude víc způsobů plánování, půjde porovnat, kolik
  která ušetřila.
- **Úspora se neukládá.** Je to rozdíl dvou uložených sloupců, takže se počítá
  při čtení.

### Kdy řádek vzniká

Řádek zapisuje [simulace baterie](simulace.md) každou čtvrthodinu, společně s
novým stavem baterie.

Řádek **nevznikne**, když pro čtvrthodinu chybí cena nebo predikce. Čtvrthodina,
kterou nejde ocenit, by součty jen zkreslila. Stav baterie se v takové
čtvrthodině zapíše i tak, takže stavů může být víc než řádků bilance.

## Součty za den a měsíc

Úspora za období je součet přes jeho čtvrthodiny:

$$
\text{úspora za den} = \sum_{\text{čtvrthodiny dne}} \left(\text{náklad bez baterie} - \text{náklad s baterií}\right)
$$

**Den je kalendářní den v Praze.** Čtvrthodina, která začíná ve 23:45 pražského
času, patří k danému dni, i když je v UTC už den následující.

### Neúplné dny

Ke každému dni se vrací i počet zaznamenaných čtvrthodin. Běžný den jich má 96.
Když jich je méně, simulace část dne neběžela nebo chyběla data, a úspora toho
dne je neúplná. V grafu jsou takové dny světlejší.

Při změně času má den 92 nebo 100 čtvrthodin a s tím se počítá.

### Co se stane s energií, která v baterii zůstane

U odhadu plánu vadí, že energie zbylá v baterii na konci horizontu se nepočítá.
U skutečných úspor tento problém s délkou období mizí. Co se dnes nabije a
nevybije, vybije se zítra a započítá se do zítřka. Na konci měsíce zbude
nezapočítaná nanejvýš jedna baterie energie, což je proti měsíčnímu součtu
zanedbatelné.

## Kde se úspory zobrazují

- **Dashboard:** „Dnes ušetřeno" vedle odhadované úspory plánu.
- **Stránka Úspory:** sloupcový graf po dnech pro zvolený měsíc, součet za měsíc,
  průměr na den, nejlepší den a součet od začátku provozu.

## Úspora baterií a úspora omezením

Tento dokument popisuje úsporu **baterií**: kolik ušetřila při dané spotřebě.
Když má lokalita zapnutý přísnější [režim úspor](rezim-uspor.md), mění se i
spotřeba samotná. Bilance čtvrthodiny proto ukládá i náklad, který by vznikl bez
baterie a bez omezení, a z něj se počítá druhá část, **úspora omezením**.

Aplikace ukazuje obě části i jejich součet. Jak se úspora omezením počítá,
popisuje dokument o režimu úspor.

## Kde to je v kódu

| Co                   | Kde                                                                                                       |
| -------------------- | --------------------------------------------------------------------------------------------------------- |
| Bilance čtvrthodiny  | `step_balance` v [savings/balance.py](../../server/src/savings/balance.py)                                |
| Tabulka              | `SiteEnergyBalance` v [savings/models.py](../../server/src/savings/models.py)                             |
| Zápis řádku a součty | `SavingsService` v [savings/service.py](../../server/src/savings/service.py)                              |
| Volání ze simulace   | `_record_balance` v [simulation/battery_simulation.py](../../server/src/simulation/battery_simulation.py) |
| API                  | [savings/router.py](../../server/src/savings/router.py)                                                   |
| Testy                | [tests/test_savings_balance.py](../../server/tests/test_savings_balance.py)                               |

## Předpoklady a omezení

- **Úspory jsou ze simulace, ne z měření.** Výroba a spotřeba v bilanci jsou
  predikce. Úspora říká, co by baterie ušetřila, kdyby predikce vyšly přesně.
  Skutečnou úsporu ukáže až měření ze střídače a elektroměru. Struktura tabulky
  na to je připravená: stačí místo predikcí ukládat naměřené hodnoty.
- **Opotřebení baterie se nepočítá.** Každý cyklus baterii o něco opotřebí, viz
  [zdraví baterie](zdravi-baterie.md). Úspora tuto cenu nezahrnuje, takže je o
  ni nadhodnocená.
- **Jen platby závislé na spotřebě.** Pevné měsíční platby v nákladu nejsou. Na
  úsporu nemají vliv, protože jsou s baterií i bez ní stejné.
- **Historie začíná nasazením funkce.** Starší čtvrthodiny zpětně dopočítané
  nejsou.
- **Mezery zůstávají mezerami.** Když simulace neběží, čtvrthodiny chybí a
  nedoplňují se.
- **Bilance je za celou lokalitu.** Nerozlišuje, která baterie co udělala.
