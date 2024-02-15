# -*- coding: utf-8 -*-
"""
Created on Thu Feb  1 11:06:44 2024

@author: 6000045970000731
"""

#New imports
import matplotlib.patches as patches

#Below taken from already implemented script for comparison of Siemens output with radiologists

#Import libraries and dependencies
import os
import pydicom as dicom
import numpy as np
import time
import matplotlib.pyplot as plt
from joblib import Parallel, delayed
from tqdm import tqdm
import sys # Save terminal output to txt file

start=time.time() #To count time to run all steps

#Input and Output paths
data_path= "H:\My Desktop/all_normal_overweight/" #Folders with scans

output_path="H:/My Desktop/bmi_normal_overweight_noise_many_3d/" #Any name

if not os.path.exists(output_path): #Create folder to save images
    os.mkdir(output_path)
    
#Create lists of input and output paths to use with Parallel processing library    
inputs=[]
outputs=[]

#Loop over all patient folders and add paths to input and output lists
for path,subdir,files in os.walk(data_path): #each time gets into next subdir and repeats
#path,subdir,files for a specific directory each time
    result_path='' #Initialize string to be filled with directory name
    if len(files)>0:
        result_path=output_path+path.split('/')[-1] #Path of specific patient        
        outputs.append(result_path)
        inputs.append(path)


def CT_files_extract(input_path):
    'Extracts all CT files (AI, original scans along with annotated CT images), the num of AI nodules,'
    'as well as the total slices in the SEG files, in AI output, and the total num of CT files (original scan).'
    'We also get possible errors. It is assumed that the input path contains only DICOM files of a specific patient'
    
    "input_path: Path of patient with nodules - should contain files of one patient only"
    
    print("Processing",input_path)
            
    num=0 #Counter of the number of files for this patient
    size_CTs=0 #Count the number of CT files - original scan and annotations files together

    # #Initialize empty lists to save CT file names with images
    CT_main_scan=[]

    #https://python.plainenglish.io/how-to-design-python-functions-with-multiprocessing-6d97b6db0214
    #https://github.com/tqdm/tqdm#usage
    for file in tqdm(os.listdir(input_path)):#,desc='step1',ascii=True): #Parallel loop into each patient 
        if input_path.endswith('/'): #Ensure that path ends with '/'
            file_path=input_path+file #subdir with files
        else:
            file_path=input_path+'/'+file 
        
        if os.path.isfile(file_path): #If we have a file and not a subdir
            dicom_file=dicom.dcmread(file_path) #Read file
            num+=1 #Increase files counter by 1
         
            if dicom_file.Modality=='CT': #For CT images
                    image=dicom_file.pixel_array #Load CT slice
                    
                    if len(np.unique(image))==1: #Problem if only 0 values
                        print("CT image slice of file {} is empty".format(file))
                            
                    if image.shape[0]==512: #Original scan slice or annotated image
                        if len(file.split('.')[3])==1: #Increase size_CT only for original scan - just one value in that position eg. 4 or 6
                            size_CTs=size_CTs+1
                            CT_main_scan.append(file)

    return CT_main_scan, size_CTs 

CT_main_scan, size_CTs =zip(*Parallel(n_jobs=-1)(delayed(CT_files_extract)(path) for index,path in enumerate(inputs)))


#New implementations

def convert_to_hounsfield_units(dicom_data): #Convert pixel data to HU units
    pixel_array=dicom_data.pixel_array
    rescale_slope=dicom_data.RescaleSlope
    rescale_intercept=dicom_data.RescaleIntercept
    
    #Convert pixel values to HU
    hu_values=(pixel_array*rescale_slope)+rescale_intercept
    return hu_values    
    
#Save print statements in txt
output_file_path=output_path+'/output.txt'
original_stdout=sys.stdout
sys.stdout=open(output_file_path,'w')

#Initialize empty lists to store variables    
mean_hu_all=[]
noise_hu_all=[]

