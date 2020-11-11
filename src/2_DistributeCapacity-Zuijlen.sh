#!/bin/bash
# In this file the data is cut for netherlands
# Author: Laurens Stoop, UU/KNMI/TenneT

# The data used for this distribution is from Bas van Zuijlen

distributions='offWind onWind solarPV'

for var in $distribution
do
    
    # As I consider only one form of PV, we combine the utility and roofbased PV
    if [[ ${var} == 'solarPV' ]]
    then
        cdo enssum RES_roofPV_cap_distr.nc RES_utilPV_cap_distr.nc RES_solarPV_cap_distr.nc
    fi
    
    # Remap the original files to the european ERA5 style (using the conservative method)
    cdo -remapcon2,constant.nc RES_${var}_cap_distr.nc temp_${var}.nc
    
    # Remove the negative installation (due to remapping) and set missing to zero
    cdo setrtomiss,-10,0 temp_${var}.nc ${var}.nc
    cdo setmisstoc,0 ${var}.nc ${var}2.nc
    
    # change the variable name
    cdo chname,CAP,${var} ${var}2.nc CapacityDistribution-Zuijlen_ERA5_${var}.nc
            
done



# CURRENTLY DONE MANUALLY