#!/usr/bin/python3

import pandas as pd 
import numpy as np
import os
import csv
from pathlib import Path
import datetime as dt
import pytz


# Specify Directory Locations 
data_dir='./Data' # This is where the daily attendance data is stored 


# Custom Errors 

class Error(Exception):
    pass
class FileNameError(Error):
    # Raised when the filename is not of set format
    pass
class FileAvailabilityError(Error):
    # Raised when either class Namelist not available or Attendance list not available
    pass
class DataMismatchError(Error):
    # Raised when the data is not of the accepted Format
    pass 


# Functions required :

def avg_time(datetimes):
    total = sum(dt.hour * 3600 + dt.minute * 60 + dt.second for dt in datetimes)
    avg = total / len(datetimes)
    minutes, seconds = divmod(int(avg), 60)
    hours, minutes = divmod(minutes, 60)
    return avg


def attendance(filename):
    try:
        date = filename.split('_')[1] #Getting Date from File Name
        date = date.split('.')[0] 
        subject = filename.split('_')[0]
    except:
        raise FileNameError
    try:
        df = pd.read_csv(filename,skiprows=4)
        data = pd.read_csv('../'+subject + '.csv')
    except:
        raise FileAvailabilityError

    try:
        if df.shape[1]>2:    
            #### Marking Present Based on Names alone ####
            
            names=df['Full Name'].to_list()
            data[date]=data['Full Name'].apply(lambda x: 1 if x in names else "") #Leaving Empty for absenteers
            df['Time in Call'] = pd.to_datetime(df['Time in Call'])
            df['Time in Call']=df['Time in Call'].dt.time
            # Getting the values of time in call for all names in our main csv (ie.data) 
            # if they are absent our attendance csv(ie.df) wont have their names and it will return a null series object

            timelist=[]
            for name in data["Full Name"]:
                a=df[df['Full Name']==name]['Time in Call']
                timelist.append(a.astype(str))

            # Identifying the null series object and replacing it with ("00:00:00")
            finallist=list(map(lambda x:pd.Series("00:00:00") if x.empty==True else x,timelist))
            # Creating a New column in main dataframe (data) and assigning it to finallist
            data['Time in Call']=finallist
            data['Time in Call']=data['Time in Call'].apply(pd.Series).stack().reset_index(drop = True) # organising #
            data['Time in Call'].astype(str) #converting to string
            data['Time in Call'] = pd.to_datetime(data['Time in Call']) #converting to datetime object #
            data['Time in Call']=data['Time in Call'].dt.time # Leaving out date and taking only time #
            data['totalTime']=data['Time in Call'].apply(lambda x:(x.hour*3600 + x.minute*60 +x.second))# Calculating Total Time in Sec #

            # Applying Threshold Conditions

            times = data['Time in Call'].to_list()
            avg = avg_time(times)
            threshold = 0.3*avg
            data[date]=data['totalTime'].apply(lambda x: 1 if x >threshold else "absent")

            # Droping Unnecessary Columns
            data.drop(['totalTime','Time in Call'],axis=1,inplace=True)

            # Converting to csv #
            data.to_csv('../'+subject +'.csv',index=False)
        else:
            names=df['Full Name'].to_list()
            data[date]=data['Full Name'].apply(lambda x: 1 if x in names else "absent") 
            data.to_csv('../'+subject +'.csv',index=False)
    
    except:
        raise DataMismatchError


# Driver Program

os.chdir(data_dir)
os.listdir()
for file in os.listdir():
    try:
        attendance(str(file))
    except(FileNameError):
        print('file')
os.chdir('..')
