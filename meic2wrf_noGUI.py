###############################################  meic2wrf  ########################################################
# Authors:     Fan Jin; Zhou Yong-long; Zhang Lei; Xu Xuan-ye; Jiang Pei-ya; Li Zhuo                              #
# Institution: Chengdu AeriDice Environment Technology Co., Ltd.; Chengdu University of Information & Technology; #
#              Chinese Academy of Meteorological Sciences                                                         #
# E-mail:      jin.fan@outlook.com                                                                                #
# Environment: Python 3.7.7; pynio 1.5.5                                                                          #
###################################################################################################################
# June 8, 2020, added noGUI script (by Hao Lyu)
# Environment added: area(https://github.com/scisco/area)

import fnmatch
import glob
import os
import shutil

import Nio
import numpy as np

from int_dis import *

meic2wrf = meic2wrf#_interp  #用线性插值替代最邻近插值
ll_area  = ll_area      #更高精度计算每块meic网格面积
# 排放源高度分布
agr_z_d = [1.000, 0.000, 0.000, 0.000, 0.000, 0.000, 0.000, 0.000, 0.000, 0.000, 0.000]
ind_z_d = [0.602, 0.346, 0.052, 0.000, 0.000, 0.000, 0.000, 0.000, 0.000, 0.000, 0.000]
pow_z_d = [0.034, 0.140, 0.349, 0.227, 0.167, 0.059, 0.024, 0.000, 0.000, 0.000, 0.000]
res_z_d = [0.900, 0.100, 0.000, 0.000, 0.000, 0.000, 0.000, 0.000, 0.000, 0.000, 0.000]
tra_z_d = [0.950, 0.050, 0.000, 0.000, 0.000, 0.000, 0.000, 0.000, 0.000, 0.000, 0.000]
sec_z_d = [agr_z_d, ind_z_d, pow_z_d, res_z_d, tra_z_d, ]
# 排放源时间分布
agr_t_d=[1.000, 1.000, 1.000, 1.000, 1.000, 1.000, 1.000, 1.000, 1.000, 1.000, 1.000, 1.000, 1.000, 1.000,
       1.000, 1.000, 1.000, 1.000, 1.000, 1.000, 1.000, 1.000, 1.000, 1.000]
ind_t_d=[1.080, 1.632, 1.632, 1.632, 1.632, 1.632, 1.632, 1.632, 1.632, 1.080, 0.936, 0.792, 0.648, 0.504, 
       0.504, 0.504, 0.504, 0.504, 0.504, 0.504, 0.504, 0.648, 0.792, 0.936]
pow_t_d=[1.104, 1.200, 1.212, 1.200, 1.224, 1.236, 1.236, 1.224, 1.176, 1.104, 1.116, 1.128, 1.080, 1.008, 
       0.948, 0.720, 0.840, 0.708, 0.576, 0.600, 0.732, 0.804, 0.852, 0.972]
res_t_d=[1.224, 1.584, 2.736, 2.520, 0.984, 0.696, 0.552, 0.984, 1.680, 2.328, 1.488, 0.840, 0.264, 0.360,
       0.336, 0.240, 0.336, 0.312, 0.408, 0.216, 0.408, 1.080, 1.176, 1.248]
tra_t_d=[1.536, 1.440, 1.392, 1.272, 1.212, 1.368, 1.380, 1.416, 1.428, 1.524, 1.380, 1.128, 1.068, 1.008,
       0.864, 0.648, 0.480, 0.348, 0.252, 0.216, 0.192, 0.312, 0.720, 1.416]
sec_t_d = [agr_t_d, ind_t_d, pow_t_d, res_t_d, tra_t_d, ]

