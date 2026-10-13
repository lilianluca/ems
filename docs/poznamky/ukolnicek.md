# Úkolníček

## Vyhodnocení (chybějící kapitola práce)

Implementace stojí, vyhodnocení ne. Úspory, které aplikace ukazuje, jsou ze
simulace za dobu, kdy běžela. V tabulce `ote_spot_price` je přitom **historie
spotových cen od 10. 7. 2026**, takže všechno níž jde udělat bez jediného čidla.

- [ ] **Zpětný test** – přehrát plánem každý uplynulý den a spočítat úsporu za
      celé období. Výstup je rozdělení, ne jedno číslo: průměr na den, nejlepší
      a nejhorší den.
- [ ] **Srovnání strategií** – pustit plán podle pravidel a plán optimalizací na
      stejných historických vstupech. Odpovídá na otázku, o kolik je optimalizace
      lepší než jednoduché pravidlo.
- [ ] **Citlivostní analýza** – jak se úspora mění s kapacitou baterie,
      s účinností a s výší distribučních poplatků. Odpovídá na „vyplatí se
      baterie", což je praktičtější otázka než „je plán optimální".

## Provoz

- [ ] **Automatické zálohy Postgresu** – zatím jen ruční `pg_dump` (29. 9. 2026,
      před přechodem na TimescaleDB). Jediný dluh, který může zničit všechno
      naráz; s rostoucí historií roste i sázka.
- [ ] **Ukládat snímek plánu** – provedené čtvrthodiny se už ukládají do
      `site_energy_balance`, samotné plány ne. Bez snímku, například jednou denně
      po zveřejnění cen, nejde porovnat, co plán slíbil, s tím, co se stalo.

## Model a data

- [ ] **Import naměřených dat** (CSV z distribuce nebo z portálu výrobce
      střídače) – bez skutečných hodnot nejde ověřit, jestli model sedí, ani
      odhalit špatně zadaný azimut.
- [ ] Stav baterie ze střídače místo simulovaného – vyžaduje integraci se
      střídačem.
- [ ] Střídač je modelovaný na každém poli FVE zvlášť – u východo-západní
      instalace se sdíleným měničem model nadhodnotí výkon.
- [ ] Plán řídí jen **první** baterii lokality; společné plánování víc úložišť
      (domácí, písková, elektromobil) je rozšíření.
- [ ] Predikce spotřeby zůstává tvarem hodinová – parametry modelu jsou per
      hodina dne, takže se hodnota ve čtyřech krocích opakuje. Zjemnit ji lze až
      lepším tvarem (lichoběžník místo obdélníku přes okno), ne kratším krokem.

## Aplikace

- [ ] Role uživatele na lokalitě chybí v `SiteRead` – `VIEWER` proto vidí
      tlačítka, která mu server odmítne.
- [ ] Tarifní parametry jsou globální v `Settings`; patří na lokalitu, protože
      distributor a sazba se liší dům od domu.
- [ ] Předvolby typických spotřebičů (lednice, myčka, bojler…) – nikdo nezná
      duty cycle své lednice zpaměti.
- [ ] `pragueMarketWindow` v klientovi duplikuje `default_market_window` ze
      serveru – čistší by bylo vracet okno v odpovědi API.
