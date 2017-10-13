#purpose: find the anisotropy PMA vs voltage from directory of text files

from scipy.integrate import quad
import numpy as np 
import matplotlib.pyplot as plt
import os
from scipy import interpolate
from datetime import datetime
from random import randint

def main() :
    in_location ="/home/hanny/Desktop/programs/work/aenergy/txt_files/"
    out_location ="/home/hanny/Desktop/programs/work/aenergy/output"
    #file locations
    os.chdir(in_location)
    files = os.listdir(in_location)
    #what files are in the directory?
    colors_count = 0
    samples = []
    for doc in files:
        sample = prep(doc) #[V,H,R,Y]
        normalized_magnetization(sample) #[V,H,R,Y,M]
        sample.append(sample[1][0]+np.trapz(sample[4],sample[1])) #[V,H,R,Y,M,PMA]
        #finds perpendicular magnetic anisotropy energy by 
        #trapezodial integration of M vs H
        #flipped m and H for less error
        thickness = find_electric_field(sample) #[V,H,R,Y,M,PMA,E]
        h_m_out(sample,doc,in_location,out_location)
        graphs = graph(sample,colors_count)
        colors_count+=1
        samples.append(sample)
    v_e_pma = sort(samples)
    v_e_pma_out(v_e_pma,doc,thickness,in_location,out_location)
    #output data to txt files
    graphs[0].show() #M vs H
    graphs[1].show() #V vs PMA
    raw_input() #press key to destroy graphs


def v_e_pma_out(v_e_pma,doc,thickness,in_location,out_location):
    '''Prints voltage, electric field, and energy to a txt file'''
    os.chdir(out_location)
    #change directory to output location
    out = open(doc[:32]+'_'+'{:0.2f}'.format(thickness)+'nm.txt','a')
    #file name based on input file name and sample thickness to 2 decimals
    out.write("Voltage (mV) Electric Field(mV/nm) PMA Energy\n")
    for line in v_e_pma:
        out.write('{:0.1f}'.format(line[0])+'       '+
                   '{:0.1f}'.format(line[1])+'                '+ 
                   '{:0.1f}'.format(line[2])+'\n') #printed with 1 decimal
    out.close()
    os.chdir(in_location)


def h_m_out(sample,doc,in_location,out_location):
    '''Prints magnetic field and magnetization to txt file for each sample'''
    h,m = sample[1],sample[4]
    os.chdir(out_location)
    out = open(doc[:-4]+'_H_M.txt','w')
    out.write("Magnetic Field (Oe) Normalized Magnetization\n")
    for i in range(len(h)):
        out.write(str(h[i])+'              '+str(m[i])+'\n')
    out.close()
    os.chdir(in_location)


def find_electric_field(sample):
    '''Determine the electic field based on voltage and sample thickness.
    Thickness corresponds to row 1 = 3nm, row 300 = 1nm'''
    row,voltage = sample[3],sample[0]
    thickness = (-2.0/299)*row+(3+2.0/299)
    sample.append(voltage/thickness)
    return thickness


def normalized_magnetization(sample):
    '''Uses the magnetic field and resistence to find the 
    normalized magnetization, returned in an array'''
    h,resistance = sample[1],sample[2]
    rp = resistance[0]
    #resistance when the field and magnetization direction are parallel    
    #occurs at highest point in H

    pos_min = 99999999999
    pos_ind = 0
    neg_min = -99999999999
    neg_ind = 0
    for i in range (0,len(h)):
    #finds negative H value closest to zero and positive closest to zero 
        if (h[i] > 0) :
            if h[i] < pos_min :
                pos_min = h[i]
                pos_ind = i
        else :
            if h[i] > neg_min :
                neg_min = h[i]
                neg_ind = i
    y1 = resistance[pos_ind]
    x1 = h[pos_ind]
    y2 = resistance[neg_ind]
    x2 = h[neg_ind]
    slope = (y2-y1)/(x2-x1)
    r90 = y1 - slope*x1
    #extrapolates the resistance at 0 field
    #resistance when field and magnetization direction are orthogonal 

    #get rid of values during negative field
    #change in sample array, not reference variable h
    resistance = resistance[:neg_ind]
    sample[1] = sample[1][:neg_ind]
    m = [(r90-resistance[i])/resistance[i] * rp/(r90-rp) for i in range(len(resistance))]
    #normalize
    sample.append(m)


def graph(sample,colours_count):
    '''Creates graphs for M vs H and PMA vs V'''
    m,h,v,pma = sample[4],sample[1],sample[0],sample[5]
    colour = colours(colours_count)
    plot1 = plt.figure(1)
    plt.plot(h,m,color=colour,label='{:1.0f}'.format(v)+'mV')
    #remove decimal points
    plt.legend()
    plt.ylabel('M in plane/Ms')
    plt.xlabel('H in plane (Oe)')
    plot2 = plt.figure(2)
    plt.plot(v,pma,marker='o',color=colour)
    #single point
    plt.ylabel('PMA')
    plt.xlabel('Voltage(mV)')
    return (plot1,plot2)


def colours(colours_count):
    '''returns a colour which changes with each function call based on colours_count'''
    colours = ('pink','deeppink','red','darkorange','yellow','lime','green','aquamarine','blue',
              'mediumorchid','purple','saddlebrown','slategray','black')
    try:
        return colours[colours_count]
    except IndexError:
        colours_count = randint(0,len(colours))
        return colours[colours_count]

def prep(doc):
    '''Takes name of input file and returns list of voltage, magnetic 
    field (list), and resistence (list) for each sample'''
    f = open(doc)
    lines = f.readlines()
    #remove label line
    doc_name_str = doc
    doc = doc.split('_')
        
    row = int(doc[4])
    #takes row number of sample from file name
    for i in range(0,len(lines)):
    #remove whitespace & make 2D list 
    #magnetic field, voltage, current, resistance
        lines[i] = lines[i].strip()
        lines[i] = lines[i].replace('\r','')
        lines[i] = lines[i].split('\t')
    try:
        voltage = float(lines[1][4])
    except IndexError:
        voltage = find_real_voltage(doc,doc_name_str,lines)
    
    resistance = [float(lines[i][3]) for i in range(1,len(lines))]
    H = [float(lines[i][0]) for i in range(1,len(lines))]
    #parse voltage (single value), mag field and resistance into lists
    return [voltage,H,resistance,row]


def sort(samples):
    '''Sort collective data from all files'''
    #[V,H,R,Y,M,PMA,E]
    v_e_pma = [[samples[i][0],samples[i][6],samples[i][5]] for i in range(len(samples))]
    v_e_pma = sorted(v_e_pma)
    #sorted [V,E,PMA]
    v = [v_e_pma[i][0] for i in range(len(v_e_pma))]
    pma = [v_e_pma[i][2] for i in range(len(v_e_pma))]
    plt.plot(v,pma,color='black')
    #create connecting line between points in v pma graph 
    return (v_e_pma)


def find_real_voltage(doc,doc_name_str,lines):
    '''If real voltage column does not exist in input column, create one. Return real voltage (excluding contact resistance)'''
    contact_R = float(doc[-3][:-2])
    v = float(lines[1][3])
    R = float(lines[1][3])
    real_v = (R-contact_R)/R*v
    lines[0].append("Real Voltage (mV)")
    lines[1].append(str(real_v))
    new_lines = ["\t".join(line)+"\n" for line in lines]
    new_lines = "".join(new_lines)
    f = open(doc_name_str,'w')
    f.write(new_lines)
    return real_v

main()