for ind,patient in enumerate(CT_main_scan): #Loop over the index and the scan slice of each participant
    size_scan=len(patient) #Number of slices of the scan
    middle_slice=int(np.ceil(size_scan/2)) #Middle slice of the scan
    
    print("Loaded participant",inputs[ind].split('/')[-1],"with Middle slice being",str(middle_slice))
    
    #Lists to be filled with patch regions
    patch_upper_up=[]
    patch_upper_low=[]
    patch_bottom_up=[]
    patch_bottom_middle=[]
    patch_bottom_low=[]
    patch_bottom_lowest=[]        
    
    for slice_num in patient: #Loop over slices of that participant
        if int(slice_num.split('.')[4]) in range (middle_slice-3,middle_slice+3): #If you find the middle slice
            dicom_file=dicom.dcmread(inputs[ind]+'/'+slice_num) #Read slice DICOM data
            image=dicom_file.pixel_array #Load CT slice            
            
            #Get patches
            upper_up=image[10:30,220:300]
            upper_low=image[20:40,220:300]
            bottom_up=image[460:480,220:300]
            bottom_middle=image[470:490,220:300]
            bottom_low=image[480:500,220:300]
            bottom_lowest=image[490:510,220:300]

            patch=convert_to_hounsfield_units(dicom_file) #Convert to HU

            for ind_patch in range(6): #Get corresponding patch - 6 different ones checked
                if ind_patch==0:
                    patch_upper_up.append(patch[10:30,220:300])
                if ind_patch==1:
                    patch_upper_low.append(patch[20:40,220:300])
                if ind_patch==2:
                    patch_bottom_up.append(patch[460:480,220:300])
                if ind_patch==3:
                    patch_bottom_middle.append(patch[470:490,220:300])
                if ind_patch==4:
                    patch_bottom_low.append(patch[480:500,220:300])
                if ind_patch==5:
                    patch_bottom_lowest.append(patch[490:510,220:300])
         
        
    patches_mean=[np.mean(patch_upper_up),np.mean(patch_upper_low),np.mean(patch_bottom_up),np.mean(patch_bottom_middle),
                  np.mean(patch_bottom_low),np.mean(patch_bottom_lowest)]
    patches_stds=[np.std(patch_upper_up),np.std(patch_upper_low),np.std(patch_bottom_up),np.std(patch_bottom_middle),
                  np.std(patch_bottom_low),np.std(patch_bottom_lowest)]
    
    #Used just for prints below
    patches_max=[np.max(patch_upper_up),np.max(patch_upper_low),np.max(patch_bottom_up),np.max(patch_bottom_middle),
                 np.max(patch_bottom_low),np.max(patch_bottom_lowest)]
    patches_min=[np.min(patch_upper_up),np.min(patch_upper_low),np.min(patch_bottom_up),np.min(patch_bottom_middle),
                 np.min(patch_bottom_low),np.min(patch_bottom_lowest)]
    
    #Lowest noise and mean of the slices in HU values
    min_index=np.argmin(patches_stds)
    min_noise_pat=patches_stds[min_index]
    min_mean_pat=patches_mean[min_index]
    
    mean_hu_all.append(min_mean_pat)
    noise_hu_all.append(min_noise_pat)
    print("Mean of 3D volume (min of all boxes) in HU is",min_mean_pat, 'and std (noise) is',min_noise_pat) #Noise in HU same as non-HU values
    print("Min value of 3D volume in HU is",patches_min[min_index],"and max is",patches_max[min_index]) #Not representative of noise range
    print("\n") 
    
    #Plot of middle slice
    #Initialize figure with slice to save it with boundign box around region of interest
    fig,ax=plt.subplots()
    ax.imshow(image)#Get whole image - 'cmap=plt.cm.gray If we want grayscale image
    
    if min_index==0:
        #Create a rectangle region
        rect=patches.Rectangle((220,10),80,20,linewidth=2,edgecolor='r',facecolor='none') #(xmin, ymin),xmax-xmin,ymax-min
    if min_index==1:
        rect=patches.Rectangle((220,20),80,20,linewidth=2,edgecolor='r',facecolor='none')
    if min_index==2:
        rect=patches.Rectangle((220,460),80,20,linewidth=2,edgecolor='r',facecolor='none')
    if min_index==3:
        rect=patches.Rectangle((220,470),80,20,linewidth=2,edgecolor='r',facecolor='none')
    if min_index==4:
        rect=patches.Rectangle((220,480),80,20,linewidth=2,edgecolor='r',facecolor='none')
    if min_index==5:
        rect=patches.Rectangle((220,490),80,20,linewidth=2,edgecolor='r',facecolor='none')
    
    plt.title("Slice is: "+str(middle_slice) +", of participant: "+str(inputs[ind].split('/')[-1]))
    ax.add_patch(rect)
    plt.savefig(output_path+'/'+str(image.shape[0])+'_'+str(inputs[ind].split('/')[-1])+'_'+
                str(middle_slice)+'_middle_slice_box'+'.png',dpi=200) #Save figure
    plt.close()
        
print("Average HU of region over all scans is",np.mean(mean_hu_all))
print("Mean HU of noise over all scans is",np.mean(noise_hu_all))
print("Max HU of noise of region over all scans is",np.max(noise_hu_all))
print("Min HU of noise of region over all scans is",np.min(noise_hu_all))
print("Median HU of noise of region over all scans is",np.median(noise_hu_all))

participants_list=[x[0].split('.')[0][-6:] for x in CT_main_scan]
noise_sorted,participants_sorted=zip(*sorted(zip(noise_hu_all,participants_list),key=lambda x:x[0]))
print("All values of noise are (sorted):", noise_sorted)
print("Participants with the above noise are",participants_sorted)

print("Took",time.time()-start,"secs to run")
sys.stdout.close()
sys.stdout=original_stdout