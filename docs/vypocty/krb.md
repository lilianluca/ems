# Topení krbem

Domácnost může místo [tepelného čerpadla](tepelne-cerpadlo.md) topit krbem,
třeba když čerpadlo nefunguje. Krb pálí dřevo a elektřinu nespotřebovává. V
[predikci spotřeby](spotreba.md) se proto projeví jen tím, že **čerpadlo
přestane spotřebovávat elektřinu**.

## Co uživatel zadá

V kartě **Dům** na stránce **Nastavení** je v části o vytápění přepínač:

| Parametr        | Hodnoty  | Význam                                       |
| --------------- | -------- | -------------------------------------------- |
| Topí se krbem   | ano / ne | čerpadlo netopí, dům vytápí krb              |

Nová lokalita má přepínač vypnutý.

Přepínač zůstane zapnutý, dokud ho uživatel nevypne. Poruchu čerpadla ani
rozhodnutí topit dřevem nikdo předpovědět nemůže, proto je musí zadat uživatel.

## Výpočet

Když je přepínač zapnutý, spotřeba tepelného čerpadla je ve všech čtvrthodinách
predikce **0 kW**. Do omezené i neomezené spotřeby, protože přepínač nesouvisí s
[režimem úspor](rezim-uspor.md).

Ostatní složky predikce se nemění: spotřebiče, osvětlení i
[ohřev vody](ohrev-vody.md) počítají jako dřív. Bojler s tepelným čerpadlem je
samostatné zařízení, které na přepínači nezávisí.

Po přepnutí se predikce hned přepočítá, stejně jako po každé jiné změně v kartě
Dům. Plán baterie tak od další čtvrthodiny počítá s nižší spotřebou.

## Příklad

Dům a čerpadlo z [příkladu u tepelného čerpadla](tepelne-cerpadlo.md#příklad), běžný
zimní den s teplotou −3 až 3 °C:

| Přepínač        | Elektřina čerpadla za den | Kdo dodá 33,8 kWh tepla |
| --------------- | ------------------------: | ----------------------- |
| vypnutý         |                   9,2 kWh | tepelné čerpadlo        |
| zapnutý         |                     0 kWh | krb                     |

Spotřeba domácnosti za den klesne o 9,2 kWh. Plán baterie pak má víc přebytku z
fotovoltaiky, který může uložit, a méně spotřeby, kterou musí pokrýt.

## Kde v kódu

| Co                     | Kde                                                                                                              |
| ---------------------- | ---------------------------------------------------------------------------------------------------------------- |
| Přepínač               | `fireplace_heating` lokality v [sites/models.py](../../server/src/sites/models.py)                               |
| Vynulování čerpadla    | `ApplianceService._heat_pump_forecast` v [appliances/service.py](../../server/src/appliances/service.py)         |
| Přepočet po změně      | `SiteService.update_site` v [sites/service.py](../../server/src/sites/service.py)                                |
| Formulář domu          | [house-form.tsx](../../client/src/features/sites/components/house-form.tsx)                                      |

Výpočet nemá vlastní test. Je to jedna podmínka ve službě, která čte databázi,
a ověřená je přepnutím v aplikaci: se zapnutým krbem je predikce stejná jako u
lokality bez čerpadla.

## Předpoklady a omezení

- **Krb vytopí vždycky.** Výkon krbu nepočítáme. Model předpokládá, že krb dodá
  všechno teplo, které by jinak dodalo čerpadlo.
- **Dřevo se nepočítá do nákladů.** Úspora elektřiny se tak může jevit jako
  úspora peněz, i když domácnost platí za dřevo. [Úsporu baterie](uspory.md) to
  nezkreslí: náklad s baterií i bez ní se počítá ze stejné spotřeby, takže cena
  dřeva by se v rozdílu odečetla.
- **Přepínač platí, dokud ho někdo nevypne.** Nezná konec poruchy ani topnou
  sezónu.
- **Krb a čerpadlo se nekombinují.** Buď topí čerpadlo, nebo krb. Večerní
  přitápění krbem k čerpadlu, při kterém čerpadlo jen dodá zbytek tepla, model
  nezná.
- **Teplovodní krb** ohřívající vodu do radiátorů nebo do bojleru nepočítáme.
