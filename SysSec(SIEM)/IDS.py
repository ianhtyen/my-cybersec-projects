#!/usr/bin/env python3
import sys
import numpy as np
import scipy.stats as stats
from datetime import datetime
import json

statdict = {}
eventdict = {}

def read_file(filename):
    with open(filename) as file:
        return [line.rstrip() for line in file]

# initial input
def datafile_splice(list, type, noofitems): #split data with splice or normally
    tempdict = {}
    temp = []
    for _, line in enumerate(list):
        if type == "initial":
            templist = line.split(':')
            tempdict[templist[0]] = templist[1:noofitems]
        elif type == "analysis":
            templist = line.split('--')
            temp.append(templist)
    if type == "initial":
        return tempdict
    else:
        return temp

def float_dict(dictlist):
    for key, values in dictlist.items():
        dictlist[key] = [float(x) for x in values]
    return dictlist

def convert_float_list_dict(tempdict):
    for k, v in tempdict.items():
       tempdict[k] = list(map(float, v))
    return tempdict

# Analysis Engine
def analysis_engine(weight, logFileName):
    with open("baselinestats.json", "r") as ro: # read and get baseline stats for mean and std
        baseline = json.load(ro)
    logData = read_file(logFileName)
    logList = datafile_splice(logData, "analysis", None)
    dailyWrite = [] # to write to file later for daily anomaly counter
    anomalySumList = []
    for value in logList:
        totalCounter = 0
        totalAnomalyList = []
        dayCount = value.pop(0)
        for event in value:
            temp = event.split(":")
            num = float(temp[1])
            totalCounter = totalCounter + num
            if temp[0] == "Logins":
                loginAnomaly = (abs(num - baseline["Mean"]["Logins"])/ baseline["SD"]["Logins"]) * weight[0]
                totalAnomalyList.append(loginAnomaly) # append event anomaly counter
            elif temp[0] == "Time online":
                timeAnomaly = (abs(num - baseline["Mean"]["Time online"])/ baseline["SD"]["Time online"]) * weight[1]
                totalAnomalyList.append(timeAnomaly)
            elif temp[0] == "Emails sent":
                sendAnomaly = (abs(num - baseline["Mean"]["Emails sent"])/ baseline["SD"]["Emails sent"]) * weight[2]
                totalAnomalyList.append(sendAnomaly)
            elif temp[0] == "Emails opened":
                openAnomaly = (abs(num - baseline["Mean"]["Emails opened"])/ baseline["SD"]["Emails opened"]) * weight[3]
                totalAnomalyList.append(openAnomaly)
            elif temp[0] == "Emails deleted":
                deleteAnomaly = (abs(num - baseline["Mean"]["Emails deleted"])/ baseline["SD"]["Emails deleted"]) * weight[4]
                totalAnomalyList.append(deleteAnomaly)

        anomalySumList.append(round(sum(totalAnomalyList),2)) # sum of event anomaly counters per day
        dailyWrite.append(f"Total Daily events for {dayCount}: {round(totalCounter,2)}---Total Anomaly Counter:{round(sum(totalAnomalyList),2)}\n")

    dailyFile = f"Daily_{logFileName}"
    with open(dailyFile, "w") as wo:
        for line in dailyWrite:
            wo.write(line)

    return anomalySumList
        
# Alert Engine
def alert_engine(anomalySum, weight):
    threshold = 2 * sum(weight)
    print(f"---Threshold:{threshold}---")
    count = 1
    for value in anomalySum:
        if value >= threshold:
            print(f"---Day {count}: ({value})--- ALERT DETECTED (Flagged)")
        elif value < threshold:
            print(f"---Day {count}: ({value})--- OKAY")
        count = count + 1
    print("\n")

