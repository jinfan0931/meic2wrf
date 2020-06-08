###############################################  meic2wrf  ########################################################
# Authors:     Fan Jin; Zhou Yong-long; Zhang Lei; Xu Xuan-ye; Jiang Pei-ya; Li Zhuo                              #
# Institution: Chengdu AeriDice Environment Technology Co., Ltd.; Chengdu University of Information & Technology; #
#              Chinese Academy of Meteorological Sciences                                                         #
# E-mail:      jin.fan@outlook.com                                                                                #
# Environment: Python 3.7.7; pynio 1.5.5                                                                          #
###################################################################################################################
# June 8, 2020, added noGUI script (by Hao Lyu)
# Environment added: area(https://github.com/scisco/area)

import Nio
import numpy as np
import os
from int_dis import *
import fnmatch
import shutil

meic2wrf = meic2wrf_interp  #用线性插值替代最邻近插值
ll_area  = ll_area_new      #更高精度计算每块meic网格面积
# 排放源高度分布
agr_z_d = [1.000, 0.000, 0.000, 0.000, 0.000, 0.000, 0.000, 0.000, 0.000, 0.000, 0.000]
ind_z_d = [0.602, 0.346, 0.052, 0.000, 0.000, 0.000, 0.000, 0.000, 0.000, 0.000, 0.000]
pow_z_d = [0.034, 0.140, 0.349, 0.227, 0.167, 0.059, 0.024, 0.000, 0.000, 0.000, 0.000]
res_z_d = [0.900, 0.100, 0.000, 0.000, 0.000, 0.000, 0.000, 0.000, 0.000, 0.000, 0.000]
tra_z_d = [0.950, 0.050, 0.000, 0.000, 0.000, 0.000, 0.000, 0.000, 0.000, 0.000, 0.000]
sec_z_d = [agr_z_d, ind_z_d, pow_z_d, res_z_d, tra_z_d, ]
# 排放源时间分布
agr_t_d = [1.000,  1.000,  1.000,  1.000,  1.000,  1.000,  1.000,  1.000,  1.000,  1.000,  1.000,  1.000,
            1.000,  1.000,  1.000,  1.000,  1.000,  1.000,  1.000,  1.000,  1.000,  1.000,  1.000,  1.000]
ind_t_d = [0.045,  0.068,  0.068,  0.068,  0.068,  0.068,  0.068,  0.068,  0.068,  0.045,  0.039,  0.033,
            0.027,  0.021,  0.021,  0.021,  0.021,  0.021,  0.021,  0.021,  0.021,  0.027,  0.033,  0.039]
pow_t_d = [0.0460, 0.0500, 0.0505, 0.0500, 0.0510, 0.0515, 0.0515, 0.0510, 0.0490, 0.0460, 0.0465, 0.0470,
            0.0450, 0.0420, 0.0395, 0.0300, 0.0350, 0.0295, 0.0240, 0.0250, 0.0305, 0.0335, 0.0355, 0.0405]
res_t_d = [0.051,  0.066,  0.114,  0.105,  0.041,  0.029,  0.023,  0.041,  0.070,  0.097,  0.062,  0.035,
            0.011,  0.015,  0.014,  0.010,  0.014,  0.013,  0.017,  0.009,  0.017,  0.045,  0.049,  0.052]
tra_t_d = [0.0640, 0.0600, 0.0580, 0.0530, 0.0505, 0.0570, 0.0575, 0.0590, 0.0595, 0.0635, 0.0575, 0.0470,
            0.0445, 0.0420, 0.0360, 0.0270, 0.0200, 0.0145, 0.0105, 0.0090, 0.0080, 0.0130, 0.0300, 0.0590]
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
        fn_act = ent_dir+'/' + \
            fnmatch.filter(fnmatch.filter(
                os.listdir(ent_dir), i), '*agr*nc')[0]
        fn_idt = ent_dir+'/' + \
            fnmatch.filter(fnmatch.filter(
                os.listdir(ent_dir), i), '*ind*nc')[0]
        fn_pwr = ent_dir+'/' + \
            fnmatch.filter(fnmatch.filter(
                os.listdir(ent_dir), i), '*pow*nc')[0]
        fn_rdt = ent_dir+'/' + \
            fnmatch.filter(fnmatch.filter(
                os.listdir(ent_dir), i), '*res*nc')[0]
        fn_tpt = ent_dir+'/' + \
            fnmatch.filter(fnmatch.filter(
                os.listdir(ent_dir), i), '*tra*nc')[0]

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
        section = [(f_post.variables[sec][:, :]*10e6)/(ll_area(lat, 0.25)*30*24*M)
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
        section = [(f_post.variables[sec][:, :]*10e6)/(ll_area(lat, 0.25)*30*24)
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
        section = [(f_post.variables[sec][:, :]*10e6)/(ll_area(lat, 0.25)*30*24*3600)
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
    ent_dir = "/data_1/meic2wrf/radm2/"                     #排放源文件路径
    ent_inp = "/data_1/meic2wrf/wrfinput_d01"               #wrfinput文件路径
    save_dir = "/data_1/meic2wrf/save/"                     #wrfchemi文件保存路径
    for i in range(1,13):
        merge_meic_dept(ent_dir+"2016"+str(i).zfill(2)+"/")
        itp_dis(ent_inp,ent_dir+"2016"+str(i).zfill(2)+"/",save_dir+"/2016"+str(i).zfill(2)+"/")
