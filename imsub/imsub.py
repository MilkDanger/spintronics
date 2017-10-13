#imsub.py
#purpose: program to subtract images to compare magnetic domains
#get numpy and open cv from pip install numpy/opencv-python

import numpy as np
import cv2
import os

def main() :
    print ("Please specify file location:")
    location = raw_input('>')
    os.chdir(location)
    files = os.listdir(location)
    print(files)
    images = []
    for i in range (0,len(files)) :
        images.append(cv2.imread(files[i]))
    
    print ("What would you like to do?")
    print ("""
    1. Subtract background from data set
    2. Average data set
    3. Compare two images
    """)
    option = raw_input('>')
    
    if (option == "1") :
        bkgrnd(images)
    elif (option == "2" ):
        avg(images)
    elif (option == "3") :
            comp()
    else :
        print ("Invalid. Please try again.")

def avg(images) :
    add = cv2.add(images[0],images[1])
    i = 2
    for i in range (2,len(images)) :
        add = cv2.add(add,images[i])
    avg = add/i
    cv2.imshow('avg image',avg)
    cv2.waitKey(0)
    print ("Do you want to save this image?")
    save = raw_input('>')
    if (save[0] == "y") :
        print ("Image name?")
        name = raw_input('>')
        cv2.imwrite(name,avg)
        print ("Image created.")
    cv2.destroyAllWindows()

def bkgrnd(images) :
#subtract background
    print("Name of background image?")
    name = raw_input('>')
    background = cv2.imread(name)
    for i in range (0, len(images)) :
        newpic = cv2.subtract(images[i],background)
        name =("img" + str(i) + ".jpg")
        cv2.imwrite(name,newpic)
        print ("Image created.")

def comp () :
#compare only two images
    print("Name of first image?")
    name = raw_input('>')
    one = cv2.imread(name)
    print("Name of second image?")
    name = raw_input('>')
    two = cv2.imread(name)
    comp = cv2.subtract(one,two)
    cv2.imshow('image',comp)
    cv2.waitKey(0)
    print ("Do you want to save this image?")
    save = raw_input('>')
    if save[0] == "y" :
        print ("Image name?")
        name = raw_input('>')
        cv2.imwrite(name,comp)
        print ("Image created.")
    cv2.destroyAllWindows()

main()
