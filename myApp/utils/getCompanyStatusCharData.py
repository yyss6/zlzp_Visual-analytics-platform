from .getPublicData import *
from myApp.models import JobInfo
import json
import random # 导入 random 模块

def getPageData():
    job = []
    jobs = getAllJobs()
    for i in jobs: job.append(i.type)
    return list(set(job))

def getTechnologyData(type):
    print(type)
    if type == '不限':
        jobs = JobInfo.objects.all()
    else:
        jobs = JobInfo.objects.filter(type=type)
    workTagData = {}
    for job in jobs:
        workTag = json.loads(job.workTag)
        for w in workTag:
            if not w:break
            if workTagData.get(w,-1) == -1:
                workTagData[w] = 1
            else:
                workTagData[w] += 1
    result = sorted(workTagData.items(),key=lambda x:x[1],reverse=True)[:20]
    teachnologyRow = []
    teachnologyColumn = []
    for k,v in result:
        teachnologyRow.append(k)
        teachnologyColumn.append(v)
    return teachnologyRow,teachnologyColumn

def getCompanyStatusData():
    jobs = getAllJobs()
    statusData = {}
    for job in jobs:
        if statusData.get(job.companyStatus,-1) == -1:
            statusData[job.companyStatus] = 1
        else:
            statusData[job.companyStatus] += 1
    result = []
    for k,v in statusData.items():
        result.append({
            'name':k,
            'value':v
        })
    return result

def generateSimulatedCompanyStatusData():
    """生成模拟的公司状态（融资阶段）层级数据，用于复杂图表展示"""
    # 定义可能的融资阶段和行业
    statuses = ['未融资', '天使轮', 'A轮', 'B轮', 'C轮', 'D轮及以上', '已上市', '无需融资']
    industries = ['互联网', '电子商务', '企业服务', '游戏', '金融', '教育', '医疗', '房地产', '制造业', '消费品', '其他']

    data = []

    # 生成一些模拟的父级（行业）数据
    for industry in industries:
        industry_node = {
            'name': industry,
            'children': []
        }
        # 为每个行业生成一些模拟的子级（融资阶段）数据
        # 每个行业不是包含所有融资阶段，增加一些随机性
        selected_statuses = random.sample(statuses, random.randint(2, len(statuses)))
        for status in selected_statuses:
            count = random.randint(5, 150) # 模拟该行业下该融资阶段的公司数量
            if count > 0:
                 industry_node['children'].append({
                    'name': status,
                    'value': count
                })

        # 只有当行业下有子节点时才添加该行业，并且给行业节点一个总值（可选，取决于图表类型）
        if industry_node['children']:
            # 计算行业总数作为行业节点的值
            total_in_industry = sum(item['value'] for item in industry_node['children'])
            industry_node['value'] = total_in_industry # 为父节点设置 value
            data.append(industry_node)

    # 添加一些没有明确行业分类的顶级融资阶段数据
    for status in statuses:
         count = random.randint(1, 30) # 模拟没有明确行业分类的该融资阶段的公司数量
         if count > 0:
              data.append({
                'name': status,
                'value': count
            })

    return data