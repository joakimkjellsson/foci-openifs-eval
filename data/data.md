Compute global-mean variables from observations
===============================================

* Note 1: All datasets are (or were as of May 2023) freely accessible. 

* Note 2: CDO is used for calculations. It is available from https://code.mpimet.mpg.de/projects/cdo but was installed via MacPorts. https://www.macports.org/. `sudo port install cdo`.

* Note 3: Computed averages are not included on the git repo to avoid any potential licensing issues. That being said, if you contact me I may know a guy who knows a guy who may have the data... 

Compute global-mean 2m air temperature from daily ERA-5 data
Retrieved from DKRZ data pool
Also available from CDS https://cds.climate.copernicus.eu/cdsapp#!/dataset/reanalysis-era5-single-levels-monthly-means?tab=overview 
`cdo -fldmean -yearmean /gxfs_work1/geomar/smomw352/reanalysis_obs/E5_1D_T2M_1979-2021.nc E5_1Y_T2M_globalmean.nc`

Compute global-mean TOA balance from CERES
Retrieved from https://ceres.larc.nasa.gov/data/
`cdo -fldmean -yearmean -select,name=toa_net_all_mon /gxfs_work1/geomar/smomw352/ceres/CERES_EBAF_Ed4.1.nc ceres_toa_globalmean.nc`

Compute time-mean fluxes from CERES
`cdo -timmean -select,name=toa_sw_all_mon,toa_lw_all_mon,cldarea_total_daynight_mon,solar_mon,toa_sw_clr_t_mon,toa_lw_clr_t_mon,toa_cre_sw_mon,toa_cre_lw_mon,sfc_cre_net_lw_mon,sfc_cre_net_sw_mon /gxfs_work1/geomar/smomw352/ceres/CERES_EBAF_Ed4.1.nc CERES_timmean.nc`

TOA and surface heat fluxes from ERA-5
Retrieved from https://cds.climate.copernicus.eu/cdsapp#!/dataset/reanalysis-era5-single-levels-monthly-means?tab=overview

Compute global mean precipitation from GPCP
Retrieved from https://www.ncei.noaa.gov/data/global-precipitation-climatology-project-gpcp-monthly/access/
`cdo -fldmean -yearmean /gxfs_work1/geomar/smomw352/reanalysis_obs/precip.mon.mean.1979-01_2014-07.nc GPCP_1Y_globalmean.nc`

Compute Arctic and Antarctic sea-ice area from HadISST
Retrieved from https://www.metoffice.gov.uk/hadobs/hadisst/data/download.html
`cdo -yearmean -select,startdate=1979-01-01T00:00:00,enddate=2020-01-01T00:00:00 -selname,sic /gxfs_work1/geomar/smomw352/reanalysis_obs/HadISST_ice.nc hadisst_mean.nc`
`cdo gridarea hadisst_mean.nc hadisst_area.nc`
`cdo -fldsum -sellonlatbox,-180,180,0,90 -mul hadisst_mean.nc hadisst_area.nc hadisst_arctic.nc`
`cdo -fldsum -sellonlatbox,-180,180,-90,0 -mul hadisst_mean.nc hadisst_area.nc hadisst_antarctic.nc`
`cdo -ymonmean -select,startdate=1979-01-01T00:00:00,enddate=2020-01-01T00:00:00 /gxfs_work1/geomar/smomw352/reanalysis_obs/HadISST_ice.nc hadisst_ice_ymonmean.nc`

Compute AMOC strength from RAPID
Retrieved from https://rapid.ac.uk/rapidmoc/rapid_data/datadl.php 
Look for "MOC Transport Time Series" 
`cdo -yearmean -select,name=moc_mar_hc10 moc_transports.nc rapid_amoc.nc`

Compute Arctic and Antarctic sea-ice thickness and volume from GIOMAS
http://psc.apl.washington.edu/zhang/Global_seaice/index.html
Zhang & Rothrock (2003) model: http://psc.apl.washington.edu/zhang/Pubs/POIM.pdf
with assimilated sea-ice concentration
```bash
./get_giomas_area_thick.sh
cdo -expr,'area=dxt*dyt' $WORK/reanalysis_obs/GIOMAS/heff.H1979.nc giomas_area.nc
cdo mergetime $WORK/reanalysis_obs/GIOMAS/heff_????.nc $WORK/reanalysis_obs/GIOMAS/heff_1979-2022.nc
cdo ymonmean $WORK/reanalysis_obs/GIOMAS/heff_1979-2022.nc heff_1979-2022_ymonmean.nc
```

Oceanic turbulent heat fluxes from ICOADS v3.0 (2deg version)
Source: https://psl.noaa.gov/data/gridded/data.coads.1deg.html
```bash
cdo -yseasmean -select,startdate=1960-01-01T00:00:00,enddate=2019-01-01T00:00:00 $WORK/reanalysis_obs/ICOADS_lflx.mean.nc ICOADS_lflx_yseasmean.nc 
cdo -yseasmean -select,startdate=1960-01-01T00:0000:00,enddate=2019-01-01T00:00:00 $WORK/reanalysis_obs/ICOADS_sflx.mean.nc ICOADS_sflx_yseasmean.nc
cdo merge ICOADS_*.nc ICOADS_thf_yseasmean.nc 
cdo -aexpr,'thf=lflx+sflx' ICOADS_thf_yseasmean.nc ICOADS_flx_yseasmean.nc
```

