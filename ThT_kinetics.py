#import packages
import numpy as np
import pandas as pd
import yaml
import seaborn as sns
import matplotlib.pyplot as plt

#reads the raw data file
def extract_data():
    filename = input("Please enter the data path:")
    raw_data = pd.read_excel(filename, header= None, index_col=0)
    
    #find all occurences of the start of a table
    indices = np.where(raw_data == 'Average over replicates based on Raw Data (440/480)')
    rows = indices[0]  # First row index
    reads=[]
    #extracts the table for every timepoint
    for row in rows:
       timepoint = raw_data.iloc[row+1:row+9, 0:12]
       timepoint = timepoint.iloc[1:]
       reads.append(timepoint)
    return reads
   
#reads the config file with your experimental groups
def config_reader()-> dict:
    with open("groups.yaml") as file:
      groups = yaml.safe_load(file.read())
    with open("settings.yaml") as file:
        settings = yaml.safe_load(file.read())
        minutes_between_reads=settings.get('minutes_between_reads', None)
        index_increments=settings.get('index_increments', None)
    return groups, minutes_between_reads, index_increments

def group_data(reads, groups, minutes_between_reads):
    all_data={}
    with open("settings.yaml") as file:
        settings = yaml.safe_load(file.read())
        minutes_between_reads=settings.get('minutes_between_reads', None)
    for group, wells in groups.items():
        group_wells=pd.DataFrame()
        for well in wells:
            well_values=[] #list for all the reads 
            row = well[0]       # First character (B)
            col = int(well[1:]) # Remaining part as integer (2)
            for read in reads:
                fluorescence= read.loc[row, col]
                well_values.append(fluorescence) #creates a list of all reads for a particular well
            group_wells[well]=well_values #creates a dataframe with all wells with the same treatment
        group_wells=group_wells.T
        time_index = np.arange(minutes_between_reads, minutes_between_reads * (len(group_wells) + 1), minutes_between_reads)
        group_wells.index = time_index[:len(group_wells)]
        print (group_wells)
        all_data[group]=group_wells #creates a dictionary will all the data
    return all_data
    

def plotting(all_data, index_increments):
    for group, mydata in all_data.items():
        plt.figure(figsize=(10, 6))
        graph=sns.pointplot(data=mydata, errorbar="sd", linewidth=1)
        for index, label in enumerate(graph.get_xticklabels()): #makes sure there are not too many ticks
            if index % index_increments == 0:
                label.set_visible(True)
            else:
                label.set_visible(False)
        plt.title(group)
        plt.xlabel("Time (minutes)")
        plt.ylabel("ThT Fluorescence")
        plt.savefig(f"{group}.png")
        plt.close() 

reads=extract_data()
groups, minutes_between_reads, index_increments=config_reader()
all_data=group_data(reads, groups, minutes_between_reads)
plotting(all_data, index_increments)