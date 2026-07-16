import pandas as pd
import pvlib

# PVWatts standard coefficients (pvlib default values)
GAMMA_PDC = -0.004  # temperature coefficient of power [1/°C]
ETA_INV_NOM = 0.96  # nominal efficiency of the inverter (pvlib default)
DC_LOSSES = 0.10  # DC-side losses: cables, soiling, mismatch (without inverter!)


def simulate_pv_generation(
    weather: pd.DataFrame,
    latitude: float,
    longitude: float,
    installed_power_kwp: float,
    inverter_power_kw: float,
    tilt_degrees: float,
    azimuth_degrees: float,
) -> pd.Series:
    """Simulate PV DC power output using the PVWatts model."""
    times = weather.index

    solar_position = pvlib.solarposition.get_solarposition(times, latitude, longitude)

    dni_extra = pvlib.irradiance.get_extra_radiation(times)

    total_irradiance = pvlib.irradiance.get_total_irradiance(
        surface_tilt=tilt_degrees,
        surface_azimuth=azimuth_degrees,
        solar_zenith=solar_position["apparent_zenith"],
        solar_azimuth=solar_position["azimuth"],
        dni=weather["dni"],
        ghi=weather["ghi"],
        dhi=weather["dhi"],
        dni_extra=dni_extra,
        model="perez",
    )

    poa_global = total_irradiance["poa_global"]

    cell_temperature = pvlib.temperature.faiman(
        poa_global=poa_global,
        temp_air=weather["temp_air"],
    )

    pdc0_w = installed_power_kwp * 1000  # kWp → W
    dc_power_w = pvlib.pvsystem.pvwatts_dc(
        effective_irradiance=poa_global,
        temp_cell=cell_temperature,
        pdc0=pdc0_w,
        gamma_pdc=GAMMA_PDC,
    )

    dc_power_w = dc_power_w * (1 - DC_LOSSES)

    inverter_pdc0_w = (inverter_power_kw * 1000) / ETA_INV_NOM
    ac_power_w = pvlib.inverter.pvwatts(
        pdc=dc_power_w,
        pdc0=inverter_pdc0_w,
        eta_inv_nom=ETA_INV_NOM,
    )

    ac_power_kw = ac_power_w / 1000
    return ac_power_kw.clip(lower=0).fillna(0)
