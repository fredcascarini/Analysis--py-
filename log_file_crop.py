# -*- coding: utf-8 -*-
"""
Created on Fri Sep 23 14:10:07 2016

@author: fc16020
"""

import numpy as np
import matplotlib.pyplot as plt
import os.path
import pandas as pd
from Create_Res import create_res as CR

def log_file_crop(filename,runtype, refresh = False, isdirectory = False, dirpath = ""):
    rtn_cnt = pd.DataFrame(np.array([0,0,0,0]).reshape(1,4), columns = ['total','reactive','successful','timeout'], index = ['Counter'])
    print 'Cropping File ' + os.path.join(dirpath,filename)
    rtn_cnt.total, rtn_cnt.reactive, rtn_cnt.successful, rtn_cnt.timeout = log_file_crop_singular(filename,runtype,dirpath = dirpath, refresh=refresh)
    return rtn_cnt
                    
def log_file_crop_singular(filename, runtype, dirpath = "", refresh = False): 
    
    runtypePath = os.path.join(dirpath,runtype)
    filenamePath = os.path.join(dirpath,filename)
    
    if os.path.isfile(runtypePath + '.csv') and refresh == False: #shortcut if it's been run before
        print 'Skipping file cropping'
        counter_array = pd.read_csv(runtypePath + '_counters.csv')
        total_counter, reaction_counter, success_counter, timeout_counter = counter_array.Total_Counter,counter_array.Reaction_Counter,counter_array.Success_Counter,counter_array.Timeout_Counter
        return float(total_counter), float(reaction_counter),float(success_counter), float(timeout_counter)
                 
    else:
        lines, total_counter, reaction_counter, timeout_counter = CR(filenamePath)
        lo_lines = []  
        p, data_iterator, success_counter = 0 , 0 , 0
        
        while p < len(lines):
            if 'LO' in lines[p]:
                lo_lines.append(p)
            p += 1
        
        data_arr = np.zeros((len(lo_lines),25))
        
        
        for lo in lo_lines:
            #...define ZPE for each pentane-based product, if applicable...
            if runtype == 'pentane':
                trajectory = int(lines[lo-2][54:57])
                if trajectory in range(1,4) or trajectory in range(10,13):
                    ZPE = 383.82
                elif trajectory in range(4,6) or trajectory in range(8,10):
                    ZPE = 387.78
                elif trajectory in range(6,8):
                    ZPE = 388.7382
                else:
                    print 'Undefined Trajectory: ' + trajectory
                    raise SystemError()
            elif runtype == 'propene':
                ZPE = 172.84
            elif runtype != 'propene' and runtype != 'pentane':
                print 'Undefined RunType: ' + runtype
                raise SystemError()
                #...and populate data_arr from lines array
            if float(lines[lo+6][116:124]) >= ZPE and float(lines[lo+9][116:124]) >= 17.95: #ZPE check           
                data_arr[data_iterator][ 0] = lines[lo    ][-10: -1] #Time
                data_arr[data_iterator][ 1] = lines[lo + 5][ 16    ] #Product 1 number
                data_arr[data_iterator][ 2] = lines[lo + 6][  9: 15] #Etot(1)
                data_arr[data_iterator][ 3] = lines[lo + 6][ 31: 38] #Epot(1)      
                data_arr[data_iterator][ 4] = lines[lo + 6][ 51: 59] #Ekin(1)
                data_arr[data_iterator][ 5] = lines[lo + 6][ 76: 83] #Etra(1)
                data_arr[data_iterator][ 6] = lines[lo + 6][ 96:103] #Erot(1)
                data_arr[data_iterator][ 7] = lines[lo + 6][116:124] #Evib(1)
                data_arr[data_iterator][ 8] = lines[lo + 8][ 16    ] #Product 2 number
                data_arr[data_iterator][ 9] = lines[lo + 9][  9: 15] #Etot(2)       
                data_arr[data_iterator][10] = lines[lo + 9][ 31: 38] #Epot(2)      
                data_arr[data_iterator][11] = lines[lo + 9][ 51: 59] #Ekin(2)
                data_arr[data_iterator][12] = lines[lo + 9][ 76: 83] #Etra(2)       
                data_arr[data_iterator][13] = lines[lo + 9][ 96:103] #Erot(2)
                data_arr[data_iterator][14] = lines[lo + 9][116:124] #Evib(2)
                data_arr[data_iterator][15] = lines[lo - 4][ 44: 52] #ANG1
                data_arr[data_iterator][16] = lines[lo - 4][ 58: 67] #ANG2
                data_arr[data_iterator][17] = lines[lo - 4][ 72: 80] #ANG3
                data_arr[data_iterator][18] = lines[lo - 3][ 47: 53] #BPAR
                data_arr[data_iterator][19] = lines[lo + 7][ 54: 67] #PCOM X (1)
                data_arr[data_iterator][20] = lines[lo + 7][ 68: 80] #PCOM Y (1)
                data_arr[data_iterator][21] = lines[lo + 7][ 82: 95] #PCOM Z (1)
                data_arr[data_iterator][22] = lines[lo + 10][ 54: 67] #PCOM X (2)
                data_arr[data_iterator][23] = lines[lo + 10][ 68: 80] #PCOM Y (2)
                data_arr[data_iterator][24] = lines[lo + 10][ 82: 95] #PCOM Z (2)
                success_counter += 1   
                data_iterator += 1        
    
        #delete blank rows
        for i in range (len(lo_lines),data_iterator,-1):
            data_arr = np.delete(data_arr,i-1,axis=0)
            
        pd_data_arr = pd.DataFrame(data_arr,columns=('TIME','PROD1','ETOT1','EPOT1','EKIN1','ETRA1','EROT1','EVIB1','PROD2','ETOT2','EPOT2','EKIN2','ETRA2','EROT2','EVIB2','ANG1','ANG2','ANG3','BPAR','PCX1','PCY1','PCZ1','PCX2','PCY2','PCZ2'))
        counter_arr = np.array([total_counter,reaction_counter,success_counter,timeout_counter])
        pd_counter_arr = pd.DataFrame(counter_arr).transpose()
        pd_counter_arr.columns=['Total_Counter','Reaction_Counter','Success_Counter','Timeout_Counter']
        pd_data_arr.to_csv(runtypePath + '.csv')
        pd_counter_arr.to_csv(runtypePath + '_counters.csv')
        
        return total_counter, reaction_counter, success_counter, timeout_counter
    
