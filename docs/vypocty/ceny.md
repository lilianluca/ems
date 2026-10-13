# Ceny elektřiny

Z jedné spotové ceny vzniknou dvě ceny, se kterými počítá zbytek systému:
**nákupní** (kolik stojí kilowatthodina ze sítě) a **prodejní** (kolik dostaneš
za kilowatthodinu dodanou do sítě).

Je to nejjednodušší výpočet v systému, ale stojí na něm všechny ostatní. Plán
baterie i úspory dávají smysl jen díky tomu, že se tyto dvě ceny liší.

## Co je spotová cena

Elektřina se obchoduje na burze. Na **denním trhu**, který v Česku organizuje
OTE (operátor trhu), se každý den odpoledne v aukci určí ceny na celý následující
den. Těmto cenám se říká **spotové**.

- Cena je zvlášť pro **každou čtvrthodinu**, tedy 96 cen na den.
- Udává se v **Kč/MWh**. Jedna megawatthodina je 1 000 kilowatthodin.
- Mění se podle nabídky a poptávky. V poledne za slunečného dne bývá nízká,
  večer vysoká.
- Může být i **záporná**. Když je elektřiny příliš, výrobci platí za to, že ji
  někdo odebere.

Domácnost se spotovým tarifem neplatí pevnou cenu, ale cenu, která se takhle mění
každou čtvrthodinu. Proto se vyplatí řešit, **kdy** elektřinu odebírá.

