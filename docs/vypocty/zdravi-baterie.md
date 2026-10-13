# Zdraví baterie

Baterie používáním stárne a postupně pojme méně energie. Tento dokument popisuje,
jak systém odhaduje, **kolik kapacity baterii zbývá**, a jak s tím počítá při
plánování.

Je to stejný jev, jaký znáš z mobilního telefonu. Po dvou letech vydrží kratší
dobu, i když ukazuje 100 %. Těch „100 %" už je menší množství energie než u
nového.

## Tři pojmy

### Cyklus

Jeden cyklus je jedno úplné nabití a jedno úplné vybití celé kapacity.

Baterie se ale málokdy nabije a vybije celá najednou. Proto se počítají
**ekvivalentní plné cykly**: sečte se všechna energie, kterou baterie kdy vydala,
a přepočítá se na to, kolikrát by to bylo celou kapacitou.

U baterie s kapacitou 10 kWh:

- jedno vybití 10 kWh je 1 cyklus,
- dvě vybití po 5 kWh jsou také 1 cyklus,
- čtyři vybití po 2,5 kWh jsou také 1 cyklus.

### Zdraví

Zdraví říká, kolik procent původní kapacity baterie ještě má. Nová má 100 %.

V angličtině se mu říká _state of health_, zkráceně **SoH**. Neplést se stavem
nabití (SoC):

|                    | Stav nabití (SoC)               | Zdraví (SoH)               |
| ------------------ | ------------------------------- | -------------------------- |
| Co říká            | jak je baterie právě teď nabitá | kolik se do ní vůbec vejde |
| Jak rychle se mění | během hodin                     | během let                  |
| Dá se vrátit zpět  | ano, nabitím                    | ne                         |

### Životnost v cyklech

Výrobce v datovém listu uvádí, kolik cyklů baterie vydrží. Typický údaj je
„6 000 cyklů". Znamená to: **po 6 000 cyklech bude mít baterie 80 % původní
kapacity.**

Baterie na 80 % nepřestane fungovat. Je to jen dohodnutá hranice, které se říká
konec životnosti. Má tři důvody:

- **Srovnání.** Životnost potřebuje nějakou definici konce, jinak by čísla od
  různých výrobců nešla porovnat.
- **Chování baterie.** Do 80 % kapacita klesá pomalu a zhruba rovnoměrně. Pod
  touto hranicí se pokles často zrychluje a hůř se předvídá.
- **Záruka.** Výrobci obvykle ručí právě za to, že kapacita po určitou dobu nebo
  počet cyklů neklesne pod 80 %, někdy 70 %.

## Vstupy a výstupy

| Vstup                     | Příklad | Jednotka | Odkud                  |
| ------------------------- | ------- | -------- | ---------------------- |
| Vybitá energie od začátku | 2 190   | kWh      | historie stavu baterie |
| Kapacita                  | 10      | kWh      | parametr baterie       |
| Životnost                 | 6 000   | cyklů    | parametr baterie       |

| Výstup                     | Jednotka           |
| -------------------------- | ------------------ |
| Počet ekvivalentních cyklů | –                  |
| Zdraví                     | podíl, 1,0 = 100 % |
| Efektivní kapacita         | kWh                |
| Výhled do konce životnosti | roky               |

## Výpočet

### Krok 1: vybitá energie

Každý záznam o stavu baterie obsahuje vybíjecí výkon, který platil jednu
čtvrthodinu. Energie se z výkonu získá vynásobením délkou kroku. Sečtením všech
záznamů vyjde celková vybitá energie:

$$
E_{\text{vybitá}} = \sum_{\text{záznamy}} P_{\text{vyb}} \times \Delta t
$$

Počítá se jen vybíjení. Co baterie vydala, musela předtím přijmout, takže stačí
sledovat jednu stranu cyklu.

### Krok 2: počet cyklů

$$
\text{cykly} = \frac{E_{\text{vybitá}}}{\text{kapacita}}
$$

Dělí se kapacitou z datového listu, ne tou už sníženou. Tak je definována i
životnost, se kterou se počet cyklů porovnává.

