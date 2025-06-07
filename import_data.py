import os
import django
import json
import sqlite3
import re
import pymysql
import pandas as pd
from datetime import datetime

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'BOSS直聘数据可视化分析.settings')
django.setup()

from myApp.models import JobInfo, User
from django.db import transaction

def create_test_data():
    # 创建测试用户
    test_user = User.objects.create(
        username='test_user',
        password='e10adc3949ba59abbe56e057f20f883e',  # 123456的MD5
        educational='本科',
        workExpirence='3-5年',
        address='北京',
        work='Python开发工程师'
    )
    
    # 创建测试职位数据
    test_jobs = [
        {
            'title': 'Python开发工程师',
            'address': '北京',
            'type': '技术',
            'educational': '本科',
            'workExperience': '3-5年',
            'workTag': json.dumps(['Python', 'Django', 'Flask']),
            'salary': json.dumps([10000, 20000]),
            'salaryMonth': '13',
            'companyTags': json.dumps(['五险一金', '年终奖', '带薪年假']),
            'hrWork': 'HR',
            'hrName': '张经理',
            'pratice': False,
            'companyTitle': '测试公司',
            'companyAvatar': 'default.png',
            'companyNature': '互联网',
            'companyStatus': '已上市',
            'companyPeople': '[100,500]',
            'detailUrl': 'http://example.com',
            'companyUrl': 'http://example.com',
            'dist': '海淀区'
        },
        {
            'title': 'Java开发工程师',
            'address': '上海',
            'type': '技术',
            'educational': '本科',
            'workExperience': '1-3年',
            'workTag': json.dumps(['Java', 'Spring', 'MySQL']),
            'salary': json.dumps([15000, 25000]),
            'salaryMonth': '14',
            'companyTags': json.dumps(['五险一金', '年终奖', '带薪年假']),
            'hrWork': 'HR',
            'hrName': '李经理',
            'pratice': False,
            'companyTitle': '测试公司2',
            'companyAvatar': 'default.png',
            'companyNature': '互联网',
            'companyStatus': '未上市',
            'companyPeople': '[50,200]',
            'detailUrl': 'http://example.com',
            'companyUrl': 'http://example.com',
            'dist': '浦东新区'
        }
    ]
    
    with transaction.atomic():
        for job_data in test_jobs:
            JobInfo.objects.create(**job_data)
    
    print("测试数据导入完成！")

def create_database():
    """创建MySQL数据库"""
    try:
        # 连接MySQL服务器（不指定数据库）
        conn = pymysql.connect(
            host='localhost',
            port=3307,
            user='root',
            password='123456',
            charset='utf8mb4'
        )
        
        # 创建游标
        cursor = conn.cursor()
        
        # 创建数据库
        cursor.execute("CREATE DATABASE IF NOT EXISTS boss DEFAULT CHARACTER SET utf8mb4")
        
        # 提交事务
        conn.commit()
        print("数据库创建成功！")
        
    except Exception as e:
        print(f"创建数据库时出错: {str(e)}")
    finally:
        if 'conn' in locals():
            conn.close()

def count_inserts(sql_script):
    """统计SQL脚本中每个表的INSERT语句数量"""
    table_counts = {}
    # 使用正则表达式匹配INSERT语句
    insert_pattern = r'INSERT INTO `([^`]+)`'
    matches = re.finditer(insert_pattern, sql_script)
    
    for match in matches:
        table_name = match.group(1)
        if table_name not in table_counts:
            table_counts[table_name] = 0
        table_counts[table_name] += 1
    
    return table_counts

def clean_sql_script(sql_script):
    """清理SQL脚本，只保留需要的表的INSERT语句"""
    # 定义需要保留的表
    allowed_tables = ['jobInfo', 'user', 'history']
    
    # 分割SQL脚本为单独的语句
    statements = sql_script.split(';')
    cleaned_statements = []
    
    for statement in statements:
        statement = statement.strip()
        if not statement:
            continue
            
        # 检查是否是INSERT语句
        if statement.upper().startswith('INSERT INTO'):
            # 提取表名
            table_match = re.search(r'INSERT INTO `([^`]+)`', statement)
            if table_match:
                table_name = table_match.group(1)
                if table_name in allowed_tables:
                    # 替换MySQL特定的语法为SQLite语法
                    statement = statement.replace('`', '')
                    cleaned_statements.append(statement)
    
    return ';'.join(cleaned_statements)

