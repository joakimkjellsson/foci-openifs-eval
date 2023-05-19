import numpy as np
import xarray as xr

def locate_esmdir(machine):
    
    # where to find data
    if machine == 'sci':
        esmdir = '/data/user/jkjellsson/esm-experiments/focioifs/'
    elif machine == 'nesh':
        esmdir = '/gxfs_work1/geomar/smomw352/esm-experiments/'
        oifs_area = '/gxfs_work1/geomar/smomw352/esm-experiments/FOCI_GJK010/outdata/oifs/areacella.nc'
    else:
        print(' ERROR: Unknown machine: %s ' % (machine,))
        
    return esmdir

def locate_nemo_mesh(machine):
    if machine == 'nesh':
        mesh_mask = '/gxfs_work1/geomar/smomw352/foci_input2/oasis3_openifs43r3-tco95_orca05/opa/mesh_mask.nc'
    return mesh_mask
    

def read_nemo_mesh(machine='nesh'):
    
    # find esm dir
    nemo_mesh = locate_nemo_mesh(machine)
    
    # NEMO mesh file has "z" as vertical coordinate
    # but the grid_T files have "deptht" so we need to rename
    ds_mesh = xr.open_dataset(nemo_mesh)
    
    tarea = (ds_mesh['e1t'] * ds_mesh['e2t']).sel(t=0)
    tarea.name = 'tarea'
    dxt, dyt = ds_mesh['e1t'].sel(t=0), ds_mesh['e2t'].sel(t=0)
    tvol = (ds_mesh['e1t'] * ds_mesh['e2t'] * 
            ds_mesh['e3t_0']).sel(t=0).rename({'z':'deptht'})
    tvol.name = 'tvolume'
    tmask = ds_mesh['tmask'].sel(t=0).rename({'z':'deptht'})
    tmask.name = 'tmask'
    
    uarea = (ds_mesh['e1u'] * ds_mesh['e2u']).sel(t=0)
    uarea.name = 'uarea'
    umask = ds_mesh['umask'].sel(t=0).rename({'z':'deptht'})
    umask.name = 'umask'
    
    varea = (ds_mesh['e1v'] * ds_mesh['e2v']).sel(t=0)
    varea.name = 'varea'
    vmask = ds_mesh['vmask'].sel(t=0).rename({'z':'deptht'})
    vmask.name = 'vmask'
    
    ds = xr.merge([tarea, uarea, varea, dxt, dyt, tvol, tmask, umask, vmask])
    return ds

def read_openifs(exp_list, time_list, version_list=[], grid='regular_sfc', freq='1m', machine='nesh'):
    
    # find esm dir
    esmdir = locate_esmdir(machine)
    
    # if no version_list, assume all are 1
    if len(version_list) == 0:
        for exp in exp_list:
            version_list.append(1)
      
    # list for all data
    ds_all = []
    for exp,time,ver in zip(exp_list,time_list,version_list):
        
        if freq == '1y':
            files = '%s/%s/outdata/oifs/ym/*1y*regular_sfc.nc' % (esmdir,exp,)
        else:
            files = '%s/%s/outdata/oifs/*%s*regular_sfc.nc' % (esmdir,exp,freq)
        print(files)
        
        # open multi-file data set. We need to use cftime since the normal python calendar stops working after 2300. 
        # also, we rename time variable from time_counter to time to make life easier
        ds = xr.open_mfdataset(files,combine='nested', 
                               concat_dim="time_counter", use_cftime=True,
                               data_vars='minimal', coords='minimal',
                               compat='override', parallel=True).rename({'time_counter':'time'}).sel(time=time)
        ds_all.append(ds)
        
    return ds_all


def read_nemo(exp_list, time_list, grid='grid_T', freq='1m', machine='nesh', decode_timedelta=True):
    
    # find esm dir
    esmdir = locate_esmdir(machine)
    
    # get NEMO mesh
    ds_mesh = read_nemo_mesh(machine)
    
    # list for all data
    ds_all = []
    for exp,time in zip(exp_list,time_list):
        
        if freq == '1y':
            files = '%s/%s/outdata/nemo/ym/%s*1y*%s.nc' % (esmdir,exp,exp,grid)
        else:
            files = '%s/%s/outdata/nemo/%s*%s*%s.nc' % (esmdir,exp,exp,freq,grid)
        print(files)
        
        # open multi-file data set. We need to use cftime since the normal python calendar stops working after 2300. 
        # also, we rename time variable from time_counter to time to make life easier
        ds = xr.open_mfdataset(files,combine='nested', 
                               concat_dim="time_counter", use_cftime=True,
                               data_vars='minimal', coords='minimal',
                               decode_timedelta=decode_timedelta,
                               compat='override', parallel=True
                              ).rename({'time_counter':'time'}).sel(time=time)
        
        # add mesh to Dataset
        _ds = xr.merge([ds, ds_mesh])
        
        ds_all.append(_ds)
        
    return ds_all


