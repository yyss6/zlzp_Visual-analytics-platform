from .getPublicData import *
from myApp.models import JobInfo
import json
def getPageData():
    return list(educations.keys())

def getAverged(list):
    result = 0
    if len(list) == 0:
        return 0
    for i in list:
        result += i
    return round(result / len(list),2)

def getExpirenceData(educational):
    hasEmpty = False
    if educational == '不限':
        jobs = JobInfo.objects.all()
    else:
        jobs = JobInfo.objects.filter(educational=educational)
    workExperiences = {}
    workPeople = {}
    for i in workExperience:
        workExperiences[i] = []
        workPeople[i] = 0
    for job in jobs:
        for k,v in workExperiences.items():
            if job.workExperience == k:
                if job.pratice == 0:
                    try:
                        salary_list = json.loads(job.salary)
                        if isinstance(salary_list, list) and len(salary_list) > 1:
                            if isinstance(salary_list[1], (int, float)):
                                workExperiences[k].append(salary_list[1])
                                workPeople[k] += 1
                            else:
                                pass
                        else:
                            pass
                    except (json.JSONDecodeError, TypeError):
                        pass

    for k,v in workExperiences.items():
        try:
            if isinstance(v, list):
                 workExperiences[k] = getAverged(v)
            else:
                 workExperiences[k] = 0
        except Exception as e:
            print(f"Error in getAverged for key {k}: {e}")
            workExperiences[k] = 0

    if len(jobs) == 0:
        hasEmpty = True

    return workExperience,list(workExperiences.values()),list(workPeople.values()),hasEmpty

def getPeopleData():
    jobs = getAllJobs()
    educationData = {}
    for i in jobs:
        if educationData.get(i.educational,-1) == -1:
            educationData[i.educational] = 1
        else:
            educationData[i.educational] += 1
    return list(educationData.keys()),list(educationData.values())





