# Dokumentace EMS

EMS (Energy Management System) je aplikace pro domácnost s fotovoltaikou a
baterií. Plánuje, kdy má baterie nabíjet a kdy vybíjet, aby domácnost zaplatila
za elektřinu co nejméně. Vzniká jako diplomová práce.

Dokumentace je psaná tak, aby jí rozuměl i čtenář, který se s energetikou ani s
tímto kódem dosud nesetkal.

## Kde začít

1. [Přehled systému](prehled.md) – co systém dělá, z čeho se skládá a jak jím
   tečou data. Vysvětluje i základní pojmy.
2. [Slovníček](slovnicek.md) – pojmy z dokumentace a jejich názvy v kódu.
3. Výpočty níže, v uvedeném pořadí.

## Výpočty

Každý dokument popisuje jeden výpočet: k čemu je, jak se počítá krok za krokem,
příklad s čísly, kde je v kódu a co zanedbává. Jdou za sebou tak, jak data tečou
systémem.

| Dokument                                              | Na co odpovídá                                                    |
| ----------------------------------------------------- | ----------------------------------------------------------------- |
| [Ceny elektřiny](vypocty/ceny.md)                     | Kolik stojí kilowatthodina ze sítě a kolik se dostane za dodanou? |
| [Predikce výroby fotovoltaiky](vypocty/fve-vyroba.md) | Kolik fotovoltaika vyrobí? _(zatím nenapsáno)_                    |
| [Predikce spotřeby](vypocty/spotreba.md)              | Kolik domácnost spotřebuje?                                       |
| [Osvětlení](vypocty/osvetleni.md)                     | Kolik domácnost prosvítí v zimě a kolik v létě?                   |
| [Režim úspor](vypocty/rezim-uspor.md)                 | Co se stane, když domácnost omezí spotřebiče?                     |
| [Model baterie](vypocty/model-baterie.md)             | Kolik energie bude v baterii za čtvrthodinu?                      |
| [Plán podle pravidel](vypocty/plan-rule-based.md)     | Co má baterie dělat, když se řídí jen přebytkem a nedostatkem?    |
| [Plán optimalizací](vypocty/plan-lp.md)               | Co má baterie dělat, aby vyšla nejlevněji? _(zatím nenapsáno)_    |
| [Simulace baterie](vypocty/simulace.md)               | Jak se plán každou čtvrthodinu provádí?                           |
| [Bilance a úspory](vypocty/uspory.md)                 | Kolik baterie ušetřila?                                           |
| [Zdraví baterie](vypocty/zdravi-baterie.md)           | Kolik kapacity baterii zbývá?                                     |

## Provoz

Jak systém běží na serveru a jak se o něj starat.

| Dokument                              | Na co odpovídá                                        |
| ------------------------------------- | ----------------------------------------------------- |
| [Zálohy databáze](provoz/zalohy.md)   | Jak se data zálohují, jak to ověřit a jak je obnovit? |

## Poznámky

Pracovní podklady. Nejsou součástí popisu systému a nemusí být aktuální.

| Dokument                           | Obsah                                    |
| ---------------------------------- | ---------------------------------------- |
| [Zadání](poznamky/zadani.md)       | zadání diplomové práce                   |
| [Úkolníček](poznamky/ukolnicek.md) | co zbývá udělat, včetně úkolů ze schůzek |

## Co v dokumentaci ještě chybí

- **Dva výpočty** označené výše jako nenapsané.
- **Rozhodnutí** – proč je systém postavený tak, jak je.
- **Omezení** – všechna zjednodušení na jednom místě. Zatím je má každý výpočet
  na svém konci.
- **Architektura** – moduly, databáze, úlohy na pozadí, frontend.
- **Provoz** – nasazení a migrace. Zálohy už jsou popsané výše.

## Jak se dokumentace píše

- **Příklady jsou spočítané kódem.** Čísla v příkladech vracejí skutečné funkce
  z kódu, nejsou vymyšlená. Když se změní výpočet, příklad je potřeba přepočítat.
- **Dokument a kód se mění společně.** Změna výpočtu patří do stejné změny jako
  úprava jeho dokumentu.
- **Formát hlídá linter.** Pravidla jsou v [.markdownlint.json](../.markdownlint.json).
  Spouští se z kořene repozitáře:

  ```bash
  npx markdownlint-cli2 "docs/**/*.md"
  ```