### Krok 3: zdraví

Model předpokládá, že každý cyklus ubere stejný kousek kapacity.

Za celou životnost baterie klesne ze 100 % na 80 %. Přijde tedy o **20 %**
kapacity, což je ve vzorci číslo 0,2:

$$
0{,}2 = 1 - 0{,}8
$$

Z těchto 20 % je pryč taková část, jaká část životnosti už uběhla:

$$
\text{zdraví} = 1 - 0{,}2 \times \frac{\text{cykly}}{\text{životnost}}
$$

| Část vzorce       | Význam                          | Po 3 000 cyklech z 6 000 |
| ----------------- | ------------------------------- | ------------------------ |
| cykly / životnost | jaká část životnosti uběhla     | 0,5 (polovina)           |
| 0,2 × podíl       | o kolik kapacity baterie přišla | 0,2 × 0,5 = 0,1 (10 %)   |
| 1 − úbytek        | kolik kapacity zbývá            | 1 − 0,1 = 0,9 (90 %)     |

Při životnosti 6 000 cyklů ubere jeden cyklus 0,2 / 6 000, tedy asi 0,0033 %
kapacity.

Zdraví nemůže klesnout pod nulu. Výpočet se na nule zastaví.

### Krok 4: efektivní kapacita

$$
\text{efektivní kapacita} = \text{kapacita} \times \text{zdraví}
$$

To je kapacita, se kterou systém dál počítá.

## Příklad: rok provozu

Baterie 10 kWh s životností 6 000 cyklů každý večer vydá 6 kWh.

| Krok                  | Výpočet           | Výsledek      |
| --------------------- | ----------------- | ------------- |
| Vybitá energie za rok | 6 × 365           | 2 190 kWh     |
| Počet cyklů           | 2 190 / 10        | 219           |
| Úbytek zdraví         | 0,2 × 219 / 6 000 | 0,73 %        |
| Zdraví                | 100 % − 0,73 %    | **99,27 %**   |
| Efektivní kapacita    | 10 × 0,9927       | **9,927 kWh** |

Za rok běžného provozu tedy baterie ztratí necelé procento kapacity.

### Jak zdraví klesá s počtem cyklů

| Cykly | Zdraví | Efektivní kapacita |
| ----: | -----: | -----------------: |
|     0 |  100 % |           10,0 kWh |
| 1 000 | 96,7 % |           9,67 kWh |
| 3 000 |   90 % |            9,0 kWh |
| 6 000 |   80 % |            8,0 kWh |
| 9 000 |   70 % |            7,0 kWh |

V 6 000 cyklech je zdraví přesně 80 %, jak říká datový list. Model pokračuje
stejným tempem i dál.

## Co se s efektivní kapacitou děje

Plán i simulace počítají s efektivní kapacitou, ne s tou z datového listu. Meze
nabití jsou procenta z kapacity, takže se s ní zmenšují i ony.

Baterie z příkladu má povolený rozsah 10–95 %:

|                     | Nová baterie |   Po roce |
| ------------------- | -----------: | --------: |
| Kapacita            |   10,000 kWh | 9,927 kWh |
| Spodní mez (10 %)   |    1,000 kWh | 0,993 kWh |
| Horní mez (95 %)    |    9,500 kWh | 9,431 kWh |
| Využitelná kapacita |    8,500 kWh | 8,438 kWh |

Kdyby plán počítal s původní kapacitou, plánoval by nabití na 9,5 kWh, kam se už
opotřebená baterie nedostane.

Stejně se počítá i stav nabití v procentech na dashboardu. Je to podíl z
efektivní kapacity, takže plně nabitá opotřebená baterie ukazuje 95 %, ne méně.
Podrobnosti o mezích jsou v [modelu baterie](model-baterie.md).

## Výhled do konce životnosti

Výhled odpovídá na otázku: **při současném tempu používání, za jak dlouho klesne
zdraví na 80 %?**

K odpovědi jsou potřeba dvě čísla, která se snadno spletou:

