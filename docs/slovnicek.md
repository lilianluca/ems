# Slovníček

Pojmy, které se v dokumentaci a v kódu opakují. Jsou seřazené podle témat, od
základů k tomu, co je specifické pro tento systém. Na konci je tabulka, která
české pojmy převádí na názvy použité v kódu.

U většiny pojmů je odkaz na dokument, kde je vysvětlený podrobně a s příkladem.

## Elektřina obecně

| Pojem              | Význam                                                                                                                               |
| ------------------ | ------------------------------------------------------------------------------------------------------------------------------------ |
| **Výkon**          | Jak rychle elektřina teče právě teď. Měří se ve wattech (W) nebo kilowattech (kW). Rychlovarná konvice má výkon asi 2 kW.            |
| **Energie**        | Kolik elektřiny proteklo za nějakou dobu. Měří se v kilowatthodinách (kWh). Platí se za energii, ne za výkon. Energie = výkon × čas. |
| **kW**             | Kilowatt, tisíc wattů. Jednotka výkonu.                                                                                              |
| **kWh**            | Kilowatthodina. Energie, kterou spotřebuje zařízení o výkonu 1 kW za jednu hodinu.                                                   |
| **MWh**            | Megawatthodina, tisíc kilowatthodin. V této jednotce se udávají ceny na burze.                                                       |
| **Příkon**         | Výkon, který spotřebič ze sítě odebírá.                                                                                              |
| **Síť**            | Veřejná elektrická síť, ke které je dům připojený. Dům z ní elektřinu odebírá a může ji do ní dodávat.                               |
| **Odběr**          | Elektřina, kterou dům bere ze sítě. Platí se za ni nákupní cena.                                                                     |
| **Dodávka**        | Elektřina, kterou dům posílá do sítě. Dostává se za ni prodejní cena. Říká se jí také přetok.                                        |
| **Přípojka**       | Místo, kde je dům připojený k síti. Má omezený výkon daný hlavním jističem.                                                          |
| **Limit přípojky** | Největší výkon, který smí přes přípojku téct, ať jde o odběr, nebo dodávku. V systému 17 kW.                                         |

Víc v [přehledu systému](prehled.md).

## Čas

| Pojem           | Význam                                                                                                                    |
| --------------- | ------------------------------------------------------------------------------------------------------------------------- |
| **Krok**        | Nejmenší časový úsek, se kterým systém počítá. Je to čtvrthodina. Všechny řady mají jednu hodnotu na krok.                |
| **Čtvrthodina** | 15 minut, tedy 0,25 hodiny. Po čtvrthodinách se obchoduje elektřina na burze. Běžný den jich má 96.                       |
| **Horizont**    | Řada čtvrthodin, pro kterou se sestavuje plán. Začíná aktuální čtvrthodinou a končí tam, kde končí známé ceny a predikce. |
| **UTC**         | Světový čas bez letního a zimního posunu. V něm jsou data uložená v databázi.                                             |
| **Pražský čas** | Čas, ve kterém se data zobrazují. Den je vždy kalendářní den v Praze.                                                     |

## Ceny

| Pojem                    | Význam                                                                                                                 |
| ------------------------ | ---------------------------------------------------------------------------------------------------------------------- |
| **Denní trh**            | Burza, na které se každý den odpoledne v aukci určí ceny elektřiny na následující den.                                 |
| **OTE**                  | Operátor trhu s elektřinou. Organizuje denní trh v Česku.                                                              |
| **Spotová cena (spot)**  | Cena elektřiny z denního trhu. Je zvlášť pro každou čtvrthodinu, udává se v Kč/MWh a může být i záporná.               |
| **Spotový tarif**        | Smlouva, podle které domácnost neplatí pevnou cenu, ale cenu odvozenou od spotu.                                       |
| **Nákupní cena**         | Kolik stojí kilowatthodina ze sítě. Spot plus marže dodavatele a distribuce, to celé s DPH.                            |
| **Prodejní cena**        | Kolik domácnost dostane za kilowatthodinu dodanou do sítě. Spot krát výkupní koeficient. Říká se jí také výkupní cena. |
| **Marže dodavatele**     | Poplatek dodavateli za to, že elektřinu na burze nakoupí.                                                              |
| **Distribuce**           | Poplatek za dopravu elektřiny sítí. Platí se jen při odběru.                                                           |
| **Výkupní koeficient**   | Jakou část spotové ceny výkupce zaplatí. Hodnota 1,0 znamená plnou cenu.                                               |
| **Vysoký a nízký tarif** | Dvě cenová pásma distribuce, která distributor během dne střídá. Systém je nerozlišuje.                                |

