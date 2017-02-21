# -*- coding: utf-8 -*-
"""
Created on Fri Oct 28 10:59:27 2016

@author: fc16020
"""

def create_res(filename):
    
    f = open(filename,'r') 
    lines = f.readlines()
    f.close
    
    reaction_lines, reaction_data, reaction_result = [], [], []
    total_counter, p, timeout_counter = 0, 0, 0
    
    for i,line in enumerate(lines):                  #find successes 
        if 'LO' in line or 'ALAS' in line:
            total_counter += 1
        if 'ALAS' in line:
            timeout_counter += 1
        if 'LO' in line and '004' not in lines[i-2]: #004 is the failure pathway
            reaction_lines.append(i)
            
    for ix,k in enumerate(reaction_lines):        #create array of text of successful runs
        k_current = k - 40   
        while True:
            if 'NEW TRAJECTORY' in lines[k_current]:
                section_start = k_current
                break
            else:
                k_current -= 1
        section_end = k+23
        reaction_data.append(" ")
        l = section_start
        while l < section_end:   
            if (lines[l] != '\n' and 
                                     (     'Message from'  not in lines[l] 
                                        or 'rotation angles'   in lines[l] 
                                        or 'impact parameter'  in lines[l]
                                        or 'testReac'          in lines[l])
                ): #strips blank lines and messages except ang[1-3] and bpar
                if 'scaling' in lines[l]: #strips scaling section
                    l_current = l
                    while True:
                        if 'rotation angles' in lines[l_current]:
                            l = l_current
                            break
                        l_current += 1
                else:
                    reaction_data.append(lines[l])
                    l += 1
            else:
                l += 1
              
    while p < len(reaction_data):
        if 'INIT' in reaction_data[p]:
            while True:
                if 'LO' in reaction_data[p]:
                    p -= 2
                    break
                else:
                    p += 1
        else:
            reaction_result.append(reaction_data[p])
            p += 1
    
    return reaction_result, total_counter, len(reaction_lines), timeout_counter


if __name__ == '__main__':
    rr, tc, rc, tc = create_res('propene_cl_all.txt')