def plot_figure_array(data_arr):
    plt.figure(1)
    plt.subplot(2,6,1)
    plt.plot(data_arr[:,0],data_arr[:,2],'o')
    plt.subplot(2,6,2)
    plt.plot(data_arr[:,0],data_arr[:,3],'o')
    plt.subplot(2,6,3)
    plt.plot(data_arr[:,0],data_arr[:,4],'o')
    plt.subplot(2,6,4)
    plt.plot(data_arr[:,0],data_arr[:,5],'o')
    plt.subplot(2,6,5)
    plt.plot(data_arr[:,0],data_arr[:,6],'o')
    plt.subplot(2,6,6)
    plt.plot(data_arr[:,0],data_arr[:,7],'o')
    plt.subplot(2,6,7)
    plt.plot(data_arr[:,0],data_arr[:,9],'o')
    plt.subplot(2,6,8)
    plt.plot(data_arr[:,0],data_arr[:,10],'o')
    plt.subplot(2,6,9)
    plt.plot(data_arr[:,0],data_arr[:,11],'o')
    plt.subplot(2,6,10)
    plt.plot(data_arr[:,0],data_arr[:,12],'o')
    plt.subplot(2,6,11)
    plt.plot(data_arr[:,0],data_arr[:,13],'o')
    plt.subplot(2,6,12)
    plt.plot(data_arr[:,0],data_arr[:,14],'o')
    
if __name__ == '__main__':
    total_counter, reaction_counter, success_counter, timeout_counter  = log_file_crop(filename = 'propene_cl_big.txt', runtype= 'propene')
