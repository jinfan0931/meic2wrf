###############################################  meic2wrf  ########################################################
# Authors:     Fan Jin; Zhou Yong-long; Zhang Lei; Xu Xuan-ye; Jiang Pei-ya; Li Zhuo                              #
# Institution: Chengdu AeriDice Environment Technology Co., Ltd.; Chengdu University of Information & Technology; #
#              Chinese Academy of Meteorological Sciences                                                         #
# E-mail:      jin.fan@outlook.com                                                                                #
# Environment: Python 3.7.7; pynio 1.5.5                                                                          #
###################################################################################################################

######################################
#     1. area of lat_lon grids       #
######################################
import numpy as np

def ll_area(lat,res):
    Re=6371.392
    X=Re*np.cos(lat*(np.pi/180))*(np.pi/180)*res
    Y=Re*(np.pi/180)*res
    return X*Y

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

###########################################
#  3. vertical & time distribution func.  #
###########################################

def sec2zt(sec,zfac,tfac):
    c=[sec*i*j for i in tfac for j in zfac]
    d=[np.array(c[i:i+len(zfac)]) for i in np.arange(0,len(c),len(zfac))]
    return np.array(d)

###################################