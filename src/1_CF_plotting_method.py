#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Spyder Editor

Restructered on Wed 10 Nov 2020 14:15

@author: Laurens Stoop - l.p.stoop@uu.nl
"""


# %%
# =============================================================================
# Dependencies
# =============================================================================


# Importing modules
import xarray as xr
import numpy as np
import matplotlib.pyplot as plt


# File locations
# file_path = '/media/DataDrive/ERA5-EU_BASE/'


# Max CF for the RES
maxCF_on = 0.95
maxCF_off = 0.95


print('NOTIFY: Basic setup done, defining functions')
# %%
# =============================================================================
# Function definitions
# =============================================================================

# Function to determine the solar capacity factor as from Jerez 2015


def solar_potential_jerez2015(ds):

    # The constant definitions
    # Cell temperature constants in [degree C, unitless, degree C * m**2 /W, degree C *s/m
    c = np.array([4.3, 0.943, 0.028, -1.528])
    tref = 25  # Reference temperature in degree C
    gamma = -0.005  # Prefactor to performance rate per degree
    istd = 1000  # Standard solar panel performance benchmark in W/m**2

    # Zeorth step: Make a dataset
    ds_temp = xr.Dataset()

    # First step: calculate cell temperature
    ds_temp['Tcell'] = c[0] + c[1]*ds.t2m + c[2]*ds.ssrd + c[3]*ds.wspd

    # The second step: Performance ratio of the solar cells
    ds_temp['solarPR'] = 1 + gamma*(ds_temp.Tcell - tref)

    # The solar energy capcaity factor
    ds_temp['solarCF'] = ds_temp.solarPR*ds.ssrd/istd

    # Force zero as minimal value
    ds_temp['solarCF'] = ds_temp.solarCF.where(ds_temp.solarCF >= 0, 0)

    return ds_temp.solarCF


# Function to determine the solar capacity factor as from bett & thornton 2016
def solar_potential_bett2016(ds):

    # The constant definitions
    ALPHA = 4.20 * 10**(-3)  # K**-1
    BETA = -4.60 * 10**(-3)  # K**-1
    C1 = 0.033  # [no unit]
    C2 = -0.092  # [no unit]
    GSTC = 1000  # W m**-2
    TSTC = 25  # degree C
    T0 = 20  # degree C
    G0 = 800  # W m**-2
    TNOCT = 48  # degree C

    # Zeorth step: Make a dataset
    ds_temp = xr.Dataset()

    # first step is to combined calculation of module temperature and taking the difference between that and the STC conditions
    ds_temp['DTmod'] = ds.t2m + (TNOCT - T0)*ds.ssrd/G0 - TSTC

    # In the second step the Reletive efficiency is calculated basedon an empirical law, where the derive irradience in taken into account
    ds_temp['Nrel'] = (1 + ALPHA * ds_temp.DTmod) * (1 + C1*np.log(ds.ssrd /
                                                                   GSTC) + C2*np.log(ds.ssrd/GSTC)**2 + BETA*ds_temp.DTmod)

    # In the final step the capacity factor is calculated based on the reletive efficiency and the STC irradience conditions
    ds_temp['solarCF'] = ds_temp.Nrel * ds.ssrd / GSTC

    # the use of the logarithm gives rise to NaN values which should be zero, therefore all nan values are set to zero
    ds_temp = ds_temp.fillna(0)

    # Force zero as minimal value
    ds_temp['solarCF'] = ds_temp.solarCF.where(ds_temp.solarCF >= 0, 0)

    return ds_temp.solarCF


# Function to determine the windpotential (this is adjusted based on expert judgement)
def wind_potential(wspd, height, alpha, cut_in_wspd, cut_out_start, cut_out_end, rated_wspd, maxCF):

    # First we create a new dataset
    ds_temp = xr.Dataset()

    # Rescaling the windspeed to the requested height
    wspd_height = wspd * (height / 100)**alpha

    # We fill it with the windpotential without considering the information of the wind turbine
    ds_temp['windCF'] = maxCF * ((wspd_height**3 - cut_in_wspd**3) / (rated_wspd**3 - cut_in_wspd**3))

    # Now we reduce the wind potential to 1 above the rated windspeed
    ds_temp['windCF'] = ds_temp.windCF.where(wspd_height <= rated_wspd, maxCF)

    # Now we set the wind potential to 0 below the cut-in windspeed
    ds_temp['windCF'] = ds_temp.windCF.where(wspd_height >= cut_in_wspd, 0)

    # Now we set the wind potential to 0 above the cut-out windspeed
    # ds_temp['windCF'] = ds_temp.windCF.where(wspd_height <= cut_out_start, maxCF*((cut_out_end-wspd_height)**3)/ ((cut_out_end-cut_out_start))**3)
    ds_temp['windCF'] = ds_temp.windCF.where(wspd_height <= cut_out_start, maxCF*((cut_out_end-wspd_height)/(cut_out_end-cut_out_start)))

    ds_temp['windCF'] = ds_temp.windCF.where(wspd_height <= cut_out_end, 0)

    return ds_temp.windCF


print('NOTIFY: Starting the mega loop')
# %%
# =============================================================================
# Starting the mega loop
# =============================================================================

# fix the wind dataset
wspd100m = np.arange(0., 30.1, step=0.1)
wspd = np.arange(0., 30.1, step=0.1)


# fix the SSRD dataset
t2m = np.arange(-10, 40.1, 0.1)
rsds = np.arange(0., 1001., 1)


rsds_data = np.zeros([501, 1001])
# fill the rsds data array
for i in np.arange(len(rsds)):
    rsds_data[:, i] = rsds[i]

t2m_data = np.zeros([501, 1001])
# fill the t2m data array
for i in np.arange(len(t2m)):
    t2m_data[i, :] = t2m[i]


# =============================================================================
# Here
# =============================================================================


# %%
dsi = xr.Dataset()

# Set RSDS input
dsi["ssrd"] = xr.DataArray(
    data=rsds_data,
    dims=["temperature", "irradiance"],
    coords=dict(
        temperature=("temperature", t2m),
        irradiance=("irradiance", rsds)
    )
)

# Set T2m input
dsi["t2m"] = xr.DataArray(
    data=t2m_data,
    dims=["temperature", "irradiance"],
    coords=dict(
        temperature=("temperature", t2m),
        irradiance=("irradiance", rsds)
    )
)

# Set wspd100m input
dsi["wspd100m"] = xr.DataArray(
    data=wspd100m,
    dims=["wind_speed"],
    coords=dict(
        wind_speed=("wind_speed", wspd100m)
    )
)

# Set wspd100m input
dsi["wspd"] = xr.DataArray(
    data=wspd,
    dims=["wspeed"],
    coords=dict(
        wspeed=("wspeed", wspd)
    )
)


# %%
# =============================================================================
# Doing the calculations for capacity factors
# =============================================================================

ds = xr.Dataset()

# Solar capacity factor calculation Bett method
ds['SPV_bett'] = solar_potential_bett2016(dsi)

#Solar capacity factor calculation Jerez method
ds['SPV_jerez'] = solar_potential_jerez2015(dsi)

#diff in cf
ds['solar_diff_0'] = ds.sel(wspeed=0.).SPV_jerez - ds.SPV_bett


# Wind capacity factor calculation for onshore
ds["WON"] = wind_potential(dsi.wspd100m, height=100.0, alpha=0.143, cut_in_wspd=3.0,
                                  cut_out_start=20.0, cut_out_end=25.0, rated_wspd=11.0, maxCF=maxCF_on)

# =============================================================================
# Plotting
# =============================================================================


# plot the solarCF
# plt.figure(1)
# ds.sel(irradiance=1000.).SPV_jerez.plot()

# plt.figure(2)
# ds.SPV_bett.plot()

# plt.figure(3)
# ds.sel(wspeed=0.).SPV_jerez.plot()


# plt.figure(4)
# ds.sel(wspeed=5.).SPV_jerez.plot()


# plt.figure(5)
# ds.sel(wspeed=20.).SPV_jerez.plot()


# plt.figure(9)
# ds.solar_diff_0.plot()


# Plot the windCF
plt.figure(10)
ds.WON.plot()