|                  | Cykly dosud                     | Tempo                      |
| ---------------- | ------------------------------- | -------------------------- |
| Co říká          | kolik cyklů má baterie za sebou | jak rychle cykly přibývají |
| Jednotka         | cykly                           | cykly za rok               |
| Z čeho se počítá | z celé historie                 | z posledního roku          |

Cykly dosud říkají, kolik životnosti je pryč. Tempo říká, jak rychle ubývá ta
zbylá.

### Krok 1: cykly za měřené období

Nejdřív se zjistí, kolik cyklů baterie udělala za období, které známe. Je to
stejný výpočet jako u cyklů dosud, jen se nesčítá celá historie, ale pouze
měřené období:

$$
\text{cykly za období} = \frac{E_{\text{vybitá za období}}}{\text{kapacita}}
$$

Měřeným obdobím je **posledních 365 dní**. Je-li historie baterie kratší, vezme
se celá.

Například baterie 10 kWh, která běží 90 dní a vydala 600 kWh, udělala
600 / 10 = **60 cyklů za 90 dní**.

#### Proč zrovna rok

Baterie u fotovoltaiky cykluje v létě výrazně víc než v zimě. Kdyby se tempo
bralo z kratšího období, například z posledního měsíce, výhled by v červenci
vyšel pesimisticky a v prosinci optimisticky, přestože se na baterii ani na jejím
používání nic nezměnilo. Rok pokryje všechna roční období.

Cenou je pomalejší reakce. Když se používání baterie změní, například přibude
tepelné čerpadlo, výhled to plně zachytí až za rok.

U baterie mladší než rok je obdobím celá její historie. Tempo je pak průměr za
celý její dosavadní život a první rok se ještě může měnit podle ročního období,
ve kterém začala.

### Krok 2: přepočet na rok

Výsledek prvního kroku platí pro měřené období. Výhled ale potřebuje tempo za
rok. Přepočítá se trojčlenkou: kolikrát se měřené období vejde do roku, tolikrát
víc cyklů baterie za rok udělá.

$$
\text{cyklů za rok} = \text{cykly za období} \times \frac{365}{\text{počet dní období}}
$$

Pokračování příkladu: 90 dní se do roku vejde 365 / 90 = 4,06krát, takže tempo
je 60 × 4,06 = **243 cyklů za rok**.

Když je měřeným obdobím právě rok, zlomek je 365 / 365 = 1 a tempo se rovná
počtu cyklů za období. Přepočet se tedy projeví jen u baterie mladší než rok.

### Krok 3: kolik cyklů zbývá a jak dlouho to potrvá

$$
\text{let do konce životnosti} = \frac{\text{životnost} - \text{cykly dosud}}{\text{cyklů za rok}}
$$

### Příklad: baterie stará dva roky

Baterie 10 kWh s životností 6 000 cyklů běží dva roky. Od začátku vydala
4 000 kWh, z toho za posledních 365 dní 2 190 kWh.

| Krok                      | Výpočet               | Výsledek         |
| ------------------------- | --------------------- | ---------------- |
| Cykly dosud               | 4 000 / 10            | 400              |
| Zdraví                    | 1 − 0,2 × 400 / 6 000 | 98,67 %          |
| Cykly za období (365 dní) | 2 190 / 10            | 219              |
| Tempo                     | 219 × 365 / 365       | 219 cyklů za rok |
| Zbývá cyklů               | 6 000 − 400           | 5 600            |
| Výhled                    | 5 600 / 219           | **25,6 roku**    |

Cykly dosud (400) a tempo (219 za rok) jsou různá čísla. Baterie první rok
cyklovala méně než druhý, takže tempo neodpovídá polovině celkového počtu.

### Příklad: baterie stará tři měsíce

Baterie běží 90 dní a vydala 600 kWh. Rok historie nemá, obdobím je celých
90 dní.

| Krok                     | Výpočet       | Výsledek         |
| ------------------------ | ------------- | ---------------- |
| Cykly dosud              | 600 / 10      | 60               |
| Cykly za období (90 dní) | 600 / 10      | 60               |
| Tempo                    | 60 × 365 / 90 | 243 cyklů za rok |
| Zbývá cyklů              | 6 000 − 60    | 5 940            |
| Výhled                   | 5 940 / 243   | **24,4 roku**    |