def merge_meic_dept(ent_dir):  # 生成merge文件夹，预处理排放源文件
    if os.path.exists(ent_dir+'/merged/'):
        shutil.rmtree(ent_dir+'/merged/')
    os.makedirs(ent_dir+'/merged/')
    for i, j in zip(['*BC*', '*CO[!2]*', '*CO2*', '*NH3*', '*NOx*', '*[!V]OC*', '*PM2.5*', '*PMcoarse*', '*ALD*',
                    '*CSL*', '*ETH*', '*GLY*', '*HC3*', '*HC5*', '*HC8*', '*HCHO*',
                    '*ISO*', '*KET*', '*MACR*', '*MGLY*', '*MVK*', '*NR*', '*NVOL*',
                    '*OL2*', '*OLI*', '*OLT*', '*ORA1*', '*ORA2*', '*TOL*', '*XYL*', '*SO2*', '*VOC*', ],
                    ['BC', 'CO', 'CO2', 'NH3', 'NOx', 'OC', 'PM2.5', 'PMcoarse', 'ALD',
                    'CSL', 'ETH', 'GLY', 'HC3', 'HC5', 'HC8', 'HCHO',
                    'ISO', 'KET', 'MACR', 'MGLY', 'MVK', 'NR','NVOL',
                    'OL2', 'OLI', 'OLT', 'ORA1', 'ORA2', 'TOL', 'XYL', 'SO2', 'VOC', ]):
        # new:2016_1_agriculture_BC.nc
        # old:2016_01__agriculture__BC.nc
        try:
            fn_act = glob.glob(ent_dir+'/*_agr*_' +j+".nc" )[0]
            fn_idt = glob.glob(ent_dir+'/*_ind*_' +j+".nc" )[0]
            fn_pwr = glob.glob(ent_dir+'/*_pow*_' +j+".nc" )[0]
            fn_rdt = glob.glob(ent_dir+'/*_res*_' +j+".nc" )[0]
            fn_tpt = glob.glob(ent_dir+'/*_tra*_' +j+".nc" )[0]
        except:
            fn_act = glob.glob(ent_dir+"/*_agr*_PM25.nc" )[0]   # 新旧文件一个是pm2.5一个是pm25
            fn_idt = glob.glob(ent_dir+"/*_ind*_PM25.nc" )[0]
            fn_pwr = glob.glob(ent_dir+"/*_pow*_PM25.nc" )[0]
            fn_rdt = glob.glob(ent_dir+"/*_res*_PM25.nc" )[0]
            fn_tpt = glob.glob(ent_dir+"/*_tra*_PM25.nc" )[0]

        f_act = Nio.open_file(fn_act)
        f_idt = Nio.open_file(fn_idt)
        f_pwr = Nio.open_file(fn_pwr)
        f_rdt = Nio.open_file(fn_rdt)
        f_tpt = Nio.open_file(fn_tpt)

        act = f_act.variables['z'][:].reshape((200, 320),)[::-1]
        act = np.where(act > 0.0, act*1, 0.0)
        idt = f_idt.variables['z'][:].reshape((200, 320),)[::-1]
        idt = np.where(idt > 0.0, idt*1, 0.0)
        pwr = f_pwr.variables['z'][:].reshape((200, 320),)[::-1]
        pwr = np.where(pwr > 0.0, pwr*1, 0.0)
        rdt = f_rdt.variables['z'][:].reshape((200, 320),)[::-1]
        rdt = np.where(rdt > 0.0, rdt*1, 0.0)
        tpt = f_tpt.variables['z'][:].reshape((200, 320),)[::-1]
        tpt = np.where(tpt > 0.0, tpt*1, 0.0)

        lon = np.arange(70.125, 150, 0.25, dtype=np.float32)
        lat = np.arange(10.125, 60, 0.25, dtype=np.float32)
        lon, lat = np.meshgrid(lon, lat)

        f =  Nio.open_file(ent_dir+'/merged/'+j+'.nc', 'c')
        f.create_dimension('lon', 320)
        f.create_dimension('lat', 200)
        for var, val in zip(['act', 'idt', 'pwr', 'rdt', 'tpt', 'lon', 'lat'], [act, idt, pwr, rdt, tpt, lon, lat]):
            f.create_variable(var, 'f', ('lat', 'lon',))
            f.variables[var][:] = val
        f.close()

