# -*- coding: utf-8 -*-
"""
Created on Mon Sep 26 09:16:30 2016

@author: fc16020
"""

from log_file_crop import log_file_crop as lfc
#from log_file_crop import plot_figure_array as pfa
#import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import time
import scipy.special as spc
import os

def analyse_file(filename = 'propene_cl_all.txt',refresh=False,printTime = False, isDir = False, dirname = ""):
    if (not isDir):
        runtype = filename.split("\\")[-1].split("_",1)[0].lower()
        lfc_counters = lfc(filename,runtype,refresh,isDir,dirname)
        pd_data, pd_data_arr, pd_counter_array = analyse_file_singular(filename,runtype,refresh,printTime, lfc_counters)
    else:
        firstRun = True
        for dirpath,subdirs,filenames in os.walk(dirname):
            for f in filenames:
                if (f.endswith("txt") or f.endswith("log")):
                    runtype = f.split("\\")[-1].split("_",1)[0].lower()
                    fileWithPath = os.path.join(dirpath,f)
                    lfc_counters = lfc(f,runtype,refresh, dirpath = dirpath)
                    pdd_crr, pdda_crr, pdca_crr = analyse_file_singular(fileWithPath,runtype,refresh,printTime, lfc_counters, dirpath)
                    if firstRun:
                        pd_data = pdd_crr
                        pd_data_arr = pdda_crr
                        pd_counter_array = pdca_crr
                        firstRun = False
                    else:
                        pd_data = pd_data.append(pdd_crr, ignore_index=True)
                        pd_data_arr = pd_data_arr.append(pdda_crr, ignore_index=True)
                        pd_counter_array = pd_counter_array.add(pdca_crr)
                      
    return pd_data, pd_data_arr, pd_counter_array

