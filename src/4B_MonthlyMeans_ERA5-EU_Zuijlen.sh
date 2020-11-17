#!/usr/bin/bash

# """
# Created on Mon 16 Nov 2020 22:15
# 
# @author: Laurens Stoop - l.p.stoop@uu.nl
# """




for Y in $(seq 1950 2019);do  
    echo ${Y}
    cdo -f nc ymonmean ./ERA5-EU_EV-Zuijlen_${Y}.nc ./MonthlyMean/ERA5-EU_EV-Zuijlen_MM_${Y}.nc
done

