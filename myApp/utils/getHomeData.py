from .getPublicData import *
import time
import json
import random
from datetime import datetime, timedelta

# 添加月份列表
monthList = ['一月', '二月', '三月', '四月', '五月', '六月', '七月', '八月', '九月', '十月', '十一月', '十二月']

# 添加学历字典
educations = {
    '学历不限': 0,
    '高中': 0.5,  # 添加高中学历
    '大专': 1,
    '本科': 2,
    '硕士': 3,
    '博士': 4
}

def getNowTime():
    timeFormat = time.localtime()
    yer = timeFormat.tm_year
    mon = timeFormat.tm_mon
    day = timeFormat.tm_mday
    return yer, monthList[mon - 1], day

def getUserCreateTime():
    users = getAllUsers()
    data = {}
    for u in users:
        if data.get(str(u.createTime),-1) == -1:
            data[str(u.createTime)] = 1
        else:
            data[str(u.createTime)] += 1
    result = []
    for k,v in data.items():
        result.append({
            'name':k,
            'value':v
        })
    return result

def getUserTop6():
    users = getAllUsers()
    def sort_fn(item):
        return time.mktime(time.strptime(str(item.createTime),'%Y-%m-%d'))
    users = list(sorted(users,key=sort_fn,reverse=True))[:6]
    return users

def getAllTags():
    jobs = JobInfo.objects.all()
    users = User.objects.all()
    educationsTop = '学历不限'
    salaryTop = 0
    salaryMonthTop = 0
    address = {}
    pratice = {}
    
    # 西安的区域列表
    xian_districts = ['雁塔', '莲湖', '长安', '未央', '碑林', '灞桥', '高新', '曲江', '经开', '西咸']
    
    for job in jobs:
        try:
            if job.educational in educations and educations[job.educational] < educations[educationsTop]:
                educationsTop = job.educational
            if job.pratice == 0:
                try:
                    salary = json.loads(job.salary)[1]
                    if salaryTop < salary:
                        salaryTop = salary
                except (json.JSONDecodeError, IndexError, TypeError):
                    continue
            try:
                salaryMonth = int(job.salaryMonth)
                if salaryMonth > salaryMonthTop:
                    salaryMonthTop = salaryMonth
            except (ValueError, TypeError):
                continue
            
            # 处理地址（区域）
            district = job.address
            if district in xian_districts:
                if address.get(district, -1) == -1:
                    address[district] = 1
                else:
                    address[district] += 1
            
            if pratice.get(job.pratice,-1) == -1:
                pratice[job.pratice] = 1
            else:
                pratice[job.pratice] += 1
        except Exception as e:
            print(f"Error processing job {job.id}: {str(e)}")
            continue

    # 按区域统计数量排序
    addressStr = sorted(address.items(), key=lambda x: x[1], reverse=True)
    addressTop = ''
    for index, item in enumerate(addressStr):
        if index == len(addressStr) - 1:
            addressTop += item[0]
        else:
            addressTop += item[0] + ','
    
    praticeMax = sorted(pratice.items(), key=lambda x: x[1], reverse=True)
    return len(jobs), len(users), educationsTop, salaryTop, addressTop, salaryMonthTop, praticeMax[0][0] if praticeMax else 0