def analyse_file_singular(filename,runtype, refresh, print_time, lfc_counters, dirpath = ''):
    
    #Function overview:
    #   -creates cropped log file (if not already done) via LFC
    #   -populates Data_Arr (np array) from cropped log file
    #   -analyses Data_Arr data, producing Data (np array)
    
    #Inputs:
    #   -refresh:    boolean, whether to redo the cropping of the log file
    #   -print_time: boolean, whether to time the function
    #   -runtype:    string,  which type of run (currently accepts 'propene' or 'pentane')

    #Outputs:
    #   -data:              Pandas DataFrame of analysed data
    #   -data_arr:          Pandas DataFrame of raw data
    #   -pd_counter_array:  Pandas DataFrame of types of trajectory numbers 
    
    #timer - begin timing
    if print_time == True:
        start = time.time()
        
    
    
    #define parameters based on runtype
    if runtype == 'pentane':
        print 'Using RunType Pentane'
        mass_frag_1 = 71.0              #C5H11 mass
        mass_frag_2 = 36.5              #HCl Mass
    elif runtype == 'propene':
        print 'Using RunType Propene'
        mass_frag_1 = 41.0              #C3H5 mass
        mass_frag_2 = 36.5              #HCl mass 
    else:
        print 'Undefined RunType: ' + runtype
        raise SystemExit('RunType Error')             
        
    #Run function to crop log file
    total_counter = lfc_counters.total
    reaction_counter = lfc_counters.reactive
    success_counter = lfc_counters.successful
    timeout_counter = lfc_counters.timeout
    csvPath = os.path.join(dirpath, runtype)
    pd_data_arr = pd.read_csv(csvPath + '.csv')
    pd_data_arr.drop(pd_data_arr.columns[[0]],axis=1,inplace=True)
    pd_data_arr
    c, h, B = 3e8,  6.626e-34, 310.021851e9
    u = 1.6605e-27
    fun_freq = c * 290372
    
    max_hcl_freq = pd_data_arr.EVIB2.max()
    max_hcl_erot = pd_data_arr.EROT2.max()
    hcl_freq_arr = [0] #initialised to zero to allow amax to be successful
    hcl_erot_arr = [0] #ditto
    v, j = 0, 0
    
    #populate arrays of energy levels for the vibrational and rotational
    # states of the HCl product
    
    while hcl_freq_arr[-1] < max_hcl_freq:
        freq_curr = (v+0.5)*h*fun_freq # calculates in J
        hcl_freq_arr.append((freq_curr/1000)*6.022e23) #convert J to kJ/mol
        v+=1
    del hcl_freq_arr[0]
    
    while np.amax(np.array(hcl_erot_arr)) < max_hcl_erot:
        erot_curr = B * h * j * (j + 1)
        hcl_erot_arr.append((erot_curr/1000)*6.022e23) #convert J to kJ/mol
        j += 1
    del hcl_erot_arr[0]
    
    freq_current_storage = []

    data_points = len(pd_data_arr) #N is not needed
    data = np.zeros((data_points,8))
    #take values from data_arr, process them and then save them to data
    print 'Analysing Data'
    for index in range(0,data_points):
        erot_current = pd_data_arr.EROT2.iloc[index]
        freq_current = pd_data_arr.EVIB2.iloc[index]
        vel_frag_1 = np.array([pd_data_arr.PCX1.iloc[index],pd_data_arr.PCY1.iloc[index],pd_data_arr.PCZ1.iloc[index]]) / (mass_frag_1 * u)
        vel_frag_2 = np.array([pd_data_arr.PCX2.iloc[index],pd_data_arr.PCY2.iloc[index],pd_data_arr.PCZ2.iloc[index]]) / (mass_frag_2 * u)
        rel_vel = vel_frag_1 - vel_frag_2
        vel_mag = np.sqrt(np.dot(rel_vel, rel_vel))
        cos_theta = rel_vel[2] / vel_mag
        for i in range (0,len(hcl_erot_arr)): #column 0 = rotational energy state
            i_lower = i - 1
            if i == len(hcl_erot_arr) - 1 : #upper boundary condition
                if erot_current > (hcl_erot_arr[i - 1]+hcl_erot_arr[i])/2:
                    data[index,0] = i
            elif i_lower < 0: #lower boundary condition
                if erot_current < (hcl_erot_arr[i + 1]+hcl_erot_arr[i])/2: 
                    data[index,0] = i
            elif i != len(hcl_erot_arr) -1 and i_lower >= 0:
                if erot_current > (hcl_erot_arr[i]+hcl_erot_arr[i_lower])/2 and erot_current < (hcl_erot_arr[i + 1]+hcl_erot_arr[i])/2 : 
                    data[index,0] = i
        for i in range (0,len(hcl_freq_arr)): #column 1 = vibrational energy state
            i_lower = i - 1
            if i == len(hcl_freq_arr) - 1 : #upper boundary condition
                if freq_current > (hcl_freq_arr[i - 1]+hcl_freq_arr[i])/2:
                    data[index,1] = i
            elif i_lower < 0: #lower boundary condition
                if freq_current < (hcl_freq_arr[i + 1]+hcl_freq_arr[i])/2: 
                    data[index,1] = i
            elif i != len(hcl_freq_arr) -1 and i_lower >= 0:
                if freq_current > (hcl_freq_arr[i]+hcl_freq_arr[i_lower])/2 and freq_current < (hcl_freq_arr[i + 1]+hcl_freq_arr[i])/2 : 
                    data[index,1] = i
            #freq_current_storage.append(freq_current)
        data[index,2] = pd_data_arr.TIME.iloc[index] #time
        data[index,3] = pd_data_arr.BPAR.iloc[index] #bpar
        data[index,4] = pd_data_arr.ANG1.iloc[index] #ang1
        data[index,5] = pd_data_arr.ANG2.iloc[index] #ang2
        data[index,6] = pd_data_arr.ANG3.iloc[index] #ang3
        data[index,7] = cos_theta
    
    print 'Finalising Data Arrays'
    pd_data = pd.DataFrame(data, columns=('NROT','NVIB','TIME','BPAR','ANG1','ANG2','ANG3','CSTH'))
        
    counter_array = [float(total_counter),float(reaction_counter),float(success_counter),float(timeout_counter)]
    
    pd_counter_array = pd.DataFrame(counter_array).transpose()
    pd_counter_array.columns=('TotalTrajs','ReactiveTrajs','SuccessfulTrajs','Timeouts')
    
    pd.DataFrame(freq_current_storage).to_csv("pdfcs.csv")

    #timer - end timing
    if print_time == True:
        end = time.time()
        print (end-start)
    return pd_data, pd_data_arr, pd_counter_array