Víc v dokumentu o [cenách](vypocty/ceny.md).

## Fotovoltaika

| Pojem                  | Význam                                                                                                                                                                     |
| ---------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Fotovoltaika (FVE)** | Solární panely, které vyrábějí elektřinu ze slunečního světla. FVE je zkratka pro fotovoltaickou elektrárnu.                                                               |
| **Výroba**             | Výkon, který fotovoltaika právě dodává.                                                                                                                                    |
| **kWp**                | Kilowatt-peak, špičkový výkon panelů. Výkon, který panely dají za ideálních zkušebních podmínek. Skutečný výkon je většinou nižší.                                         |
| **Střídač**            | Zařízení, které mění stejnosměrný proud z panelů a baterie na střídavý proud používaný v domě. Jeho výkon omezuje, kolik fotovoltaika do domu dodá. Říká se mu také měnič. |
| **Sklon**              | Úhel panelů od vodorovné roviny. 0° je naplocho, 90° svisle.                                                                                                               |
| **Azimut**             | Světová strana, na kterou panely míří. 0° je sever, 90° východ, 180° jih, 270° západ.                                                                                      |
| **Pole**               | Skupina panelů se stejným sklonem a azimutem. Lokalita jich může mít víc, například na dvou stranách střechy.                                                              |

Dokument o [predikci výroby](vypocty/fve-vyroba.md) zatím není napsaný.

## Spotřeba

| Pojem                   | Význam                                                                                                                                    |
| ----------------------- | ----------------------------------------------------------------------------------------------------------------------------------------- |
| **Spotřeba**            | Výkon, který domácnost právě odebírá ze všech zdrojů dohromady.                                                                           |
| **Spotřebič**           | Zařízení v domácnosti zadané v aplikaci: jeho příkon a to, kdy obvykle běží. Ze spotřebičů se skládá predikce spotřeby.                   |
| **Přebytek**            | Výroba je větší než spotřeba. Rozdíl jde do baterie nebo do sítě.                                                                         |
| **Nedostatek**          | Spotřeba je větší než výroba. Rozdíl pokryje baterie nebo síť.                                                                            |
| **Vlastní spotřeba**    | Část vyrobené elektřiny, kterou domácnost sama spotřebuje, místo aby ji prodala.                                                          |
| **Priorita spotřebiče** | Jak moc je spotřebič pro domácnost důležitý, od 1 (nezbytný) po 4 (komfortní). Podle ní režim úspor rozhoduje, co vypne.                  |
| **Režim úspor**         | Jak moc je domácnost ochotná omezit spotřebu: běžný, úsporný, velmi úsporný, nebo extrémní. Vedoucí práce ho označuje jako úrovně rizika. |
| **Dům**                 | Nastavení lokality, které nepatří k žádnému spotřebiči: zatím výkon osvětlení a doba, kdy je někdo doma.                                  |
| **Obsazenost**          | Zda je někdo doma a vzhůru. Zadává se jako okna v celých hodinách, stejná pro všechny dny.                                                |
| **Tma**                 | Číslo od 0 do 1 podle výšky slunce nad obzorem: 0 ve dne, 1 po skončení občanského soumraku. Určuje, jakou část osvětlení svítí.          |

Víc v dokumentech o [predikci spotřeby](vypocty/spotreba.md) a
[osvětlení](vypocty/osvetleni.md).

## Baterie