# Activity Stimulation Engine (Some parts of analysis engine (mean,std of generated datasets) is merged into this function)
def activity_engine(statlist, eventlist, part, daysnum, eventno):
    weightlist = []
    discretedict, continousdict = ({}, {})
    statdict = float_dict(datafile_splice(statlist,"initial",3)) # Event Name: [mean, standard deviation]
    eventdict = datafile_splice(eventlist,"initial", 5)
    eventKey = []

    # check if events are the same
    for key in statdict:
        if key in eventdict:
            eventKey.append(key)
    
    if (len(eventKey) == eventno):
        for key, value in eventdict.items(): # Event Name: [min, max]
            if value[0] == 'D':
                value.pop(0)
                weightlist.append(int(value.pop()))
                discretedict[key] = value 
            else:
                value.pop(0)
                weightlist.append(int(value.pop()))
                continousdict[key] = value

        for key, value in statdict.items(): # key in reasonable max value (own formula: (mean+std) * 2)

            for tempk in discretedict:
                if key == tempk:
                    if discretedict[tempk][1] == "":
                        max = sum((value)) * 2
                        discretedict[tempk][1] = round(max)

            for tempk in continousdict:
                if key == tempk:
                    if continousdict[tempk][1] == "":
                        max = sum((value)) * 2
                        continousdict[tempk][1] = round(max)
        
        continousdict = convert_float_list_dict(continousdict)
        discretedict = convert_float_list_dict(discretedict)
        baselinedict = {"Mean": {}, "SD": {}}
    # event format shows discrete only logins, emails (sent, opened, deleted) while continous only time online
        for key, value in statdict.items():
            for k in discretedict:
                if key == k == 'Logins':
                    mean = statdict[key][0]
                    std = statdict[key][1]
                    min = discretedict[key][0]
                    max = discretedict[key][1]
                    loginData = generate_dataset(min, max, mean, std, 'D',daysnum)
                    baselinedict["Mean"]["Logins"] = round(np.mean(loginData),2)
                    baselinedict["SD"]["Logins"] = round(np.std(loginData),2) # no ddof due to the the list of data is the whole population instead of sample of population
                elif key == k == 'Emails sent':
                    mean = statdict[key][0]
                    std = statdict[key][1]
                    min = discretedict[key][0] 
                    max = discretedict[key][1]
                    sendData = generate_dataset(min, max, mean, std, 'D', daysnum)
                    baselinedict["Mean"]["Emails sent"] = round(np.mean(sendData),2)
                    baselinedict["SD"]["Emails sent"] = round(np.std(sendData),2)
                elif key == k == 'Emails opened':
                    mean = statdict[key][0]
                    std = statdict[key][1]
                    min = discretedict[key][0]
                    max = discretedict[key][1]
                    openData = generate_dataset(min, max, mean, std, 'D', daysnum)
                    baselinedict["Mean"]["Emails opened"] = round(np.mean(openData),2)
                    baselinedict["SD"]["Emails opened"] = round(np.std(openData),2)
                elif key == k == 'Emails deleted':
                    mean = statdict[key][0]
                    std = statdict[key][1]
                    min = discretedict[key][0]
                    max = discretedict[key][1]
                    deleteData = generate_dataset(min, max, mean, std, 'D', daysnum)
                    baselinedict["Mean"]["Emails deleted"] = round(np.mean(deleteData),2)
                    baselinedict["SD"]["Emails deleted"] = round(np.std(deleteData),2)

            for k in continousdict:
                if key == k:
                    mean = statdict[key][0]
                    std = statdict[key][1]
                    min = continousdict[key][0]
                    max = continousdict[key][1]
                    onlineData = generate_dataset(min, max, mean, std, 'C', daysnum)
                    baselinedict["Mean"]["Time online"] = round(np.mean(onlineData),2)
                    baselinedict["SD"]["Time online"] = round(np.std(onlineData),2)

        statsdata = json.dumps(baselinedict, indent=2) # first will be baseline, subsequent will be the input data
        writelist = []
        for i in range(daysnum):
            logdata = f'Days {i+1}--Logins:{loginData[i]}--Time online:{onlineData[i]}--Emails sent:{sendData[i]}--Emails opened:{openData[i]}--Emails deleted:{deleteData[i]}\n'
            writelist.append(logdata) 

        now = datetime.now() # to record for each files
        now = now.strftime("%H%M%S")
        if part == 1:
            fileLog = f"BaselineLog_{now}.txt"
        else:
            fileLog = f"Log_{now}.txt"
        with open(fileLog, 'w') as wo:
            for line in writelist:
                wo.write(line)

        if(part == 1):
            with open("baselinestats.json", "w") as of:
                of.write(statsdata) # for baseline
        else:
            with open(f"Stats_Log_{now}.txt", "w") as of:
                of.write(statsdata) # after baseline

    else:
        print("Error, Inconsistency detected!") # if there are different events, terminate program
        sys.exit(0)

    return weightlist, fileLog

