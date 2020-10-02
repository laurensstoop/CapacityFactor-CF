#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Spyder Editor

Restructered on Wed 16 Oct 2019 17:15

@author: Laurens Stoop - l.p.stoop@uu.nl
"""


#%%
# =============================================================================
# Dependencies
# =============================================================================


# Importing modules
import xarray as xr
#import regionmask as rm
#import matplotlib.pyplot as plt
import numpy as np
import datetime
#import cartopy.crs as ccrs
#import geopandas as gp



# Run fist 
# cdo sellonlatbox,0,10,49,55 ERA5-EU_ssrd_2011.nc ERA5-NL_ssrd_2011.nc

# Select the years to run
years = np.array([
#            '1979','1980','1981',
#            '1982','1983','1984',
#            '1985','1986','1987',
#            '1988','1989','1990',
#            '1991','1992','1993',
#            '1994','1995','1996',
#            '1997','1998','1999',
#            '2000','2001',
            '2002',
            '2003','2004','2005',
            '2006','2007','2008',
            '2009','2010','2011',
            '2012','2013','2014',
            '2015','2016','2017',
            '2018'
#            '2016'
            
        ])


# File locations
file_path = '/media/DataDrive/ERA5-EU_BASE/'
out_path = '/media/DataGate2/Erik/'
#file_path = '/home/stoop/Documents/Data/ERA5/'
#era_path = file_path+'netherlands/'
era_path = file_path+''


# Max CF for the RES
maxCF_on = 0.95
maxCF_off = 0.95


print('NOTIFY: Basic setup done, defining functions')
#%%
# =============================================================================
# Function definitions
# =============================================================================

# Function to determine the solar capacity factor
def solar_potential(ds):
    
    # The constant definitions
    c = np.array([4.3, 0.943, 0.028, -1.528]) # Cell temperature constants in [degree C, unitless, degree C * m**2 /W, degree C *s/m
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
    
    return ds_temp.solarCF


# Function to determine the windpotential
def wind_potential(wspd, height, alpha, cut_in_wspd, cut_out_start, cut_out_end, rated_wspd, maxCF):
    
    # First we create a new dataset
    ds_temp = xr.Dataset()
    
    # Rescaling the windspeed to the requested height
    wspd_height = wspd * (height / 100)**alpha
    
    # We fill it with the windpotential without considering the information of the wind turbine
    ds_temp['windCF'] = maxCF* ((wspd_height**3 - cut_in_wspd**3) / (rated_wspd**3 - cut_in_wspd**3))
    
    # Now we reduce the wind potential to 1 above the rated windspeed
    ds_temp['windCF'] = ds_temp.windCF.where(wspd_height <= rated_wspd, maxCF)
    
    # Now we set the wind potential to 0 below the cut-in windspeed
    ds_temp['windCF'] = ds_temp.windCF.where(wspd_height >= cut_in_wspd, 0)
    
    # Now we set the wind potential to 0 above the cut-out windspeed
    ds_temp['windCF'] = ds_temp.windCF.where(wspd_height <= cut_out_start, maxCF*((cut_out_end)**3 - wspd_height**3) / ((cut_out_end)**3 -(cut_out_start)**3))
    ds_temp['windCF'] = ds_temp.windCF.where(wspd_height <= cut_out_end, 0)
    
    return ds_temp.windCF



print('NOTIFY: Starting the mega loop')
#%%
# =============================================================================
# Starting the mega loop
# =============================================================================

# The mega loop
for year in years:

    print('NOTIFY: Working on '+str(year))

    
    # Files to load
    ssrd = era_path+'ERA5-EU_ssrd_'+str(year)+'.nc'
    t2m = era_path+'ERA5-EU_t2m_'+str(year)+'.nc'
    wspd = era_path+'ERA5-EU_wspd_'+str(year)+'.nc'
    wspd100m = era_path+'ERA5-EU_wspd100m_'+str(year)+'.nc'
    
    print('Working on '+str(year)+': Started to load the files')
    #%%
    # =============================================================================
    # Loading in the files
    # =============================================================================
     
    # Combine the data for easiness
    ds = xr.Dataset()

    # Open the netCDF file of the data to cut. Units are checked!
    ds['ssrd'] = xr.open_dataset(ssrd).ssrd # in W/m**2 per timestep (= 1 hour)
    ds['t2m'] = xr.open_dataset(t2m).t2m # in degree C
    ds['wspd'] = xr.open_dataset(wspd).wspd # in m/s
    ds['wspd100m'] = xr.open_dataset(wspd100m).wspd100m # in m/s
    

    
    print('Working on '+str(year)+': Loading done, doing the calculations for the CFs')
    #%%
    # =============================================================================
    # Doing the calculations for capacity factors
    # =============================================================================
    
    # Solar capacity factor calculation
    ds['solarCF'] = solar_potential(ds)
    
    # Wind capacity factor calculation for offshore
    ds['windCF_off'] = wind_potential(ds.wspd100m, height=122.0, alpha=0.11, cut_in_wspd=3.0, cut_out_start=20.0, cut_out_end=25.0, rated_wspd=11.0, maxCF=maxCF_off)
    
    # Wind capacity factor calculation for onshore
    ds['windCF_on'] = wind_potential(ds.wspd100m, height=98.0, alpha=0.143, cut_in_wspd=3.0, cut_out_start=20.0, cut_out_end=25.0, rated_wspd=11.0, maxCF=maxCF_on)
 
    # =============================================================================
    # Setting the attributes    
    # =============================================================================
    
    # Set the global atributes
    ds.attrs.update(
            author = 'Laurens Stoop UU/KNMI/TenneT',
            created = datetime.datetime.today().strftime('%d-%m-%Y'),
            map_area = 'NL',
            grid_type = 'gaussian',
            data_source = 'ERA5 reanalysis data, contains modified Copernicus Climate Change Service information [08-03-2019]'
            )
    
    # Set the demand attributes
    ds.solarCF.attrs.update(
            units = ' ',
            short_name = 'solarCF',
            long_name = 'Capacity factor for photovoltaics',
            method = 'Adopted by L.P. Stoop, based on Jerez et al., 2015', 
            description = 'Hourly capacity factor of solar panels')

    # Set the demand attributes
    ds.windCF_on.attrs.update(
            units = ' ',
            short_name = 'windCF_on',
            long_name = 'Capacity factor for wind onshore with hubheigh 98 meter',
            method = 'Adopted by L.P. Stoop, based on Jerez et al., 2015', 
            description = 'Hourly capacity factor of onshore wind turbines')
    
    # Set the demand attributes
    ds.windCF_off.attrs.update(
            units = ' ',
            short_name = 'windCF_off',
            long_name = 'Capacity factor for wind offshore with hubheigh 122 meter',
            method = 'Adopted by L.P. Stoop, based on Jerez et al., 2015', 
            description = 'Hourly capacity factor of offshore wind turbines')
    
    
    #%%
    # =============================================================================
    # Saving the data
    # =============================================================================
    
    # Removing unneeded variables
    ds = ds.drop(['wspd', 'ssrd', 'wspd100m'])
    
    # Saving the file
    ds.to_netcdf(out_path+'ERA5-EU_Erik-CF_'+str(year)+'.nc')
    
    # Closing files
    ds.close()