| Pojem                            | Význam                                                                                              |
| -------------------------------- | --------------------------------------------------------------------------------------------------- |
| **Kapacita**                     | Kolik energie baterie pojme. V kWh.                                                                 |
| **Stav nabití (SoC)**            | Kolik energie v baterii právě je. V kWh nebo v procentech kapacity. Z anglického _state of charge_. |
| **Minimální a maximální nabití** | Meze, mezi kterými se baterie používá. Úplné vybití ani trvalé nabití na 100 % jí neprospívá.       |
| **Spodní a horní mez**           | Minimální a maximální nabití přepočtené na kWh.                                                     |
| **Využitelná kapacita**          | Rozdíl mezi horní a spodní mezí. Tolik energie se z baterie reálně používá.                         |
| **Nabíjecí výkon**               | Výkon, kterým baterie odebírá energii z domu. Uloží se z něj méně, o ztráty.                        |
| **Vybíjecí výkon**               | Výkon, kterým baterie dodává energii do domu. Z baterie kvůli tomu ubude víc, o ztráty.             |
| **Účinnost cyklu**               | Kolik energie se z baterie vrátí z té, která do ní byla poslána. Při 90 % se z 1 kWh vrátí 0,9 kWh. |
| **Účinnost jednoho směru**       | Účinnost samotného nabíjení nebo samotného vybíjení. Odmocnina z účinnosti cyklu.                   |
| **Cyklus**                       | Jedno úplné nabití a vybití celé kapacity.                                                          |
| **Ekvivalentní plné cykly**      | Počet cyklů přepočítaný z celkové vybité energie. Dvě poloviční vybití jsou jeden cyklus.           |
| **Životnost v cyklech**          | Počet cyklů, po kterém má baterie 80 % původní kapacity. Údaj z datového listu.                     |
| **Zdraví (SoH)**                 | Kolik procent původní kapacity baterie ještě má. Z anglického _state of health_.                    |
| **Efektivní kapacita**           | Kapacita snížená o opotřebení. S ní systém počítá.                                                  |
| **Tempo**                        | Jak rychle cykly přibývají, v cyklech za rok.                                                       |
| **Výhled**                       | Odhad, za jak dlouho klesne zdraví na 80 %.                                                         |
| **Datový list**                  | Dokument výrobce s technickými parametry zařízení.                                                  |

Víc v dokumentech o [modelu baterie](vypocty/model-baterie.md) a o
[zdraví baterie](vypocty/zdravi-baterie.md).

## Plánování a simulace

| Pojem                             | Význam                                                                                                                                            |
| --------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Predikce**                      | Odhad budoucí výroby nebo spotřeby po čtvrthodinách.                                                                                              |
| **Plán**                          | Rozpis, co má baterie dělat v každé čtvrthodině horizontu: nabíjet, vybíjet, nebo stát.                                                           |
| **Strategie**                     | Způsob, jakým se plán sestavuje. Systém zná dvě: podle pravidel a optimalizací.                                                                   |
| **Plán podle pravidel**           | Jednodušší strategie. Přebytek uloží, nedostatek pokryje z baterie. Na ceny se nedívá.                                                            |
| **Maximalizace vlastní spotřeby** | Cíl plánu podle pravidel: spotřebovat co nejvíc vlastní výroby.                                                                                   |
| **Plán optimalizací**             | Složitější strategie. Hledá nejlevnější plán s ohledem na ceny v celém horizontu.                                                                 |
| **Lineární program (LP)**         | Matematická úloha, kterou plán optimalizací řeší.                                                                                                 |
| **Klouzavý horizont (MPC)**       | Postup, při kterém se naplánuje celý horizont, provede jen první krok a v dalším kroku se plánuje znovu. Z anglického _model predictive control_. |
| **Simulace**                      | Výpočet, který zastupuje skutečnou baterii. Každou čtvrthodinu provede první krok plánu a zapíše nový stav.                                       |

Víc v dokumentech o [plánu podle pravidel](vypocty/plan-rule-based.md) a o
[simulaci](vypocty/simulace.md).

## Úspory

| Pojem                       | Význam                                                                                                   |
| --------------------------- | -------------------------------------------------------------------------------------------------------- |
| **Bilance**                 | Vyúčtování jedné čtvrthodiny: co šlo přes síť a kolik to stálo, s baterií a bez ní.                      |
| **Náklad**                  | Kolik čtvrthodina nebo období stálo. Platba za odběr minus příjem za dodávku. Záporný náklad je výdělek. |
| **Náklad bez baterie**      | Kolik by totéž stálo, kdyby baterie nebyla: každý přebytek prodaný, každý nedostatek koupený.            |
| **Úspora**                  | Náklad bez baterie minus náklad s baterií.                                                               |
| **Odhadovaná úspora plánu** | Úspora, kterou plán slibuje od teď do konce horizontu. Předpověď, která se nedá sčítat.                  |
| **Skutečná úspora**         | Součet úspor čtvrthodin, které už proběhly. Dá se sčítat po dnech a měsících.                            |
| **Neúplný den**             | Den, ve kterém simulace nezaznamenala všechny čtvrthodiny. Jeho úspora je neúplná.                       |