def generate_pd_arr(pd_data, success_counter, time_min = -1, time_max = -1, interval_power_of_half = 1):

    #Function overview:
    #   -creates pandas (PD) DataFrames (DF) for time, NROT and NVIB bins
    #   -populates these bins by number of trajectories in each state
    
    #Inputs:
    #   -pd_data:           PD DF of analysed data
    #   -success_counter:   number of reactive trajectories that passed ZPE check
    #   -time_restriction:  only consider times >= this value, < 0 results in no cropping
    
    #Outputs:
    #   -pd_counter_array_nvib: PD DF of NVIB bins
    #   -pd_counter_array_nrot: PD DF of NROT bins
    #   -pd_time_bin_arr:       PD DF of TIME bins
    
    #applies time restriction cropping
    if time_min >=0:
        pd_data = pd_data[pd_data.TIME >= time_min]
    if time_max >= 0:
        pd_data = pd_data[pd_data.TIME <= time_max]
    print len(pd_data)
    #find max NVIB
    pd_arr_sort_nvib = (pd_data.sort_values(by='NVIB'))
    max_val_nvib = int(pd_arr_sort_nvib.NVIB.iloc[-1])
    
    #create and populate NVIB bins array
    counter_array_nvib = np.zeros(max_val_nvib+1)    
    for __i in range(0,max_val_nvib+1):
        counter_array_nvib[__i] = len(pd_arr_sort_nvib[pd_arr_sort_nvib.NVIB == __i])/success_counter
    pd_counter_array_nvib = pd.DataFrame(counter_array_nvib, columns=['Bins'])

    #find max NROT
    pd_arr_sort_nrot = (pd_data.sort_values(by='NROT'))
    max_val_nrot = int(pd_arr_sort_nrot.NROT.iloc[-1])
    
    #create and populate NROT bins 
    counter_array_nrot = np.zeros(max_val_nrot+1)
    for __j in range(0,max_val_nrot+1):
        counter_array_nrot[__j] = len(pd_arr_sort_nrot[pd_arr_sort_nrot.NROT == __j])/success_counter
    pd_counter_array_nrot = pd.DataFrame(counter_array_nrot, columns=['Bins'])  
    
 
    #For time bins, round to the nearest 2^-n where
    n = interval_power_of_half
    
    #Create constant to multiply numbers by, so that rounding results in the right bins when divided by this number
    #e.g. for n=1 (round to the nearest half):
    #multiplier = 2
    # 12.43 becomes 24.86 round to 25 then halve to 12.5, which is 12.43 to the nearest 0.5
    multiplier = 2**n
    max_time = int(pd_data.sort_values(by='TIME').TIME.iloc[-1]) + multiplier
    

    #creates and populates TIME bins
    time_bin_arr = np.zeros(max_time*multiplier)
    for k in range(0,len(pd_data)):
        value = round(pd_data.TIME.iloc[k]*multiplier)
        time_bin_arr[int(value)] += 1
    time_bin_arr /= len(pd_data) * np.ones_like(time_bin_arr)
    pd_time_bin_arr = pd.DataFrame(time_bin_arr, columns = ['Bins'])
    
    return pd_counter_array_nvib, pd_counter_array_nrot, pd_time_bin_arr