def generate_dataset(min, max, mean, std, type, daysnum):
    first = True
    for _ in range(5):
        a = (min-mean)/std 
        b = (max-mean)/std

        dist = stats.truncnorm(a, b, loc=mean, scale=std)
        data = dist.rvs(daysnum) # generate random datasets based on the stats, events txt

        consistent_distribution = abs(np.mean(data) - mean) + abs(np.std(data) - std)
        if first:
            comparediff = consistent_distribution
            if type == "D":
                dataset = [round(value) for value in data] # discrete
            else:
                dataset = [round(value, 2) for value in data] # continous (2 decimal places)
            first = False
        
        if comparediff > consistent_distribution: # smaller more accurate
            comparediff = consistent_distribution
            if type == "D":
                dataset = [round(value) for value in data] # discrete
            else:
                dataset = [round(value, 2) for value in data] # continous (2 decimal places)
        else:
            pass
            
    return dataset

def main():
    # initial
    print("---Initiating IDS---")
    part = 1
    global statdict, eventdict
    eventlist = read_file(sys.argv[1])
    statlist = read_file(sys.argv[2])
    daysnum = int(sys.argv[3])
    print("---Initial Input Done---") # End of initial input
    eventformat = eventlist.pop(0)
    # pop number of events to compare the inconsistency between the events and stats
    if eventformat == statlist.pop(0):
        print("---Activity Engine started---")
        activity_output = activity_engine(statlist, eventlist, part, daysnum, int(eventformat)) # start of activity engine
        input("Data generated successfully. Press 'Enter' to analyse the data...\n")
        _ = analysis_engine(activity_output[0], activity_output[1])
        part = 0
    else: # quit program if there is inconsistency
        print("Error, Inconsistency detected!")
        sys.exit(0)

    while True: # For alert engine
        cont = input("---IDS (Select your choice 1-2)---\n1) Use Alert Engine\n2) Quit the program\nInput: ")
        if cont == "1":
            inputFile = input("Which file to input: ")
            try:
                newstatlist = read_file(inputFile)
                tempFormat = newstatlist.pop(0)
            except:
                print("---File not found---")
            else:
                if(eventformat == tempFormat):
                    inputDays = input("Specify number of days: ")
                    if inputDays.isdigit():
                        print("---Activity Engine started---")
                        userinput_output = activity_engine(newstatlist, eventlist, part, int(inputDays), int(eventformat))
                        input("Data generated successfully. Press 'Enter' to analyse the data...\n")
                        analysisData = analysis_engine(userinput_output[0], userinput_output[1])
                        print("---Data analaysed, Alert Engine in action now---\n")
                        alert_engine(analysisData, userinput_output[0])
                    else:
                        print("---Error! Please use integers only, Going back to main menu---")
                else:
                    print("Error, Inconsistency detected!")
                    sys.exit(0)
        elif cont == "2":
            print("---Quitting the program---")
            break
        else:
            print("---Error! Please input 1 or 2 only---")

main()