def getAllJobsPBar():
    try:
        jobs = getAllJobs()
        if not jobs:
            print("警告：没有获取到职位数据")
            return []
            
        tempData = {}
        for job in jobs:
            try:
                create_time = str(job.createTime)
                if not create_time:
                    continue
                    
                if tempData.get(create_time, -1) == -1:
                    tempData[create_time] = 1
                else:
                    tempData[create_time] += 1
            except Exception as e:
                print(f"处理职位数据时出错: {str(e)}")
                continue
                
        if not tempData:
            print("警告：没有有效的创建时间数据")
            return []
            
        # 按时间排序
        def sort_fn(item):
            try:
                item = list(item)
                return time.mktime(time.strptime(str(item[0]), '%Y-%m-%d'))
            except Exception as e:
                print(f"时间排序出错: {str(e)}")
                return 0
                
        result = list(sorted(tempData.items(), key=sort_fn, reverse=False))
        
        # 计算百分比
        total_jobs = len(jobs)
        def map_fn(item):
            try:
                item = list(item)
                percentage = round(item[1] / total_jobs, 3) if total_jobs > 0 else 0
                item.append(percentage)
                return item
            except Exception as e:
                print(f"计算百分比时出错: {str(e)}")
                return item
                
        result = list(map(map_fn, result))
        
        # 生成模拟数据
        # 获取最早一条数据的日期
        earliest_date = datetime.strptime(result[0][0], '%Y-%m-%d') if result else datetime.now()
        
        # 生成过去30天的模拟数据
        simulated_past_data = []
        for i in range(30):
            past_date = earliest_date - timedelta(days=i+1)
            date_str = past_date.strftime('%Y-%m-%d')
            
            # 生成随机波动数据
            base_count = random.randint(30, 80)  # 基础数据量
            fluctuation = random.randint(-20, 20)  # 随机波动
            count = max(1, base_count + fluctuation)  # 确保数据量大于0
            
            # 计算百分比（基于模拟的总量或其他逻辑，这里简化处理，可以后续调整）
            # 为了简单，这里先不计算百分比，或者给一个固定/随机的百分比，实际中需要根据模拟的总量来计算
            # percentage = round(count / (total_jobs + count), 3) # total_jobs 需要重新计算包含模拟数据的总量
            percentage = random.random() # 随机百分比作为示例
            
            simulated_past_data.append([date_str, count, percentage])
            
        # 将模拟的过去数据添加到结果中
        result = simulated_past_data + result

        # 重新按时间排序，确保模拟数据和真实数据都在正确的时间顺序上
        def sort_fn(item):
            try:
                item = list(item)
                return time.mktime(time.strptime(str(item[0]), '%Y-%m-%d'))
            except Exception as e:
                print(f"时间排序出错: {str(e)}")
                return 0
                
        result = list(sorted(result, key=sort_fn, reverse=False))
        
        # 确保返回的数据格式正确
        valid_result = []
        for item in result:
            if len(item) == 3 and all(isinstance(x, (str, int, float)) for x in item):
                valid_result.append(item)
                
        return valid_result
        
    except Exception as e:
        print(f"获取职位数据时发生错误: {str(e)}")
        return []

def getTablaData():
    jobs = getAllJobs()
    for i in jobs:
        try:
            i.workTag = '/'.join(json.loads(i.workTag))
            if i.companyTags != "无":
                i.companyTags = "/".join(json.loads(i.companyTags)[0].split('，'))
            if i.companyPeople == '[0,10000]':
                i.companyPeople = '10000人以上'
            else:
                i.companyPeople = json.loads(i.companyPeople)
                i.companyPeople = list(map(lambda x:str(x) + '人',i.companyPeople))
                i.companyPeople = '-'.join(i.companyPeople)
            i.salary = json.loads(i.salary)[1]
        except (json.JSONDecodeError, IndexError, TypeError, AttributeError) as e:
            print(f"Error processing job {i.id}: {str(e)}")
            continue
    return jobs

def generateSimulatedCompanyStatusData():
    """生成模拟的公司状态（融资阶段）数据，用于复杂图表展示"""
    statuses = ['未融资', '天使轮', 'A轮', 'B轮', 'C轮', 'D轮及以上', '已上市', '无需融资']
    industries = ['互联网', '电子商务', '企业服务', '游戏', '金融', '教育', '医疗', '房地产']

    data = []

    # 生成一些模拟的父级（行业）数据
    for industry in industries:
        industry_node = {
            'name': industry,
            'children': []
        }
        # 为每个行业生成一些模拟的子级（融资阶段）数据
        for status in statuses:
            count = random.randint(10, 200) # 模拟该行业下该融资阶段的公司数量
            if count > 0:
                 industry_node['children'].append({
                    'name': status,
                    'value': count
                })
        # 只有当行业下有子节点时才添加该行业
        if industry_node['children']:
             data.append(industry_node)

    # 添加一些没有明确行业分类的顶级融资阶段数据
    for status in statuses:
         count = random.randint(5, 50) # 模拟没有明确行业分类的该融资阶段的公司数量
         if count > 0:
              data.append({
                'name': status,
                'value': count
            })

    return data