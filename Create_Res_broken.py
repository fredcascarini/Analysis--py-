# -*- coding: utf-8 -*-
"""
Created on Fri Oct 28 10:59:27 2016

@author: fc16020
"""

import numpy as np

def create_res(filenamePath):
    
    reaction_lines, reaction_data, reaction_result = [], [], []
    total_counter, p, timeout_counter = 0, 0, 0
    locationsOfReactionLines = []
    x = 0
    failureString = '004'
    
    
    with open(filenamePath,'r') as f:
        
        while True:
            
            reactionLine = False
    
            locationsOfReactionLines.append(f.tell())

            line = f.readline()
            
            if line == '': #end at EOF
                print '.'
                break
                        
            if line == '\n': #ignore blank lines
                print '1'
            
            
            if failureString in line:
                failedPathway = True
            
            if 'LO' in line or 'ALAS' in line:
                total_counter += 1
                print 'x'
            
            if 'ALAS' in line:
                timeout_counter += 1
                print 'y'
            
            if 'LO' in line and failedPathway != True: #004 is the failure pathway
                reactionLine = True
                print 'z'
            
            if 'LO' in line and failedPathway == True:
                failedPathway = False
                print '*'
                
            if reactionLine:
                
                k_current = x-40
                section_end = x+23
                
                f.seek(locationsOfReactionLines[k_current])
                
                
                while True:
                    current_line = f.readline()
                    if 'NEW TRAJECTORY' in current_line:
                        section_start = k_current
                        break
                    else:
                        k_current -= 1
                        f.seek(locationsOfReactionLines[k_current])
                  
                lines = []
                numberOfLinesRead = 0
                
                while numberOfLinesRead <= section_end - section_start:
                    lines += f.readline()
                    numberOfLinesRead += 1
                
                reaction_data.append(" ")
                
                l = 0
                
                while l < section_end:
                    if (lines[l] != '\n' and ( 'Message from'    not in lines[l] 
                                               or 'rotation angles'  in lines[l]
                                               or 'impact parameter' in lines[l]
                                               or 'testReac'         in lines[l])
                        ): #strips blank lines and messages except and[1-3] and bpar
                        if 'scaling' in lines[l]: #strips scaling section
                            l_current = l
                            while True:
                                if 'rotation_angles' in lines[l]:
                                    l = l_current
                                    break
                                l_current += 1
                        else:
                            reaction_data.append(lines[l])
                            l += 1
                    else:
                        l += 1
             
            
            x += 1
        
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
    rr, tc, rc, tc = create_res('propene_cl_big.txt')