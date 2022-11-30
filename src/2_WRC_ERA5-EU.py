#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Spyder Editor

Restructered on Wed 10 Nov 2020 14:15

@author: Laurens Stoop - l.p.stoop@uu.nl
"""


#%%
# =============================================================================
# Dependencies
# =============================================================================


# Importing modules
import xarray as xr
import numpy as np
import datetime
import os.path


# Select the years to run
years = np.array([
            # '1950', '1951', '1952',
            # '1953', '1954', '1955',
            # '1956', '1957', '1958',
            # '1959', '1960', '1961',
            # '1962', '1963', '1964',
            # '1965', '1966', '1967',
            # '1968', '1969', '1970',
            # '1971', '1972', '1973',
            # '1974', '1975', '1976',
            # '1977', '1978',
            # '1979', '1980', '1981',
            # '1982', '1983', '1984',
            # '1985', '1986', '1987',
            # '1988', '1989', 
            '1990',
            # '1991', '1992', '1993',
            # '1994', '1995', '1996',
            # '1997', '1998', '1999',
            # '2000', '2001', '2002',
            # '2003', '2004', '2005',
            # '2006', '2007', '2008',
            # '2009', '2010', '2011',
            # '2012', '2013', '2014',
            # '2015', '2016', '2017',
            # '2018', '2019', '2020',
            # '2021'
        ])


# File locations
# file_path = '/media/DataStager1/ERA5-EU_BASE/'
# file_path = '/media/DataDrive/ERA5BE-EU_BASE/'
# file_path = '/media/DataStager1/ERA5-EU_BASE/'
file_path = '/media/DataGate2/ERA5/origin/'
# out_path = '/media/DataGate3/ERA5-EU_CF/'
out_path = '/media/DataStager1/ERA5_CF/'
#file_path = '/home/stoop/Documents/Data/ERA5/'



# Max CF for the RES
maxCF_on = 0.95
maxCF_off = 0.95


print('NOTIFY: Basic setup done, defining functions')
#%%
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
    ds_temp['windCF'] = maxCF* ((wspd_height**3 - cut_in_wspd**3) / (rated_wspd**3 - cut_in_wspd**3))
    
    # Now we reduce the wind potential to 1 above the rated windspeed
    ds_temp['windCF'] = ds_temp.windCF.where(wspd_height <= rated_wspd, maxCF)
    
    # Now we set the wind potential to 0 below the cut-in windspeed
    ds_temp['windCF'] = ds_temp.windCF.where(wspd_height >= cut_in_wspd, 0)
    
    # Now we set the wind potential to 0 above the cut-out windspeed
    # ds_temp['windCF'] = ds_temp.windCF.where(wspd_height <= cut_out_start, maxCF*((cut_out_end)**3 - wspd_height**3) / ((cut_out_end)**3 -(cut_out_start)**3))
    ds_temp['windCF'] = ds_temp.windCF.where(wspd_height <= cut_out_start, maxCF*((cut_out_end-wspd_height)/(cut_out_end-cut_out_start)))
    ds_temp['windCF'] = ds_temp.windCF.where(wspd_height <= cut_out_end, 0)
    
    return ds_temp.windCF



print('NOTIFY: Starting the mega loop')
#%%
# =============================================================================
# Starting the mega loop
# =============================================================================

# The mega loop
for year in years:
    for month in ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12']:
        # Define the file name
        file_save = out_path+'ERA5_CF_'+year+month+'.nc'
        
        
        # Check if file allready exist, then get out
        if os.path.isfile(file_save) == True:
            
            # Tell us the file exist
            print('NOTIFY: Allready applied for year '+year+month+'!')
          
            
        # IF the file doesn't exist, apply the distribution
        elif os.path.isfile(file_save) == False:
            
            # Tell us the file exist
            print('NOTIFY: Now starting work on '+year+month+'!')    
        
                    
            # Files to load
            data_file = file_path+'ERA5-EU_'+year+month+'.nc'
            
            print('Working on '+str(year)+': Started to load the files')
            #%%
            # =============================================================================
            # Loading in the files
            # =============================================================================
             
            # Combine the data for easiness
            ds = xr.open_dataset(data_file)
            
            print('                 Cleaning the units')
            #%%
            # =============================================================================
            # Loading in the files
            # =============================================================================
             
            # Combine the u&v component for easiness
            ds['wspd'] = xr.ufuncs.sqrt(ds.u10**2 + ds.v10**2)
            ds['wspd100m'] = xr.ufuncs.sqrt(ds.u100**2 + ds.v100**2)
            ds.wspd.attrs.update(long_name = '10 meter wind speed', units = 'm s**-1')
            ds.wspd100m.attrs.update(long_name = '100 meter wind speed', units = 'm s**-1')
            
            # Conversion to celsius
            ds['t2m'] = ds.t2m - 273.4
            ds['t2m'].attrs.update(units = 'degree C')
                
            # Setting windspeed in hPa
            ds['mpsl'] = ds.msl/1e2
            ds.mpsl.attrs.update(units = 'hPa')
              
            # Getting ssrd fixed in units
            ds['ssrd'] = ds.ssrd/3600.
            ds['ssrd'].attrs.update(units = 'W m**-2')
    
            print('                 Loading done, doing the calculations for the CFs')
            #%%
            # =============================================================================
            # Doing the calculations for capacity factors
            # =============================================================================
            
            # Solar capacity factor calculation Jerez method
            ds['solarCF'] = solar_potential_jerez2015(ds)
            
            # Solar capacity factor calculation Bett method
            # ds['solarCF'] = solar_potential_bett2016(ds)
            
            #diff in cf
            # ds['solar_diff'] = ds.solarCF_jerez - ds.solarCF_bett
            
            # Wind capacity factor calculation for offshore
            ds['windCF_off'] = wind_potential(ds.wspd100m, height=150.0, alpha=0.11, cut_in_wspd=3.0, cut_out_start=20.0, cut_out_end=25.0, rated_wspd=11.0, maxCF=maxCF_off)
            
            # Wind capacity factor calculation for onshore
            ds['windCF_on'] = wind_potential(ds.wspd100m, height=120.0, alpha=0.143, cut_in_wspd=3.0, cut_out_start=20.0, cut_out_end=25.0, rated_wspd=11.0, maxCF=maxCF_on)
         
            
            print('                 Adding the correct attributes to the variables')
            # =============================================================================
            # Setting the attributes    
            # =============================================================================
            
            # Set the global atributes
            ds.attrs.update(
                    author = 'Laurens Stoop UU/KNMI/TenneT',
                    created = datetime.datetime.today().strftime('%d-%m-%Y'),
                    map_area = 'Europe',
                    data_source = 'ERA5 reanalysis data, contains modified Copernicus Climate Change Service information [28-01-2021]'
                    )
            
            # # Set the demand attributes
            # ds.solarCF.attrs.update(
            #         units = ' ',
            #         short_name = 'solarCF',
            #         long_name = 'Capacity factor for photovoltaics',
            #         method = 'Adopted by L.P. Stoop, based on Jerez et al., 2015', 
            #         description = 'Hourly capacity factor of solar panels')
            
            # Set the demand attributes
            ds.solarCF.attrs.update(
                    units = ' ',
                    short_name = 'solarCF',
                    long_name = 'Capacity factor for photovoltaics',
                    method = 'Based on Jerez et al., 2015', 
                    description = 'Hourly capacity factor of solar panels')
        
            # Set the demand attributes
            ds.windCF_on.attrs.update(
                    units = ' ',
                    short_name = 'windCF_on',
                    long_name = 'Capacity factor for wind onshore with hubheigh 100 meter',
                    method = 'Adopted by L.P. Stoop, based on Jerez et al., 2015', 
                    description = 'Hourly capacity factor of onshore wind turbines')
            
            # Set the demand attributes
            ds.windCF_off.attrs.update(
                    units = ' ',
                    short_name = 'windCF_off',
                    long_name = 'Capacity factor for wind offshore with hubheigh 150 meter',
                    method = 'Adopted by L.P. Stoop, based on Jerez et al., 2015', 
                    description = 'Hourly capacity factor of offshore wind turbines')
            
            print('                 Storing the data in the defined location')
            #%%
            # =============================================================================
            # Saving the data
            # =============================================================================
            
            # Removing unneeded variables
            ds = ds.drop(['u10', 'v10', 'u100', 'v100', 'msl', 'ro', 'sro', 'mpsl', 't2m', 'ssrd', 'wspd100m', 'wspd'])
            
            # Saving the file
            ds.to_netcdf(file_save, encoding={'time':{'units':'days since 1900-01-01'}})
            
            # Closing files
            ds.close()
            
            print('                 Finished with '+year+' '+month)