def read_amoc(exp_list, time_list, machine='nesh'):
    
    # find esm dir
    esmdir = locate_esmdir(machine)
    
    derived_list = ['moc','amoc_max_25.000N','amoc_max_45.000N']
    derived_name = ['moc','amoc25','amoc45']
    
    # list for all data
    ds_all = []
    for exp,time in zip(exp_list,time_list):
        
        ds_derived = []
        
        for i,(derived,name) in enumerate(zip(derived_list,derived_name)):
            
            files = '%s/%s/derived/nemo/%s*%s.nc' % (esmdir,exp,exp,derived)
            
            # open multi-file data set. We need to use cftime since the normal python calendar stops working after 2300. 
            # also, we rename time variable from time_counter to time to make life easier
            ds = xr.open_mfdataset(files,combine='nested', 
                                   concat_dim="time_counter", use_cftime=True,
                                   data_vars='minimal', coords='minimal',
                                   compat='override',parallel=True
                                  ).rename({'time_counter':'time'}).sel(time=time)
            
            if i > 0:
                ds = ds.rename({'AMOC_MAX':name})
            
            ds_derived.append(ds)
        
        _ds = xr.merge(ds_derived)
        ds_all.append(_ds)
        
    return ds_all

#
# global mean for OpenIFS
#
def global_mean(data, lonname='lon', latname='lat'):
    weights = np.cos(np.deg2rad(data.lat))
    weights.name = "weights"
    
    data_wgt = data.weighted(weights)
    data_mean = data_wgt.mean((lonname, latname))
    
    return data_mean

#
# global mean for NEMO
#
def global_mean_nemo(data, mask, area, lonname='x', latname='y'):
    
    # Weighted global mean
    data_wgt = data.where(mask == 1).weighted(area)
    data_mean = data_wgt.mean((lonname,latname))
    
    return data_mean 

#
# compute sea ice area
#
def seaice_areas(ds, areacello, lsm, sicname='ileadfra', latname='nav_lat'):
    
    # scale from m2 to million km2
    icescale = 1e-12
    
    # ice area = icefrac * cell area
    _nh = (ds[sicname].where(ds[latname] > 0) * areacello).sum(('x','y')) * icescale
    _sh = (ds[sicname].where(ds[latname] < 0) * areacello).sum(('x','y')) * icescale
    
    # ice extent = cell area where icefrac > 0.15
    _nh2 = (ds[sicname].where(ds[latname] > 0).where(ds[sicname] > 0.15) * areacello).sum(('x','y')) * icescale
    _sh2 = (ds[sicname].where(ds[latname] < 0).where(ds[sicname] > 0.15) * areacello).sum(('x','y')) * icescale
    
    # give dataarrays names
    _nh.name = 'ar_sia'
    _sh.name = 'an_sia'
    _nh2.name = 'ar_sie'
    _sh2.name = 'an_sie'
    _ds_n = _nh.to_dataset()
    _ds_s = _sh.to_dataset()
    _ds_n2 = _nh2.to_dataset()
    _ds_s2 = _sh2.to_dataset()
    
    # put results in one dataset
    _ds = xr.merge([_ds_n, _ds_s, _ds_n2, _ds_s2])
    
    return _ds


def ice_volumes(ds):
    
    # iicethic is cell average ice thickness
    # i.e. if half cell is covered by 2m thick ice, iicethic is 1m
    _nh = (ds['iicethic'].where(lat_05 > 0) * areacello_05).sum(('x','y')) 
    _sh = (ds['iicethic'].where(lat_05 < 0) * areacello_05).sum(('x','y')) 
    
    _nh.name = 'ar_siv'
    _sh.name = 'an_siv'
    _ds_n = _nh.to_dataset()
    _ds_s = _sh.to_dataset()
    _ds = xr.merge([_ds_n, _ds_s])
    
    return _ds