def itp_dis(ent_inp,ent_dir,save_dir):
    f_inp = Nio.open_file(ent_inp, format='nc')
    lon_inp = f_inp.variables['XLONG'][0, :]
    lat_inp = f_inp.variables['XLAT'][0, :]
    time_inp = f_inp.variables['Times'][:][0]
    time_inp = ''.join([i.decode('utf-8') for i in time_inp]).split('_')[0]
    f_inp.close()
    # put all the distributed meic species into meic_spec_emis:
    meic_spec_emis = []
    # inorganic gas: ton/(grid.month) to mole/(km2.h)
    for spec, M in zip(['CO', 'CO2', 'NH3', 'NOx', 'SO2', ], [28, 44, 17, 46, 64]):
        f_post = Nio.open_file(ent_dir+'/merged/'+spec+'.nc')
        lon = f_post.variables['lon'][:]
        lat = f_post.variables['lat'][:]
        section = [(f_post.variables[sec][:, :]*1e6)/(ll_area(lat, 0.25)*30*24*M)
                    for sec in ['act', 'idt', 'pwr', 'rdt', 'tpt', ]]
        f_post.close()
        sections = [meic2wrf(lon_inp, lat_inp, lon, lat, emis,)
                    for emis in section]
        c = [sec2zt(i, j, k) for i, j, k in zip(sections, sec_z_d, sec_t_d)]
        c = sum(c)
        meic_spec_emis.append(c)
    # organic gas: million_mole/(grid.month) to mole/(km2.h)
    for spec in ['ALD', 'CSL', 'ETH', 'GLY', 'HC3', 'HC5', 'HC8', 'HCHO', 'ISO', 'KET', 'MACR', 'MGLY', 'MVK', 'NR', 'NVOL',
                'OL2', 'OLI', 'OLT', 'ORA1', 'ORA2', 'TOL', 'XYL', ]:
        f_post = Nio.open_file(ent_dir+'/merged/'+spec+'.nc')
        section = [(f_post.variables[sec][:, :]*1e6)/(ll_area(lat, 0.25)*30*24)
                    for sec in ['act', 'idt', 'pwr', 'rdt', 'tpt', ]]
        f_post.close()
        sections = [meic2wrf(lon_inp, lat_inp, lon, lat, emis,)
                    for emis in section]
        c = [sec2zt(i, j, k) for i, j, k in zip(sections, sec_z_d, sec_t_d)]
        c = sum(c)
        meic_spec_emis.append(c)
    # aerosol: ton/(grid.month) to ug/(m2.s)
    for spec in ['BC', 'OC', 'PM2.5', 'PMcoarse', ]:
        f_post = Nio.open_file(ent_dir+'/merged/'+spec+'.nc')
        # lon=f_post.variables['lon'][:]
        # lat=f_post.variables['lat'][:]
        section = [(f_post.variables[sec][:, :]*1e6)/(ll_area(lat, 0.25)*30*24*3600)
                    for sec in ['act', 'idt', 'pwr', 'rdt', 'tpt', ]]
        f_post.close()
        sections = [meic2wrf(lon_inp, lat_inp, lon, lat, emis,)
                    for emis in section]
        c = [sec2zt(i, j, k) for i, j, k in zip(sections, sec_z_d, sec_t_d)]
        c = sum(c)
        meic_spec_emis.append(c)

    # meic emission to RADM2 chemistry scheme:

    wrf_spec_emis = [
        np.zeros(meic_spec_emis[0][:].shape, dtype='float32')]*31

    wrf_spec_emis[0] = meic_spec_emis[0]  # wrf: CO
    wrf_spec_emis[1] = meic_spec_emis[2]  # wrf: NH3
    wrf_spec_emis[2] = meic_spec_emis[3]*0.9  # wrf: NO
    wrf_spec_emis[3] = meic_spec_emis[3]*0.1  # wrf: NO2
    wrf_spec_emis[4] = meic_spec_emis[4]*0.9  # wrf: SO2
    wrf_spec_emis[5] = meic_spec_emis[5]  # wrf: ALD
    wrf_spec_emis[6] = meic_spec_emis[6]  # wrf: CSL
    wrf_spec_emis[7] = meic_spec_emis[7]  # wrf: ETH
    wrf_spec_emis[8] = meic_spec_emis[9]  # wrf: HC3
    wrf_spec_emis[9] = meic_spec_emis[10]  # wrf: HC5
    wrf_spec_emis[10] = meic_spec_emis[11]  # wrf: HC8
    wrf_spec_emis[11] = meic_spec_emis[12]  # wrf: HCHO
    wrf_spec_emis[12] = meic_spec_emis[13]  # wrf: ISO
    wrf_spec_emis[13] = meic_spec_emis[14]  # wrf: KET
    wrf_spec_emis[14] = meic_spec_emis[20]*1.1  # wrf: OL2
    wrf_spec_emis[15] = meic_spec_emis[21]*1.1  # wrf: OLI
    wrf_spec_emis[16] = meic_spec_emis[22]*1.1  # wrf: OLT
    wrf_spec_emis[17] = meic_spec_emis[24]  # wrf: ORA2
    wrf_spec_emis[18] = meic_spec_emis[25]*1.1  # wrf: TOL
    wrf_spec_emis[19] = meic_spec_emis[26]*1.1  # wrf: XYL
    wrf_spec_emis[20] = meic_spec_emis[27]*0.2  # wrf: ECi
    wrf_spec_emis[21] = meic_spec_emis[27]*0.8  # wrf: ECj
    wrf_spec_emis[22] = meic_spec_emis[28]*0.2  # wrf: ORGi
    wrf_spec_emis[23] = meic_spec_emis[28]*0.8  # wrf: ORGj
    wrf_spec_emis[24] = meic_spec_emis[29] - \
        meic_spec_emis[28]-meic_spec_emis[27]*0.2  # wrf: PM25i
    wrf_spec_emis[25] = meic_spec_emis[29] - \
        meic_spec_emis[28]-meic_spec_emis[27]*0.8  # wrf: PM25j
    wrf_spec_emis[26] = meic_spec_emis[30]*0.8  # wrf: PM10
    wrf_spec_emis[27] = np.zeros(
        meic_spec_emis[0][:].shape, dtype='float32')  # wrf: SO4i
    wrf_spec_emis[28] = np.zeros(
        meic_spec_emis[0][:].shape, dtype='float32')  # wrf: SO4j
    wrf_spec_emis[29] = np.zeros(
        meic_spec_emis[0][:].shape, dtype='float32')  # wrf: NO3i
    wrf_spec_emis[30] = np.zeros(
        meic_spec_emis[0][:].shape, dtype='float32')  # wrf: NO3j

    #生成00和12两个时次
    for ihour in [0,12]:
        # generate wrfchemi_00z_d01 anthropogenic emission data for wrf-chem model run:
        if os.path.exists(ent_dir+'/merged/'+'wrfchemi_'+str(ihour).zfill(2)+'z_'+ent_inp.split('_')[-1]):
            os.remove(ent_dir+'/merged/'+'wrfchemi_'+str(ihour).zfill(2)+'z_' + ent_inp.split('_')[-1])
        f_chem = Nio.open_file(ent_dir+'/merged/'+'wrfchemi_'+str(ihour).zfill(2)+'z_'+ent_inp.split('_')[-1], 'c', format='nc')
        f_chem.create_dimension('Time', None)
        f_chem.create_dimension('emissions_zdim', wrf_spec_emis[0].shape[1])
        f_chem.create_dimension('south_north', wrf_spec_emis[0].shape[2])
        f_chem.create_dimension('west_east', wrf_spec_emis[0].shape[3])
        f_chem.create_dimension('DateStrLen', 19)

        f_chem.create_variable('Times', 'S1', ('Time', 'DateStrLen'),)
        for i, time in enumerate([time_inp+'_'+str(ii).zfill(2)+':00:00' for ii in range(ihour,ihour+12)]):
            f_chem.variables['Times'][i] = list(time)  # split the string to char
        for ll, LL in zip([lon_inp, lat_inp], ['XLONG', 'XLAT']):
            f_chem.create_variable(LL, 'f', ('south_north', 'west_east',),)
            f_chem.variables[LL][:] = ll

        radm_gas = ['E_CO', 'E_NH3', 'E_NO', 'E_NO2', 'E_SO2', 'E_ALD', 'E_CSL', 'E_ETH', 'E_HC3', 'E_HC5', 'E_HC8', 'E_HCHO', 'E_ISO', 'E_KET',
                    'E_OL2', 'E_OLI', 'E_OLT', 'E_ORA2', 'E_TOL', 'E_XYL', ]
        radm_aerosol = ['E_ECI', 'E_ECJ', 'E_ORGI', 'E_ORGJ', 'E_PM25I',
                        'E_PM25J', 'E_PM_10', 'E_SO4I', 'E_SO4J', 'E_NO3I', 'E_NO3J', ]

        for gas in radm_gas:
            f_chem.create_variable(gas, 'f', ('Time', 'emissions_zdim', 'south_north', 'west_east',))
            f_chem.variables[gas].FieldType = np.int16(104)
            f_chem.variables[gas].MemoryOrder = 'XYZ'
            f_chem.variables[gas].description = 'EMISSIONS'
            f_chem.variables[gas].units = 'mol km^-2 hr^-1'
            f_chem.variables[gas].stagger = 'Z'
            # f_chem.variables[gas].ordinates = 'XLONG XLAT'
        for aerosol in radm_aerosol:
            f_chem.create_variable(aerosol, 'f', ('Time', 'emissions_zdim', 'south_north', 'west_east',))
            f_chem.variables[aerosol].FieldType = np.int16(104)
            f_chem.variables[aerosol].MemoryOrder = 'XYZ'
            f_chem.variables[aerosol].description = 'EMISSIONS'
            f_chem.variables[aerosol].units = 'ug/m3 m/s'
            f_chem.variables[aerosol].stagger = 'Z'
            # f_chem.variables[aerosol].ordinates = 'XLONG XLAT'

        radm_spec = ['E_CO', 'E_NH3', 'E_NO', 'E_NO2', 'E_SO2', 'E_ALD', 'E_CSL', 'E_ETH', 'E_HC3', 'E_HC5', 'E_HC8', 'E_HCHO', 'E_ISO', 'E_KET',
                    'E_OL2', 'E_OLI', 'E_OLT', 'E_ORA2', 'E_TOL', 'E_XYL', 'E_ECI', 'E_ECJ', 'E_ORGI', 'E_ORGJ', 'E_PM25I', 'E_PM25J', 'E_PM_10', 'E_SO4I',
                    'E_SO4J', 'E_NO3I', 'E_NO3J', ]

        for i, spec in enumerate(radm_spec):
            # dimension need to be matched with the variable defination
            #f_chem.variables[spec][:] = wrf_spec_emis[i][ihour:ihour+12, :, :, :]
            chem_spec_input=wrf_spec_emis[i][ihour:ihour+12, :, :, :]
            chem_spec_input_new = chem_spec_input.astype(np.float32)
            f_chem.variables[spec].assign_value(chem_spec_input_new)
        f_chem.close()
        #rename,delete suffix .nc
        if not os.path.exists(save_dir): os.makedirs(save_dir)
        shutil.move(ent_dir+'/merged/'+'wrfchemi_'+str(ihour).zfill(2)+'z_'+ent_inp.split('_')[-1]+'.nc',
                save_dir+'/'+'wrfchemi_'+str(ihour).zfill(2)+'z_'+ent_inp.split('_')[-1])


if __name__ == '__main__':
    ent_dir = "/home/em/桌面/test/201601/"              #请设置为自己的排放源数据所在目录的路径
    ent_inp = "/home/em/桌面/test/meic2wrf/wrfinput_d01"               #请设置为自己的wrfinput文件所在路径
    save_dir = "/home/em/桌面/test/meic2wrf/ssssaaaa"                          #请设置生成的wrfchemi文件保存目录路径
    merge_meic_dept(ent_dir)
    itp_dis(ent_inp,ent_dir,save_dir)
