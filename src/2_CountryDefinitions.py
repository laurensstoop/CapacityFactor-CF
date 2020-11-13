#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Restructered on Wed 11 Nov 2020 14:15

@author: Laurens Stoop - l.p.stoop@uu.nl
"""

#%%
# =============================================================================
# Dependencies
# =============================================================================


## Importing modules
import numpy as np
import xarray as xr
import salem

# Set the path for the data
path_TYNDP = '/media/DataDrive/Other/CapacityDistribution/TYNDP/'
path_EEZ = '/media/DataDrive/Other/RegionDefinitions/'


print('NOTIFY: Initialization is complete, Skynet active')
#%%
# =============================================================================
# Load in the base file where stuff can be, select the regions, save the files
# =============================================================================

# Select the data for the whole region
ds = salem.open_xr_dataset(path_TYNDP+'constant.nc')

# Select the shapefile with the Economic Exclusive Zones for all countries in the world
shdf = salem.read_shapefile(location_eezmap+'EEZ_land_v2_201410.shp')

# The nations for which we want info
countrylist = np.array([
        ['Austria','AT'],
        ['Belgium','BE'],
        ['Bulgaria','BG'],
        ['Switzerland','CH'], ######
#        ['Cyprus','CY'],
        ['Czech Republic','CZ'],
        ['Denmark','DK'],
        ['Germany','DE'],
        ['Estonia','EE'],
        ['Greece','EL'],
        ['Spain','ES'],
        ['Finland','FI'],
        ['France','FR'],
        ['Croatia','HR'],
        ['Hungary','HU'],
        ['Ireland','IE'],
#        ['Iceland','IS'],
        ['Lithuania','LT'],
#        ['Liechtenstein','LI'],
#        ['Luxembourg','LU'],
        ['Latvia','LV'], ######
#        ['Malta','MT'],
        ['Netherlands','NL'],
        ['Norway','NO'],
        ['Poland','PL'],
        ['Portugal','PT'],
        ['Romania','RO'],
        ['Sweden','SE'],
        ['Slovenia','SI'], ######
        ['Slovakia','SK'],
        ['United Kingdom','UK']
        ])


# For loop over all countries
for country_name, country_code in countrylist:
    
    print('NOTIFY: Now we select the dish from '+ country_name)
    
    # Select a country by name and only use this country from the shape file (shdf)
    country_shape = shdf.loc[shdf['Country'] == country_name]  
#    print('NOTIFY: 1')    
    
    # Set a subset (dsr) of the DataSet (ds) based on the selected shape (shdf)
    ds_country = ds.salem.subset(shape=country_shape, margin = 10)
#    print('NOTIFY: 2')
    
    # Select only the region within the subset (dsr) [I am not sure what this does and doesn't do]
    ds_country = ds_country.salem.roi(shape=country_shape)
#    print('NOTIFY: 3')
    
    # Make a quick map to check the selected data, if only one country is selected!
    if np.size(countrylist) == 2:
        ds_country.maskocean.salem.quick_map();
    
    # Fill all non country values with 0
    ds_country = ds_country.fillna(1E-20)
    
    # Save the country mask to a file
    ds_country.to_netcdf(location_country+'country_EEZ66_'+country_code+'_ECEarth.nc')
#    print('NOTIFY: 4')


