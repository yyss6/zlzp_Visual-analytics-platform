from .getPublicData import *
from myApp.models import JobInfo
import json
def getPageData():
    jobs = getAllJobs()
    typeData = []
    for i in jobs:typeData.append(i.type)
    return list(set(typeData))

def getCompanyBar(type):
    if type == 'all':
        jobs = JobInfo.objects.all()
    else:
        jobs = JobInfo.objects.filter(type=type)
    natureData = {}
    for i in jobs:
        if natureData.get(i.companyNature,-1) == -1:
            natureData[i.companyNature] = 1
        else:
            natureData[i.companyNature] += 1
    natureList = list(sorted(natureData.items(),key=lambda x:x[1],reverse=True))
    rowData = []
    columnData = []
    for k,v in natureList:
        rowData.append(k)
        columnData.append(v)
    return rowData[:20],columnData[:20]

def getCompanyPie(type):
    if type == 'all':
        jobs = JobInfo.objects.all()
    else:
        jobs = JobInfo.objects.filter(type=type)
    addressData = {}
    for i in jobs:
        if addressData.get(i.address, -1) == -1:
            addressData[i.address] = 1
        else:
            addressData[i.address] += 1
    result = []
    for k,v in addressData.items():
        result.append({
            'name':k,
            'value':v
        })
    return result[:40]

def getCompanPeople(type):
    if type == 'all':
        jobs = JobInfo.objects.all()
    else:
        jobs = JobInfo.objects.filter(type=type)

    def map_fn(item):
        try:
            company_people_list = json.loads(item.companyPeople)
            # 检查列表长度是否足够且是列表类型
            if isinstance(company_people_list, list) and len(company_people_list) > 1:
                item.companyPeople = company_people_list[1]
            else:
                # 如果列表长度不足或不是列表，设置默认值
                item.companyPeople = 0  # 或者 None，根据你的需求决定
        except (json.JSONDecodeError, TypeError):
            # 处理JSON解析错误或类型错误
            item.companyPeople = 0  # 或者 None

        return item

    jobs = list(map(map_fn,jobs))
    data = [0 for x in range(6)]

    for i in jobs:
        p = i.companyPeople
        # 确保p是数字类型再进行比较
        if isinstance(p, (int, float)):
            if p <= 20:
                data[0] += 1
            elif p <= 100:
                data[1] += 1
            elif p <= 500:
                data[2] += 1
            elif p <= 1000:
                data[3] += 1
            elif p < 10000:
                data[4] += 1
            else:
                data[5] += 1
    return companyPeople,data