Systém si ceny stahuje každých 30 minut z veřejného API služby
[spotovaelektrina.cz](https://spotovaelektrina.cz), která ceny OTE zpřístupňuje,
a ukládá je do tabulky `ote_spot_price`.
Pro představu, v datech vývojové instalace (červenec až říjen 2026) byla nejnižší
cena −269 Kč/MWh, průměrná 3 218 Kč/MWh a nejvyšší 16 735 Kč/MWh.

## Vstupy a výstupy

| Vstup                             | Hodnota           | Jednotka | Odkud                    |
| --------------------------------- | ----------------- | -------- | ------------------------ |
| Spotová cena                      | podle čtvrthodiny | Kč/MWh   | tabulka `ote_spot_price` |
| Marže dodavatele                  | 0,30              | Kč/kWh   | nastavení systému        |
| Distribuční a regulované poplatky | 1,80              | Kč/kWh   | nastavení systému        |
| Sazba DPH                         | 21                | %        | nastavení systému        |
| Výkupní koeficient                | 1,0               | –        | nastavení systému        |

| Výstup        | Jednotka |
| ------------- | -------- |
| Nákupní cena  | Kč/kWh   |
| Prodejní cena | Kč/kWh   |

Čtyři hodnoty z nastavení jsou v [config.py](../../server/src/core/config.py).
Jsou to **orientační odhady**, ne údaje ze skutečné faktury. Víc v omezeních na
konci.

## Výpočet

### Krok 1: převod na kilowatthodiny

Spot je v Kč/MWh, všechno ostatní v Kč/kWh. Megawatthodina je tisíc
kilowatthodin, takže se cena vydělí tisícem.

$$
c_{\text{spot}} = \frac{\text{spot [Kč/MWh]}}{1000}
$$

Spot 2 500 Kč/MWh je 2,50 Kč/kWh.

### Krok 2: nákupní cena

Spotová cena je jen cena samotné elektřiny. Když ji kupuješ ze sítě, platíš
navíc:

- **marži dodavatele** za to, že ti elektřinu na burze nakoupí,
- **distribuční a regulované poplatky** za to, že ti ji někdo po drátech dopraví,
- **DPH** z celé částky.

$$
c_{\text{nákup}} = \left(c_{\text{spot}} + m + d\right) \times (1 + \text{DPH})
$$

kde $m$ je marže dodavatele a $d$ jsou distribuční poplatky.

### Krok 3: prodejní cena

Když elektřinu do sítě dodáváš, dostaneš zaplaceno jen za elektřinu samotnou.

$$
c_{\text{prodej}} = c_{\text{spot}} \times k
$$

kde $k$ je výkupní koeficient.

Proč ve vzorci chybí ostatní položky:

- **Distribuce:** platí se za dopravu elektřiny k tobě. Při dodávce do sítě tuto
  službu nevyužíváš, takže ji neplatíš ani za ni nic nedostáváš.
- **DPH:** běžná domácnost s fotovoltaikou není plátce DPH, takže ji k prodejní
  ceně nepřičítá.
- **Výkupní koeficient** vyjadřuje, že výkupce si z ceny něco nechá. Hodnota 1,0
  znamená, že dostaneš plnou spotovou cenu.

## Příklad

Spotová cena je 2 500 Kč/MWh.

| Krok          | Výpočet            | Výsledek         |
| ------------- | ------------------ | ---------------- |
| Převod        | 2 500 / 1 000      | 2,50 Kč/kWh      |
| Nákup bez DPH | 2,50 + 0,30 + 1,80 | 4,60 Kč/kWh      |
| Nákup s DPH   | 4,60 × 1,21        | **5,566 Kč/kWh** |
| Prodej        | 2,50 × 1,0         | **2,50 Kč/kWh**  |

Kilowatthodina ze sítě stojí víc než dvojnásobek toho, co dostaneš za
kilowatthodinu do sítě dodanou.

## Proč na rozdílu záleží

Celý smysl baterie je v rozdílu mezi nákupní a prodejní cenou. Následující
tabulka ukazuje obě ceny pro různé spotové ceny, spočítané funkcemi z kódu:

| Spot [Kč/MWh] | Nákup [Kč/kWh] | Prodej [Kč/kWh] | Rozdíl [Kč/kWh] |
| ------------: | -------------: | --------------: | --------------: |
|         6 000 |           9,80 |            6,00 |            3,80 |
|         2 500 |           5,57 |            2,50 |            3,07 |
|             0 |           2,54 |            0,00 |            2,54 |
|          −500 |           1,94 |           −0,50 |            2,44 |

Z tabulky plynou tři věci:

1. **Nákup je dražší než prodej** v celém rozsahu cen, o 2,4 až 3,8 Kč/kWh.
   Poplatky se totiž platí jen při nákupu.
2. **Rozdíl nezmizí, ani když je spot nulový.** I když je elektřina na burze
   zadarmo, ze sítě stojí 2,54 Kč/kWh, protože poplatky a DPH zůstávají.
3. **Při záporném spotu za dodávku do sítě platíš.** Prodejní cena −0,50 Kč/kWh
   znamená, že za každou dodanou kilowatthodinu zaplatíš 50 haléřů.

Proto se vyplatí přebytek z fotovoltaiky neprodat, ale uložit do baterie a
spotřebovat později. Každá kilowatthodina, kterou si domácnost vyrobí a sama
spotřebuje, ušetří nákupní cenu. Kdyby ji prodala, dostala by jen prodejní.

Přesný výpočet toho, kolik baterie ušetří včetně ztrát při nabíjení a vybíjení,
je v dokumentu o [úsporách](uspory.md).

## Kde se ceny používají

Obě ceny se počítají na dvou místech, vždy stejnými funkcemi:

- **při plánování baterie** pro každou čtvrthodinu horizontu,
- **při vyúčtování provedené čtvrthodiny**, kdy se uloží do tabulky
  `site_energy_balance` spolu s nákladem.

Ceny se k vyúčtované čtvrthodině ukládají záměrně. Když se později změní
nastavení poplatků, minulé čtvrthodiny zůstanou spočítané tak, jak tehdy platilo.

## Kde to je v kódu

| Co                                 | Kde                                                                                                                                     |
| ---------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------- |
| Výpočet nákupní ceny               | `import_price_czk_kwh` v [optimization/service.py](../../server/src/optimization/service.py)                                            |
| Výpočet prodejní ceny              | `export_price_czk_kwh` tamtéž                                                                                                           |
| Hodnoty poplatků                   | `supplier_margin_czk_kwh`, `distribution_fees_czk_kwh`, `vat_rate`, `export_factor` v [core/config.py](../../server/src/core/config.py) |
| Stahování a ukládání spotových cen | [ote/service.py](../../server/src/ote/service.py)                                                                                       |

Tyto dvě funkce zatím nemají vlastní testy.

## Předpoklady a omezení

- **Poplatky jsou odhad.** Hodnoty 0,30 a 1,80 Kč/kWh jsou řádově správné, ale
  nejsou z konkrétní faktury. Skutečné se liší podle dodavatele, distribučního
  území a sazby.
- **Poplatky jsou stejné pro všechny lokality.** Jsou v nastavení celého systému,
  ne u lokality.
- **Distribuce stojí v každou hodinu stejně.** Model přičítá ke každé
  kilowatthodině stejných 1,80 Kč, ať je odebraná ve dne nebo v noci. Mnoho
  domácností má ale dvoutarifní sazbu: distributor střídá během dne **vysoký
  tarif** a **nízký tarif** (dříve „noční proud") a v nízkém tarifu je poplatek
  za distribuci výrazně nižší. Kdy který platí, určuje distributor, typicky je
  nízký tarif v noci a část odpoledne. Pro takovou domácnost model nákupní cenu
  v hodinách nízkého tarifu nadhodnocuje a v hodinách vysokého podhodnocuje.
- **Bez pevných plateb.** Měsíční platby za jistič nebo odběrné místo nezávisí na
  spotřebě. Na rozhodování baterie nemají vliv, proto v modelu nejsou. Do
  celkového účtu za elektřinu by ale patřily.
- **Výkupní koeficient 1,0 je optimistický.** Předpokládá, že výkupce platí plnou
  spotovou cenu. Smlouvy bývají různé, orientačně:

  | Tvar výkupu               | Typicky                          |
  | ------------------------- | -------------------------------- |
  | Spot × koeficient         | 0,80 až 0,95                     |
  | Spot mínus pevný poplatek | spot − 0,10 až 0,30 Kč/kWh       |
  | Pevná výkupní cena        | 1 až 2 Kč/kWh bez ohledu na spot |
  | Bez výkupu                | přetoky zdarma                   |

  Model umí jen první tvar. Nižší koeficient zvětší rozdíl mezi nákupem a
  prodejem, takže baterie vyjde výhodněji.

- **Záporné ceny se berou doslova.** Při záporném spotu vyjde záporná prodejní
  cena, tedy platba za dodávku. Při spotu pod −2 100 Kč/MWh vyjde záporná i
  nákupní cena. Skutečné smlouvy tyto situace často řeší jinak, například
  nulovou výkupní cenou.