Víc v dokumentu o [úsporách](vypocty/uspory.md).

## Aplikace

| Pojem         | Význam                                                                                                                                  |
| ------------- | --------------------------------------------------------------------------------------------------------------------------------------- |
| **Lokalita**  | Jedno místo s vlastní fotovoltaikou, baterií a spotřebiči, typicky jeden dům. Má zeměpisné souřadnice, podle kterých se stahuje počasí. |
| **Zařízení**  | Fotovoltaické pole nebo baterie patřící k lokalitě.                                                                                     |
| **Dashboard** | Úvodní stránka lokality s cenami, predikcemi, plánem a stavem baterie. V aplikaci se jmenuje Přehled.                                   |

## Česky a v kódu

Kód je psaný anglicky. Tato tabulka pomáhá najít, jak se pojem z dokumentace
jmenuje v kódu a v databázi.

| Česky                               | V kódu                                          |
| ----------------------------------- | ----------------------------------------------- |
| krok, délka kroku                   | `STEP`, `STEP_HOURS`, `step_hours`              |
| výroba                              | `pv_kw`, `pv_generation_kw`                     |
| spotřeba                            | `load_kw`                                       |
| přebytek                            | `surplus_kw`                                    |
| odběr ze sítě                       | `grid_import_kw`                                |
| dodávka do sítě                     | `grid_export_kw`                                |
| limit přípojky                      | `grid_limit_kw`                                 |
| spotová cena                        | `price_czk_mwh`, `spot_czk_mwh`                 |
| nákupní cena                        | `price_import_czk_kwh`                          |
| prodejní cena                       | `price_export_czk_kwh`                          |
| marže dodavatele                    | `supplier_margin_czk_kwh`                       |
| distribuce                          | `distribution_fees_czk_kwh`                     |
| výkupní koeficient                  | `export_factor`                                 |
| špičkový výkon panelů               | `installed_power_kwp`                           |
| výkon střídače                      | `inverter_power_kw`                             |
| sklon, azimut                       | `tilt_degrees`, `azimuth_degrees`               |
| kapacita                            | `capacity_kwh`                                  |
| stav nabití                         | `state_of_charge_kwh`, `state_of_charge`        |
| minimální a maximální nabití        | `min_state_of_charge`, `max_state_of_charge`    |
| spodní a horní mez                  | `usable_floor_kwh`, `usable_ceiling_kwh`        |
| nabíjecí a vybíjecí výkon           | `charge_kw`, `discharge_kw`                     |
| maximální nabíjecí a vybíjecí výkon | `max_charge_power_kw`, `max_discharge_power_kw` |
| účinnost cyklu                      | `round_trip_efficiency`                         |
| účinnost jednoho směru              | `one_way_efficiency`                            |
| životnost v cyklech                 | `cycle_life`                                    |
| ekvivalentní plné cykly             | `equivalent_full_cycles`                        |
| zdraví                              | `state_of_health`                               |
| efektivní kapacita                  | `effective_capacity_kwh`                        |
| výhled                              | `years_to_end_of_life`                          |
| plán                                | `OptimizationPlan`, `OptimizationResult`        |
| strategie                           | `PlanStrategy`                                  |
| plán podle pravidel                 | `rule_based_schedule`                           |
| plán optimalizací                   | `optimize_battery_schedule`                     |
| bilance čtvrthodiny                 | `step_balance`, `StepBalance`                   |
| náklad                              | `cost_czk`                                      |
| náklad bez baterie                  | `baseline_cost_czk`                             |
| úspora                              | `savings_czk`                                   |
| lokalita                            | `Site`, `site_id`                               |
| zařízení                            | `Device`, `device_id`                           |
| spotřebič                           | `Appliance`                                     |
| režim úspor                         | `saving_mode`, `SavingMode`                     |
| priorita spotřebiče                 | `priority`                                      |
| výkon osvětlení                     | `lighting_power_w`                              |
| okna obsazenosti                    | `occupancy_windows`, `OccupancyWindow`          |
| tma                                 | `darkness`                                      |