def generate_dcs(pd_data, J_select = -1, v_select = -1, order_max = 6, delta_angle = 0.5):
    
    #Function overview:
    #   -calculates the Differential Cross Section of the reaction using a Lagrange expansion
    
    #Inputs:
    #   -pd_data:       PD DF of analysed data
    #   -J_select:      only consider trajectories resulting in rotational constants = this value ( <0 results in no cropping)
    #   -v_select:      only consider trajectories resulting in vibrational constants = this value ( <0 results in no cropping)
    #   -order_max:     lagrange polynomial order to go up to
    #   delta_angle:    increment in angle to use    
    
    #Outputs:
    #   -pd_DCS:        PD DF of ANGLE and DCS  
    
    #Crops input data by selecting specific J or v values
    if J_select >= 0 or v_select >= 0:
        if J_select != -1:
            pd_data = pd_data[pd_data.NROT == J_select]
        if v_select != -1:
            pd_data = pd_data[pd_data.NVIB == v_select]

    DCS = np.zeros(int(180.0/delta_angle) + 1)
    n_traj_sel = len(pd_data) #number of trajectories being considered
    coeff = np.zeros(order_max + 1)

    #calculates coefficients to use in the lagrange expansion
    for i in range(0,len(pd_data)):
        c_theta = pd_data.CSTH.iloc[i]
        for L in range(0,order_max + 1):
            coeff[L] += spc.lpmv(0,L,c_theta)   
    
    #divides each coefficient by the number of trajectories
    coeff /= (n_traj_sel* np.ones_like(coeff))
    
    #normalises the coefficients
    for L in range(0,order_max + 1):
        coeff[L] /= (2.0/((2*L)+1))
    
    pd.DataFrame(coeff).to_csv('coeffs.csv')

    #calculates the DCS for each angle using the above coefficients
    for angle in np.arange(180,0-delta_angle, -delta_angle):
        cos_angle = np.cos((angle*np.pi/180.0))
        for L in range(0,order_max + 1):
            DCS[int(angle/delta_angle)] += coeff[L] * spc.lpmv(0,L,cos_angle)  
    
    #pairs the output numpy array with the angles and converts to PD DF
    DCS = np.vstack((np.arange(180,0-delta_angle, -delta_angle),DCS))
    pd_DCS = pd.DataFrame(DCS).transpose()
    pd_DCS.columns=('ANGLE','DCS')
            
    return pd_DCS
  
 
def dcs_cos_hist (pd_data_CSTH, bins = 180):
    
    #Function overview:
    #   -calculates an approximation to the DCS using the cosine of the relative velocity vector
    
    #Inputs:
    #   -pd_data_CSTH:  PD DF of analysed data, passed as CSTH only (i.e. pd_data.CSTH)
    #   -bins:          number of bins to use across the DCS   
    
    #Outputs:
    #   -bins_array:    numpy array of the DCS approximation for each angle
    
    bins_array = np.zeros(bins+1)
    for i in pd_data_CSTH:
        bins_array[int(round(np.arccos(i)/np.pi * bins,0))] += 1/np.sin(np.arccos(i))
    
    pd_bins_array = pd.DataFrame(bins_array,columns=['Bins'])    
        
    return pd_bins_array


    
if __name__ == '__main__':
    print 'Creating Arrays of Data'
    pd_data, pd_data_arr, pd_counter_array = analyse_file(filename = 'propene_cl.log', isDir=True, dirname = os.path.normpath("C:/Users/fc16020/OneDrive - University of Bristol/Runs/HE"))
    print 'Finished Creating Arrays'
    print 'Creating Counter Arrays'
    pd_counter_array_nvib, pd_counter_array_nrot, pd_time_bin_arr = generate_pd_arr(pd_data, pd_counter_array.SuccessfulTrajs)
    pd_counter_array_nvib_long, pd_counter_array_nrot_long, pd_time_bin_arr_long = generate_pd_arr(pd_data, pd_counter_array.SuccessfulTrajs, time_min = 1)
    pd_counter_array_nvib_crop, pd_counter_array_nrot_crop, pd_time_bin_arr_crop = generate_pd_arr(pd_data, pd_counter_array.SuccessfulTrajs, time_min=1, time_max = 5, interval_power_of_half = 3)
    print 'Finished Creating Counter Arrays'
    print 'Generating DCS'
    pd_DCS = generate_dcs(pd_data, v_select=0, J_select=2)
    bins_array = dcs_cos_hist(pd_data.CSTH)
    print 'Finished Generating DCS'
    
    
#plt.plot(hcl_erot_list,'o')
#plt.plot(data[:,0], data[:,1], 'o')
#pfa(data_arr)