# Základy fotovoltaiky (FVE)

EMS potřebuje **predikci výroby FVE** na následující hodiny/den, aby mohl
rozhodovat:

- Kdy nabíjet baterii z FVE vs. ze sítě (levné hodiny OTE)?
- Kdy prodávat přebytky do sítě (drahé hodiny OTE)?
- Kolik výroby lze očekávat zítra → plánování spotřeby.

## Simulace výroby FVE (`simulate_pv_generation`)

Predikce výroby je implementovaná v [`src/simulation/pv_model.py`](../../server/src/simulation/pv_model.py)
funkcí `simulate_pv_generation`, na bázi knihovny [pvlib](https://pvlib-python.readthedocs.io/) a
modelu **PVWatts**. Volá ji `SimulationService.simulate_pv_device`
([`src/simulation/service.py`](../../server/src/simulation/service.py)), který zařídí vstupní data
a uloží výsledek.

### Vstupy

| Parametr                | Zdroj                               | Význam                                                                  |
| ----------------------- | ----------------------------------- | ----------------------------------------------------------------------- |
| `weather`               | InfluxDB, měření `weather_forecast` | předpověď počasí indexovaná UTC časem (`dni`, `dhi`, `ghi`, `temp_air`) |
| `latitude`, `longitude` | `Site`                              | poloha instalace                                                        |
| `installed_power_kwp`   | `PVDevice`                          | jmenovitý DC výkon panelu/pole [kWp]                                    |
| `inverter_power_kw`     | `PVDevice`                          | jmenovitý AC výkon měniče [kW]                                          |
| `tilt_degrees`          | `PVDevice`                          | sklon panelu                                                            |
| `azimuth_degrees`       | `PVDevice`                          | orientace panelu                                                        |

Počasí se načítá v `SimulationService._load_weather` z InfluxDB a přejmenovává na názvy
sloupců, které očekává pvlib:

| InfluxDB sloupec           | pvlib název | Význam                                        |
| -------------------------- | ----------- | --------------------------------------------- |
| `direct_normal_irradiance` | `dni`       | přímé normálové záření [W/m²]                 |
| `diffuse_radiation`        | `dhi`       | difúzní záření na horizontální rovinu [W/m²]  |
| `shortwave_radiation`      | `ghi`       | globální záření na horizontální rovinu [W/m²] |
| `temperature_2m`           | `temp_air`  | teplota vzduchu 2 m nad zemí [°C]             |

### Postup výpočtu

1. **Poloha slunce** — `pvlib.solarposition.get_solarposition(times, latitude, longitude)`
   spočítá pro každý časový krok zenit a azimut slunce nad danou lokací.

2. **Extraterestrické záření** — `pvlib.irradiance.get_extra_radiation(times)` dopočítá
   záření dopadající na vrchol atmosféry; je potřeba jako vstup pro Perezův model v
   dalším kroku.

3. **Transpozice na rovinu panelu (POA)** — `pvlib.irradiance.get_total_irradiance(...)`
   s `model="perez"` přepočítá horizontální složky záření (`dni`/`dhi`/`ghi`) na záření
   dopadající přímo na nakloněnou plochu panelu (`poa_global`), s ohledem na `tilt_degrees`,
   `azimuth_degrees` a polohu slunce z kroku 1.

4. **Teplota článku** — `pvlib.temperature.faiman(poa_global, temp_air)` odhadne teplotu
   samotného FV článku (ta je za slunečného počasí vyšší než teplota vzduchu a snižuje
   účinnost panelu).

5. **DC výkon (PVWatts)** — `pvlib.pvsystem.pvwatts_dc(...)` spočítá DC výkon z `poa_global`,
   teploty článku, jmenovitého výkonu (`pdc0` = `installed_power_kwp × 1000` W) a teplotního
   koeficientu `GAMMA_PDC = -0.004 [1/°C]` (typická hodnota pro křemíkové panely — výkon
   klesá s rostoucí teplotou článku nad 25 °C).

6. **DC-side ztráty** — DC výkon se ještě před měničem sníží o `DC_LOSSES = 10 %`
   (kabeláž, znečištění panelů, mismatch mezi panely) — účinnost měniče v tomhle
   čísle záměrně **není** zahrnutá, řeší se samostatně v dalším kroku.

7. **DC → AC přes model měniče** — `pvlib.inverter.pvwatts(pdc, pdc0, eta_inv_nom)`
   převede DC výkon na AC pomocí realistické účinnostní křivky měniče (účinnost není
   konstantní, ale závisí na zatížení — nejnižší je při nízkém výkonu, vrchol má kolem
   70–90 % jmenovitého zatížení) a zároveň simuluje **clipping**: pokud DC výkon z panelů
   přesáhne kapacitu měniče (typické u předimenzovaného pole vůči měniči), AC výkon se
   neschopně "utne" na jmenovitý AC výkon měniče (`inverter_power_kw`). `pdc0` pro tenhle
   model je DC výkon, při kterém měnič dosahuje jmenovitého AC výkonu za referenčních
   podmínek — dopočítá se jako `inverter_power_kw × 1000 / ETA_INV_NOM`.

Záporné/`NaN` hodnoty (noc, chybějící data) se na konci ořežou na 0. Výstupem je
`pd.Series` AC výkonu v kW, indexovaný časem.

### Uložení výsledku

`SimulationService` uloží výsledné body zpět do InfluxDB do měření `pv_generation_forecast`
(tagy `device_id`, `site_id`, pole `power_kw`) a zároveň vrátí `PVSimulationResult` s body
(`PVGenerationPoint`) a celkovou energií za období (`total_energy_kwh` = součet hodinových
výkonů, protože při hodinovém kroku odpovídá výkon [kW] × 1 h energii [kWh]).

## DC vs. AC — rychlé základy

- DC (stejnosměrný proud) — proud teče pořád jedním směrem. Přesně tohle produkuje fotovoltaický článek: sluneční záření v něm přímo vyrazí elektrony jedním směrem (fotovoltaický jev). Solární panel tedy nativně generuje DC.
- AC (střídavý proud) — proud pravidelně mění směr (v ČR 50× za sekundu, 50 Hz). Tohle používá distribuční síť a naprostá většina spotřebičů v domácnosti/na síti.

Proč se to musí převádět: protože panel vyrábí DC, ale abyste tu energii mohli poslat do domácí sítě, spotřebovat spotřebiči nebo prodat zpět do distribuční sítě, musí projít měničem (invertorem), který DC převede na AC. Bez měniče je výkon z panelů prakticky nepoužitelný — proto je "AC výkon" to skutečné číslo, které EMS zajímá (kolik reálně využitelné energie zařízení vyrobí), zatímco "DC výkon" je jen mezivýpočet.

Simulace teď měnič modeluje skutečně (`pvlib.inverter.pvwatts`, krok 7 výše), ne jen
plochou srážkou — počítá s tím, že:

- účinnost měniče závisí na tom, jak moc je zrovna vytížený (není konstantní),
- pokud je FV pole navržené s vyšším DC výkonem než AC výkon měniče (běžná praxe,
  tzv. **DC/AC ratio** > 1, protože panely málokdy jedou na 100 % jmenovitého výkonu),
  přebytek se nad kapacitu měniče **oseká** ("clipping") — reálný AC výstup nemůže
  nikdy přesáhnout jmenovitý AC výkon měniče (`inverter_power_kw`), i kdyby DC výkon
  z panelů byl vyšší.

## Slovníček

| Pojem       | Význam                                                                                           |
| ----------- | ------------------------------------------------------------------------------------------------ |
| FVE         | fotovoltaická elektrárna                                                                         |
| SoC         | State of Charge – stav nabití baterie [%]                                                        |
| kWp         | kilowatt-peak – jmenovitý výkon FVE za standardních podmínek (STC)                               |
| Azimut      | orientace panelů (180° = jih v konvenci pvlib)                                                   |
| Tilt        | sklon panelů od vodorovné roviny                                                                 |
| STC         | Standardní testovací podmínky                                                                    |
| DC/AC ratio | poměr jmenovitého DC výkonu panelů k jmenovitému AC výkonu měniče (>1 je běžné)                  |
| Clipping    | oříznutí AC výkonu na maximum daném kapacitou měniče, když DC výkon panelů převýší jeho kapacitu |
