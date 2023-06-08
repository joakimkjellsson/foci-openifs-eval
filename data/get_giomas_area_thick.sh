#!/bin/bash

module load cdo nco

for (( year=1979 ; year<=2022 ; year++ )) ; do
	for var in heff ; do 

		# Get data
		#wget --no-check-certificate https://pscfiles.apl.washington.edu/zhang/Global_seaice/${var}.H${year}.nc.gz
		#gunzip ${var}.H${year}.nc.gz

		# Get lon,lat and set correct time axis
		cdo -setctomiss,9999.9 -select,name=${var},lon,lat -chname,lat_scaler,lat -chname,lon_scaler,lon -settunits,days -settaxis,${year}-01-15,00:00,1month heff.H${year}.nc tmp.nc 
                
		# Set attributes so CDO knows what grid this is
                ncatted -a standard_name,lon,c,c,"longitude" -a units,lon,c,c,"degrees_east" -a standard_name,lat,c,c,"latitude" -a units,lat,c,c,"degrees_north" -a coordinates,${var},c,c,"time lat lon" tmp.nc

		mv tmp.nc ${var}_${year}.nc 

	done
done


