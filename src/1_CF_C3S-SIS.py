# -*- coding: utf-8 -*-
"""
Spyder Editor

Created on Tue 05 Jan 2021 17:34

@author: Laurens Stoop - l.p.stoop@uu.nl
"""

# to unpack all files after download use: for z in ./origin/*.zip; do unzip "$z" -d ./unpack/; done
    


#%%
# =============================================================================
# Dependencies
# =============================================================================

# Get the dependencies
import cdsapi
import datetime as dt
import os.path

#%%
# =============================================================================
# Run definitions
# =============================================================================

# aggregation level
aggregation = 'original_grid'

# define the storage location
file_path = '/media/DataGate2/ERA5-EU_C3S-SIS/origin/'


# The year definitions
years = [   
            # '1979', '1980', '1981',
            # '1982', '1983', '1984',
            # '1985', '1986', '1987',
            # '1988', '1989', '1990',
            # '1991', '1992', '1993',
            # '1994', '1995', '1996',
            # '1997', '1998', '1999',
            # '2000', '2001', '2002',
            # '2003', '2004', '2005',
            # '2006', '2007', '2008',
            # '2009', '2010', '2011',
            # '2012', '2013', '2014',
            # '2015', '2016', '2017',
            # '2018', '2019', 
            '2020'
            ]




#%%
# =============================================================================
# Download loop
# =============================================================================

# Make a shortcut for the CDS download client
c = cdsapi.Client()

# Run over the years
for year in years:

    # Let's notify our terminal where we are!
    print(dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')+' NOTIFY: Starting to retrieve '+year)
    
      
    # Retrieve SSRD
    file=file_path+'C3S-SIS_'+aggregation+'_'+year+'.zip'
    
    # Check if file exist to allow for easy redo
    if os.path.isfile(file) == True:

        # Tell us the file exist
        print('NOTIFY: this file was allready done! '+file)
    
    # if file doesn't exist, we download it
    elif os.path.isfile(file) == False:

        c.retrieve(
                'sis-energy-derived-reanalysis',
                {
                    'format': 'zip',
                    'temporal_aggregation': 'hourly',
                    'energy_product_type': 'capacity_factor_ratio',
                    'variable': [
                        'solar_photovoltaic_power_generation', 
                        'wind_power_generation_offshore', 
                        'wind_power_generation_onshore',
                        ],
                    'spatial_aggregation': aggregation,
                    'month': [
                        '01', '02', '03',
                        '04', '05', '06',
                        '07', '08', '09',
                        '10', '11', '12',
                    ],
                    'year': year
                },
                file)