def import_sql_data():
    """导入SQL数据到MySQL数据库"""
    try:
        # 读取SQL文件
        sql_file_path = 'boss.sql'
        with open(sql_file_path, 'r', encoding='utf-8') as f:
            sql_script = f.read()
        
        # 统计原始SQL文件中的数据条数
        print("\n原始SQL文件中的数据条数：")
        original_counts = count_inserts(sql_script)
        for table, count in original_counts.items():
            print(f"{table}: {count}条")
        
        # 连接MySQL数据库
        conn = pymysql.connect(
            host='localhost',
            port=3307,
            user='root',
            password='123456',
            database='boss',
            charset='utf8mb4'
        )
        
        # 创建游标
        cursor = conn.cursor()
        
        # 分割SQL脚本为单独的语句
        statements = sql_script.split(';')
        
        # 执行每个SQL语句
        for statement in statements:
            statement = statement.strip()
            if statement:
                try:
                    cursor.execute(statement)
                except Exception as e:
                    print(f"执行语句时出错: {str(e)}")
                    print(f"问题语句: {statement[:200]}...")  # 只打印前200个字符
                    continue
        
        # 提交事务
        conn.commit()
        
        print("\n数据导入成功！")
        
    except Exception as e:
        print(f"导入数据时出错: {str(e)}")
    finally:
        if 'conn' in locals():
            conn.close()

def import_data():
    # 读取CSV文件
    df = pd.read_csv('merged-data.csv')
    
    # 清空现有数据
    JobInfo.objects.all().delete()
    
    # 创建默认用户（如果不存在）
    default_user, created = User.objects.get_or_create(
        username='root',
        defaults={
            'password': '123456',
            'createTime': datetime.now()
        }
    )
    
    # 导入数据
    for _, row in df.iterrows():
        # 处理薪资
        salary = row['薪资']
        if isinstance(salary, str):
            if '万' in salary:
                salary_range = salary.replace('万', '').split('-')
                if len(salary_range) == 2:
                    # 只提取数字和小数点
                    min_salary_str = re.findall(r'[\d.]+', salary_range[0])
                    max_salary_str = re.findall(r'[\d.]+', salary_range[1])
                    if min_salary_str and max_salary_str:
                        min_salary = float(min_salary_str[0]) * 10000
                        max_salary = float(max_salary_str[0]) * 10000
                        salary = json.dumps([min_salary, max_salary])
            else:
                salary_range = salary.replace('元', '').split('-')
                if len(salary_range) == 2:
                    min_salary_str = re.findall(r'[\d.]+', salary_range[0])
                    max_salary_str = re.findall(r'[\d.]+', salary_range[1])
                    if min_salary_str and max_salary_str:
                        min_salary = float(min_salary_str[0])
                        max_salary = float(max_salary_str[0])
                        salary = json.dumps([min_salary, max_salary])
        
        # 处理工作经验
        experience = row['经验']
        if experience == '经验不限':
            pratice = False
        else:
            years = ''.join(filter(str.isdigit, str(experience)))
            pratice = False if not years or int(years) == 0 else True
        
        # 处理公司规模
        company_size = row['规模']
        if company_size == '10000人以上':
            company_people = '[0,10000]'
        else:
            numbers = ''.join(filter(str.isdigit, str(company_size)))
            if numbers:
                company_people = f'[{numbers}]'
            else:
                company_people = '[0,10000]'
        
        # 创建JobInfo对象
        JobInfo.objects.create(
            title=row['职位'],
            address=row['区域'],
            type=row['领域'],
            educational=row['学历'],
            workExperience=row['经验'],
            workTag=json.dumps([row['领域']]),
            salary=salary,
            salaryMonth='12',
            companyTags=json.dumps([row['性质']]),
            hrWork='',
            hrName='',
            pratice=pratice,
            companyTitle=row['公司'],
            companyAvatar='default.png',
            companyNature=row['性质'],
            companyStatus='',
            companyPeople=company_people,
            detailUrl='',
            companyUrl='',
            createTime=datetime.now(),
            dist=row['区域']
        )
    
    print("数据导入完成！")

if __name__ == '__main__':
    create_database()  # 先创建数据库
    create_test_data()
    import_sql_data()  # 再导入数据
 # 再导入数据 