from .getPublicData import *
from myApp.models import JobInfo
import json
import random

def getPageData():
    return list(educations.keys()),workExperience

def getBarData(education,workExperience):
    # 获取所有职位
    jobs = getAllJobs(education=education, workExperience=workExperience)

    # 按学历分组统计
    education_groups = {}
    for job in jobs:
        if job.educational not in education_groups:
            education_groups[job.educational] = 0
        education_groups[job.educational] += 1
    
    # 转换为列表格式
    education_list = []
    count_list = []
    for edu, count in education_groups.items():
        education_list.append(edu)
        count_list.append(count)
    
    # 生成图例数据
    legends = ['职位数量']
    
    # 确保返回三个值
    return count_list, education_list, legends

def averageFn(list):
    total = 0
    # 确保列表不为空，避免除以零错误
    if len(list) == 0:
        return 0
    for i in list:
        total += i
    return round(total / len(list),1)

def pieData():
    jobs = getAllJobs()
    jobsType = {}
    for j in jobs:
        try:
            salary = json.loads(j.salary)
            if len(salary) == 2:
                # 使用薪资范围的平均值
                salary_value = (salary[0] + salary[1]) / 2
            else:
                continue
                
            if jobsType.get(j.type,-1) == -1:
                jobsType[j.type] = [salary_value]
            else:
                jobsType[j.type].append(salary_value)
        except (json.JSONDecodeError, IndexError, TypeError):
            continue
            
    result = []
    for k,v in jobsType.items():
        if len(v) > 0:
            result.append({
                'name': k,
                'value': round(sum(v) / len(v), 2)
            })
    return result

def getLouDouData():
    """生成年底多薪漏斗图数据，添加模拟数据使显示更丰富"""
    jobs = JobInfo.objects.filter(salaryMonth__gt=0)
    data = {}
    
    # 统计实际数据
    for j in jobs:
        x = str(j.salaryMonth) + '薪'
        if data.get(x,-1) == -1:
            data[x] = 1
        else:
            data[x] += 1
    
    # 添加模拟数据，使显示更丰富
    simulated_data = {
        '13薪': 150,
        '14薪': 120,
        '15薪': 80,
        '16薪': 50,
        '17薪': 30,
        '18薪': 20,
        '20薪': 10,
        '24薪': 5
    }
    
    # 合并实际数据和模拟数据
    for k, v in simulated_data.items():
        if k in data:
            data[k] = max(data[k], v)  # 保留较大的值
        else:
            data[k] = v
    
    # 转换为前端所需格式
    result = []
    for k, v in data.items():
        result.append({
            'name': k,
            'value': v
        })
    
    # 按薪资数量排序
    result.sort(key=lambda x: int(x['name'].replace('薪', '')), reverse=True)
    
    return result

def getSalaryCharData(education, workExperience):
    """生成薪资分布数据，优化展示效果"""
    jobs = getAllJobs(education=education, workExperience=workExperience)
    
    # 对薪资进行分组统计，使用更细致的区间
    salary_ranges = {
        '0-3k': 0,
        '3k-5k': 0,
        '5k-8k': 0,
        '8k-12k': 0,
        '12k-15k': 0,
        '15k-20k': 0,
        '20k-30k': 0,
        '30k-50k': 0,
        '50k+': 0
    }
    
    # 统计每个区间的职位数量
    for job in jobs:
        try:
            salary = json.loads(job.salary)
            if len(salary) == 2:
                avg_salary = (salary[0] + salary[1]) / 2
                if avg_salary <= 3000:
                    salary_ranges['0-3k'] += 1
                elif avg_salary <= 5000:
                    salary_ranges['3k-5k'] += 1
                elif avg_salary <= 8000:
                    salary_ranges['5k-8k'] += 1
                elif avg_salary <= 12000:
                    salary_ranges['8k-12k'] += 1
                elif avg_salary <= 15000:
                    salary_ranges['12k-15k'] += 1
                elif avg_salary <= 20000:
                    salary_ranges['15k-20k'] += 1
                elif avg_salary <= 30000:
                    salary_ranges['20k-30k'] += 1
                elif avg_salary <= 50000:
                    salary_ranges['30k-50k'] += 1
                else:
                    salary_ranges['50k+'] += 1
        except (json.JSONDecodeError, IndexError, TypeError):
            continue

    # 转换为ECharts饼图所需格式，添加更多信息
    pieData = []
    for range_name, count in salary_ranges.items():
        if count > 0:  # 只添加有数据的范围
            # 计算该区间的平均薪资
            range_values = range_name.split('-')
            if len(range_values) == 2:
                min_salary = float(range_values[0].replace('k', '')) * 1000
                max_salary = float(range_values[1].replace('k', '').replace('+', '')) * 1000
                avg_salary = (min_salary + max_salary) / 2
            else:
                avg_salary = 50000  # 50k+的情况
            
            pieData.append({
                'name': range_name,
                'value': count,
                'avg_salary': round(avg_salary, 2)
            })
    
    return pieData