### Kdy se výhled neukáže

- **Baterie má méně než jeden den historie.** Z pár hodin se rok odhadnout nedá.
  Jeden večerní výboj by se promítl, jako by trval nepřetržitě.
- **Baterie se nepoužívá.** Při nulovém tempu by vyšlo nekonečno.

### Výhled je horní odhad

Výhled počítá jen s cykly. Baterie ale stárne i časem, ať se používá, nebo ne.
Domácí baterie se proto v praxi dožívají spíš 10 až 15 let, i když by podle cyklů
vydržely déle.

Aplikace proto výhled delší než 30 let zobrazí jako „více než 30 let". Přesnější
číslo by předstíralo znalost, kterou model nemá.

## Vliv životnosti z datového listu

Jak moc záleží na jediném parametru, který do výpočtu zadáváš? Baterie z příkladu
roku provozu (219 cyklů dosud, tempo 219 cyklů za rok) se dvěma různými
životnostmi:

|   Životnost | Zdraví po roce |    Výhled |
| ----------: | -------------: | --------: |
| 6 000 cyklů |        99,27 % | 26,4 roku |
| 3 000 cyklů |        98,54 % | 12,7 roku |

Poloviční životnost znamená dvojnásobný úbytek a zhruba poloviční výhled. Vyplatí
se proto zadat skutečnou hodnotu z datového listu. Výchozí hodnota 6 000 cyklů je
jen rozumný odhad pro dnešní domácí baterie.

## Kde to je v kódu

| Co                                         | Kde                                                                                               |
| ------------------------------------------ | ------------------------------------------------------------------------------------------------- |
| Výpočet cyklů, zdraví a efektivní kapacity | `battery_health` v [devices/battery_health.py](../../server/src/devices/battery_health.py)        |
| Výpočet výhledu                            | `years_to_end_of_life` tamtéž                                                                     |
| Hranice konce životnosti (80 %)            | `END_OF_LIFE_HEALTH` tamtéž                                                                       |
| Součet vybité energie                      | `read_discharged_kwh` v [devices/battery_state.py](../../server/src/devices/battery_state.py)     |
| Tempo z posledního roku                    | `DeviceService._years_to_end_of_life` v [devices/service.py](../../server/src/devices/service.py) |
| Použití efektivní kapacity v plánu         | `battery_spec` v [optimization/service.py](../../server/src/optimization/service.py)              |
| Parametr životnosti                        | `cycle_life` v [devices/models.py](../../server/src/devices/models.py)                            |
| Testy                                      | [tests/test_battery_health.py](../../server/tests/test_battery_health.py)                         |

## Předpoklady a omezení

Model je nejjednodušší, jaký jde postavit na jediném údaji, který výrobce
opravdu uvádí. Zanedbává tyto věci:

- **Stárnutí časem.** Baterie ztrácí kapacitu i nepoužívaná. Model zná jen
  cykly, takže zdraví nepoužívané baterie neklesá vůbec.
- **Hloubku vybití.** Mělké cykly, například mezi 40 a 60 %, škodí baterii méně
  než plné. Model počítá každou kilowatthodinu stejně.
- **Teplotu a rychlost nabíjení.** Horko a rychlé nabíjení stárnutí urychlují.
- **Skutečný průběh.** Ve skutečnosti baterie ztrácí rychleji na začátku a ke
  konci života. Model předpokládá rovnoměrný úbytek.
- **Hranice 80 % je pevná.** Někteří výrobci uvádějí životnost do 70 % nebo
  60 %. Pro takovou baterii model zdraví podhodnocuje.
- **Historie musí být úplná.** Zdraví se počítá ze zaznamenaných stavů baterie.
  Cykly z doby, kdy systém neběžel nebo ještě neexistoval, model nezná. U
  baterie, která už něco odsloužila, proto vyjde zdraví lepší, než jaké je.
- **Cena opotřebení se do úspor nepočítá.** Každý cyklus baterii o něco
  opotřebí, ale [úspory](uspory.md) to nezohledňují a plán se tím neřídí.
