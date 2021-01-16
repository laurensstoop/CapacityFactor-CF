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
path_RegionDefinition = '/media/DataDrive/Other/RegionDefinitions/'

path_CFdata = '/media/DataGate3/ERA5-EU_CF/'


print('NOTIFY: Initialization is complete, Skynet active')
#%%
# =============================================================================
# Load in the base file where stuff can be, select the regions, save the files
# =============================================================================

# Select the data for the whole region
ds = salem.open_xr_dataset(path_TYNDP+'constant.nc')

# Select the shapefile with the Economic Exclusive Zones for all countries in the world
shdf_eez = salem.read_shapefile(path_RegionDefinition+'EEZ/EEZ_land_v2_201410.shp')
shdf_nuts = salem.read_shapefile(path_RegionDefinition+'nuts-2016/NUTS_0/NUTS_RG_01M_2016_4326_LEVL_0.shp')

# Extra data for outliers
shdf_BA = salem.read_shapefile(path_RegionDefinition+'BA_Bosnia_Herzegovina_adm0/BIH_adm0.shp')
shdf_UA = salem.read_shapefile(path_RegionDefinition+'UA_Ukraine_adm0/ukr_admbnda_adm0_q2_sspe_20171221.shp')

# The nations for which we want info
countrylist = np.array([
#         ['Albania','AL'],
#         ['Austria','AT'],
#         ['Bosnia & Herzegovina','BA'], 
#         ['Belgium','BE'],
#         ['Bulgaria','BG'],
#         ['Switzerland','CH'],  
#         ['Cyprus','CY'],
#         ['Czech Republic','CZ'],
#         ['Denmark','DK'],
#         ['Germany','DE'],
#         ['Estonia','EE'],
#         ['Greece','EL'],
#         ['Spain','ES'],
#         ['Finland','FI'],
#         ['France','FR'],
#         ['Croatia','HR'],
#         ['Hungary','HU'],
#         ['Ireland','IE'],
# # #        ['Iceland','IS'],
#         ['Italy', 'IT'],
#         ['Lithuania','LT'],
# # #        ['Liechtenstein','LI'],
#         ['Luxembourg','LU'],
#         ['Latvia','LV'],  
#         ['Montenegro', 'ME'],
#         ['Macedonia', 'MK'],
        # ['Malta','MT'],
        ['Netherlands','NL'], #
        ['Norway','NO'], #
        ['Poland','PL'], #
        ['Portugal','PT'],
        ['Romania','RO'],
        ['Serbia', 'RS'],
        ['Sweden','SE'],
        ['Slovenia','SI'],
        ['Slovakia','SK'],
        ['Turkey','TR'],
        ['Ukraine', 'UA'],
        ['United Kingdom','UK']
        ])

#%%
# =============================================================================
# Looping over countries
# =============================================================================

# For loop over all countries
for country_name, country_code in countrylist:
    
    print('NOTIFY: Now we select the dish from '+ country_name)
    
    # filter out the outliers Bosnia & Herzegovina
    if country_code =='BA':
               
        # Select a country by name and only use this country from the shape file (shdf)
        shape_eez = shdf_eez.loc[shdf_eez['Country'] == country_name]  
        shape_nuts = shdf_BA.loc[shdf_BA['ISO2'] == country_code]  
    

    # Filter out the outlier Ukraine           
    elif country_code == 'UA':
                        
        # Select a country by name and only use this country from the shape file (shdf)
        shape_eez = shdf_eez.loc[shdf_eez['Country'] == country_name]  
        shape_nuts = shdf_UA.loc[shdf_UA['ADM0_EN'] == country_name]  
       
    # if the country isn't an outlier, we go ahead
    else:        
        
        # Select a country by name and only use this country from the shape file (shdf)
        shape_eez = shdf_eez.loc[shdf_eez['Country'] == country_name]  
        shape_nuts = shdf_nuts.loc[shdf_nuts['NUTS_ID'] == country_code]  

    
    # Set a subset (dsr) of the DataSet (ds) based on the selected shape (shdf)
    ds_eez = ds.salem.subset(shape=shape_eez, margin = 25)
    ds_nuts = ds.salem.subset(shape=shape_nuts, margin = 50)
    
    # Select only the region within the subset (dsr) [I am not sure what this does and doesn't do]
    ds_eez = ds_eez.salem.roi(shape=shape_eez)
    ds_nuts = ds_nuts.salem.roi(shape=shape_nuts)
        
        
        
    # Make a quick map to check the selected data, if only one country is selected!
    # if np.size(countrylist) == 2:
    #     # ds_eez.random.salem.quick_map();
    #     ds_nuts.random.salem.quick_map();
        
    
    # Fill all non country values with 0
    ds_eez = ds_eez.fillna(0.) #1E-20)
    ds_nuts = ds_nuts.fillna(0.) #1E-20)
    
    #Define the offshore region
    ds_offshore = ds_eez - ds_nuts
    
    # Save the country mask to a file
    ds_offshore.to_netcdf(path_TYNDP+'CountryDefinitions_ERA5-EU/CountryDefinitions_ERA5-EU_offshore_'+country_code+'.nc')
    ds_nuts.to_netcdf(path_TYNDP+'CountryDefinitions_ERA5-EU/CountryDefinitions_ERA5-EU_onshore_'+country_code+'.nc')
    