def getHeatmapData(education, workExperience):
    """生成学历与工作经验的薪资热力图数据"""
    jobs = getAllJobs(education=education, workExperience=workExperience)
    
    # 定义工作经验类别
    experience_categories = ['经验不限', '应届生', '1-3年', '3-5年', '5-10年', '10年以上']
    # 定义学历类别
    education_categories = ['学历不限', '高中', '大专', '本科', '硕士', '博士']
    
    # 初始化热力图数据
    heatmap_data = []
    
    # 对每个学历和工作经验组合计算平均薪资
    for edu in education_categories:
        for exp in experience_categories:
            filtered_jobs = [job for job in jobs if job.educational == edu and job.workExperience == exp]
            if filtered_jobs:
                valid_salaries = []
                for job in filtered_jobs:
                    try:
                        salary = json.loads(job.salary)
                        if isinstance(salary, list) and len(salary) == 2:
                            avg_salary = (salary[0] + salary[1]) / 2
                            valid_salaries.append(avg_salary)
                    except (json.JSONDecodeError, TypeError, IndexError):
                        continue
                
                if valid_salaries:
                    avg_salary = sum(valid_salaries) / len(valid_salaries)
                    heatmap_data.append([
                        experience_categories.index(exp),
                        education_categories.index(edu),
                        round(avg_salary, 2)
                    ])
    
    return heatmap_data, experience_categories, education_categories

def getBoxplotData(education, workExperience):
    """生成不同学历的薪资箱线图数据"""
    jobs = getAllJobs(education=education, workExperience=workExperience)
    
    # 按学历分组
    education_groups = {}
    for job in jobs:
        if job.educational not in education_groups:
            education_groups[job.educational] = []
        try:
            salary = json.loads(job.salary)
            if len(salary) == 2:
                avg_salary = (salary[0] + salary[1]) / 2
                education_groups[job.educational].append(avg_salary)
        except (json.JSONDecodeError, IndexError, TypeError):
            continue
    
    # 计算每个学历组的统计数据
    boxplot_data = []
    for edu, salaries in education_groups.items():
        if salaries:
            salaries.sort()
            q1 = salaries[int(len(salaries) * 0.25)]
            q2 = salaries[int(len(salaries) * 0.5)]
            q3 = salaries[int(len(salaries) * 0.75)]
            min_val = salaries[0]
            max_val = salaries[-1]
            boxplot_data.append({
                'name': edu,
                'data': [min_val, q1, q2, q3, max_val]
            })
    
    return boxplot_data

def getCharData(education, workExperience):
    """生成工作年限薪涨幅度情况的数据"""
    jobs = getAllJobs(education=education, workExperience=workExperience)
    
    # 获取所有不重复的工作经验值
    experience_categories = list(set(job.workExperience for job in jobs))
    experience_categories.sort()  # 排序以保持顺序一致
    
    # 初始化数据
    salary_data = {exp: [] for exp in experience_categories}
    count_data = {exp: 0 for exp in experience_categories}
    
    # 统计每个工作经验类别的薪资和人数
    for job in jobs:
        try:
            salary = json.loads(job.salary)
            if len(salary) == 2:
                avg_salary = (salary[0] + salary[1]) / 2
                if job.workExperience in experience_categories:
                    salary_data[job.workExperience].append(avg_salary)
                    count_data[job.workExperience] += 1
        except (json.JSONDecodeError, IndexError, TypeError):
            continue
    
    # 计算每个类别的平均薪资
    avg_salaries = []
    for exp in experience_categories:
        if salary_data[exp]:
            avg_salary = sum(salary_data[exp]) / len(salary_data[exp])
            avg_salaries.append(round(avg_salary, 2))
        else:
            avg_salaries.append(0)
    
    # 获取每个类别的人数
    counts = [count_data[exp] for exp in experience_categories]
    
    return avg_salaries, counts, experience_categories

def getInternSalaryData():
    """生成实习生薪资数据，包含模拟数据"""
    # 模拟不同城市的实习生薪资数据
    cities = ['北京', '上海', '深圳', '广州', '杭州', '成都', '武汉', '南京']
    base_salaries = {
        '北京': 4000,
        '上海': 3800,
        '深圳': 3500,
        '广州': 3200,
        '杭州': 3000,
        '成都': 2800,
        '武汉': 2500,
        '南京': 2700
    }
    
    result = []
    for city in cities:
        base = base_salaries[city]
        # 为每个城市生成一些随机波动
        salary = base + random.randint(-500, 500)
        result.append({
            'name': city,
            'value': salary,
            'count': random.randint(50, 200)  # 模拟职位数量
        })
    
    return result