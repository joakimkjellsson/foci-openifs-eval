#!/bin/bash

# Remove the date in the global attribute since its super long
# Also remove the valid_min and max since those mask most of the data otherwise
ncatted -O --glb_att_add date=' ' \
-a valid_min,mld_da_mean,m,f,0  -a valid_max,mld_da_mean,m,f,5000 \
-a valid_min,mld_dt_mean,m,f,0  -a valid_max,mld_dt_mean,m,f,5000 \
Argo_mixedlayers_monthlyclim_04142022.nc Argo_MLD.nc

# Extract only the mean fields
ncks -O -v lon,lat,mld_da_mean,mld_dt_mean Argo_MLD.nc Argo_MLD_slim.nc

# Rename dimensions to standard names
ncrename -O -d iLON,lon -d iLAT,lat -d iMONTH,time Argo_MLD_slim.nc

# Reorder dimensions 
ncpdq -O -a time,lat,lon Argo_MLD_slim.nc Argo_MLD_slim_order.nc

# Set a proper time axis
cdo -O settunits,days -settaxis,2000-01-15,00:00,1month Argo_MLD_slim_order.nc Argo_MLD_slim_taxis.nc

rm Argo_MLD.nc Argo_MLD_slim.nc Argo_MLD_slim_order.nc 
mv Argo_MLD_slim_taxis.nc Argo_MLD.nc 
