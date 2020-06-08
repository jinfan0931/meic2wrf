###############################################  meic2wrf  ########################################################
# Authors:     Fan Jin; Zhou Yong-long; Zhang Lei; Xu Xuan-ye; Jiang Pei-ya; Li Zhuo                              #
# Institution: Chengdu AeriDice Environment Technology Co., Ltd.; Chengdu University of Information & Technology; #
#              Chinese Academy of Meteorological Sciences                                                         #
# E-mail:      jin.fan@outlook.com                                                                                #
# Environment: Python 3.7.7; pynio 1.5.5                                                                          #
###################################################################################################################
# June 8, 2020, added ll_area_new(more accurent meic grid area), meic2wrf_interp(linear interpolation instead of 
#               nearest)   (by Hao Lyu) 

######################################
#     1. area of lat_lon grids       #
######################################
import numpy as np

def ll_area(lat,res):  #input : lat : np.array((200, 320))
    Re=6371.392
    X=Re*np.cos(lat*(np.pi/180))*(np.pi/180)*res  #np.array((200, 320))
    Y=Re*(np.pi/180)*res  #float
    return X*Y

def ll_area_new(lat,res):
    from area import area
    startlon=0
    return_area = np.zeros_like(lat)
    isize,jsize = return_area.shape
    for i in range(isize):
        for j in range(jsize):
            obj = {'type':'Polygon','coordinates':[[[startlon,lat[i,j]-0.125],[startlon,lat[i,j]+0.125],[startlon+0.25,lat[i,j]+0.125],[startlon+0.25,lat[i,j]-0.125]]]}
            return_area[i,j] = area(obj)/1000.0/1000.0
    return return_area
###################################
#    2. 2D interpolation func.    #
#       ----dx----|--cdx---       #
#       --------1----------       #
###################################

def meic2wrf(lon_inp,lat_inp,lon,lat,emis,):#lon/lat_inp: model; lon/lat: meic; emis: meic emis
    
    #coordinations of meic grids origin
    ox=lat[0,0]
    oy=lon[0,0]
    
    def inp(ix, iy, dx, dy, cdx, cdy): #put small function under meic2wrf function, or variables in small functions are global.
        #area_ratio
        return emis[ix,iy]*cdx*cdy+emis[ix,iy+1]*cdx*dy+emis[ix+1,iy+1]*dx*dy+emis[ix+1,iy]*dx*cdy
        
    def std_p(p,o): #standardize point p
        p = (p-o)*4
        dp = p - int(p)
        cdp = 1 - dp
        ip = int(p) #get index of the nearest big grid relates to the p point
        return dp, cdp, ip

    def inp_p(px, py):
        dx, cdx, ix = std_p(px,ox)
        dy, cdy, iy = std_p(py,oy)
        return inp(ix, iy, dx, dy, cdx, cdy)

    emis_inp=np.zeros(lon_inp.shape, dtype='float32')
    y_cnt =0
    for (row_lat, row_lon) in zip(lat_inp, lon_inp): #2D meic coordinates to 1D
        x_cnt=0
        for (pnt_lat, pnt_lon) in zip(row_lat, row_lon): #1D to point
            emis_inp[y_cnt,x_cnt] = inp_p(pnt_lat, pnt_lon) #assign meic emission
            x_cnt += 1
        y_cnt +=1
    return emis_inp

def meic2wrf_interp(lon_inp,lat_inp,lon,lat,emis,interp_method = 'bilinear'):#lon/lat_inp: model; lon/lat: meic; emis: meic emis
    import xesmf as xe
    grid_out = {'lon': lon_inp,'lat': lat_inp}
    grid_in = {'lon': lon,'lat': lat}    
    regridder = xe.Regridder(grid_in, grid_out, interp_method,reuse_weights=True)
    emis_inp = regridder(emis)
    return emis_inp
###########################################
#  3. vertical & time distribution func.  #
###########################################

def sec2zt(sec,zfac,tfac):
    c=[sec*i*j for i in tfac for j in zfac]
    d=[np.array(c[i:i+len(zfac)]) for i in np.arange(0,len(c),len(zfac))]
    return np.array(d)

###################################