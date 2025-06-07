from django.shortcuts import render,redirect
from django.core.paginator import Paginator
from myApp.models import User,JobInfo
from .utils.error import *
import hashlib
from .utils import getHomeData
from .utils import getSelfInfo
from .utils import getChangePasswordData
from .utils import getTableData
from .utils import getHisotryData
from .utils import getSalaryCharData
from .utils import getCompanyCharData
from .utils import getEducationalCharData
from .utils import getCompanyStatusCharData
from .utils import getAddressCharData
from . import word_cloud_picture
from .utils.error import *
import random
import os

def login(request):
    if request.method == 'GET':
        return render(request,'login.html')
    else:
        uname = request.POST.get('username')
        pwd = request.POST.get('password')
        md5 = hashlib.md5()
        md5.update(pwd.encode())
        pwd = md5.hexdigest()
        try:
            user = User.objects.get(username=uname,password=pwd)
            request.session['username'] = user.username
            return redirect('/myApp/home')
        except:
            return errorResponse(request,'用户名或密码出错！')

def registry(request):
    if request.method == 'GET':
        return render(request,'registry.html')
    else:
        uname = request.POST.get('username')
        pwd = request.POST.get('password')
        checkPwd = request.POST.get('checkPassword')
        try:
            User.objects.get(username=uname)
        except:
            if not uname or not pwd or not checkPwd:return errorResponse(request,'不允许为空！')
            if pwd != checkPwd : return errorResponse(request,'两次密码不符合！')
            md5 = hashlib.md5()
            md5.update(pwd.encode())
            pwd = md5.hexdigest()
            User.objects.create(username=uname,password=pwd)
            return redirect('/myApp/login')
        return errorResponse(request,"该用户名已经被注册！")

def logOut(request):
    request.session.clear()
    return redirect('login')

def home(request):
    uname = request.session.get('username')
    if not uname:
        return redirect('login')
    userInfo = User.objects.get(username=uname)
    yea,month,day = getHomeData.getNowTime()
    userCreateData = getHomeData.getUserCreateTime()
    top6Users = getHomeData.getUserTop6()
    jobsLen,usersLen,educationsTop,salaryTop,addressTop,salaryMonthTop,praticeMax = getHomeData.getAllTags()
    jobsPBarData = getHomeData.getAllJobsPBar()
    tablaData = getHomeData.getTablaData()
    return render(request,'home.html',{
        'userInfo':userInfo,
        'dateInfo':{
            'year':yea,
            'month':month,
            'day':day
        },
        'userCreateData':userCreateData,
        'top6Users':top6Users,
        'tagDic':{
            'jobsLen':jobsLen,
            'usersLen':usersLen,
            'educationsTop':educationsTop,
            'salaryTop':salaryTop,
            'addressTop':addressTop,
            'salaryMonthTop':salaryMonthTop,
            "praticeMax":praticeMax
        },
        'jobsPBarData':jobsPBarData,
        'tableData':tablaData
    })

def selfInfo(request):
    uname = request.session.get('username')
    userInfo = User.objects.get(username=uname)
    educations,workExperience,jobList = getSelfInfo.getPageData()
    if request.method == 'POST':
        getSelfInfo.changeSelfInfo(request.POST,request.FILES)
        userInfo = User.objects.get(username=uname)
    return render(request,'selfInfo.html',{
        'userInfo':userInfo,
        'pageData':{
            'educations':educations,
            'workExperience':workExperience,
            'jobList':jobList
        }
    })

def changePassword(request):
    uname = request.session.get('username')
    userInfo = User.objects.get(username=uname)
    if request.method == 'POST':
        res = getChangePasswordData.changePassword(userInfo,request.POST)
        if res != None:
            return errorResponse(request,res)
        userInfo = User.objects.get(username=uname)
    return render(request, 'changePassword.html', {
        'userInfo': userInfo
    })

def tableData(request):
    uname = request.session.get('username')
    userInfo = User.objects.get(username=uname)
    tableData = getTableData.getTableData()
    paginator = Paginator(tableData,10)
    cur_page = 1
    if request.GET.get('page'):cur_page = int(request.GET.get('page'))
    c_page = paginator.page(cur_page)

    page_range = []
    visibleNumber = 10
    min = int(cur_page - visibleNumber / 10)
    if min < 1:
        min = 1
    max = min + visibleNumber
    if max > paginator.page_range[-1]:
        max = paginator.page_range[-1]
    for i in range(min,max):
        page_range.append(i)

    return render(request,'tableData.html',{
        'userInfo':userInfo,
        'c_page':c_page,
        'page_range':page_range,
        'paginator':paginator
    })

def historyTableData(request):
    uname = request.session.get('username')
    userInfo = User.objects.get(username=uname)
    historyData = getHisotryData.getHisotryData(userInfo)
    return render(request,'historyTableData.html',{
        'userInfo':userInfo,
        'historyData':historyData
    })

def addHistory(request,jobId):
    uname = request.session.get('username')
    userInfo = User.objects.get(username=uname)
    getHisotryData.addHistory(userInfo,jobId)
    return redirect('historyTableData')

def removeHisotry(request,hisId):
    getHisotryData.removeHisotry(hisId)
    return redirect('historyTableData')

def salary(request):
    uname = request.session.get('username')
    userInfo = User.objects.get(username=uname)
    # 获取所有可选项
    educations, workExperiences = getSalaryCharData.getPageData()
    cities = JobInfo.objects.values_list('address', flat=True).distinct()
    jobs = JobInfo.objects.values_list('type', flat=True).distinct()

    # 获取筛选参数
    defaultEducation = request.GET.get('educational', '不限')
    defaultWorkExperience = request.GET.get('workExperience', '不限')
    defaultCity = request.GET.get('city', '不限')
    defaultJob = request.GET.get('job', '不限')

    # 构建筛选条件
    filter_kwargs = {}
    if defaultEducation != '不限':
        filter_kwargs['educational'] = defaultEducation
    if defaultWorkExperience != '不限':
        filter_kwargs['workExperience'] = defaultWorkExperience
    if defaultCity != '不限':
        filter_kwargs['address'] = defaultCity
    if defaultJob != '不限':
        filter_kwargs['type'] = defaultJob

    # 获取筛选后的职位数据（如需传递给前端可加到context）
    jobs_queryset = JobInfo.objects.filter(**filter_kwargs)

    # 生成图表数据（如getBarData等需支持更多参数可同步调整）
    salaryList, barData, legends = getSalaryCharData.getBarData(defaultEducation, defaultWorkExperience)
    pieData = getSalaryCharData.getSalaryCharData(defaultEducation, defaultWorkExperience)
    louDouData = getSalaryCharData.getLouDouData()

    return render(request, 'salaryChar.html', {
        'userInfo': userInfo,
        'educations': educations,
        'workExperiences': workExperiences,
        'cities': cities,
        'jobs': jobs,
        'defaultEducation': defaultEducation,
        'defaultWorkExperience': defaultWorkExperience,
        'defaultCity': defaultCity,
        'defaultJob': defaultJob,
        'salaryList': salaryList,
        'barData': barData,
        'legends': legends,
        'pieData': pieData,
        'louDouData': louDouData
    })

def company(request):
    uname = request.session.get('username')
    userInfo = User.objects.get(username=uname)
    typeList = getCompanyCharData.getPageData()
    type = 'all'
    if request.GET.get('type'):type = request.GET.get('type')
    rowBarData,columnBarData = getCompanyCharData.getCompanyBar(type)
    pieData = getCompanyCharData.getCompanyPie(type)
    companyPeople,lineData = getCompanyCharData.getCompanPeople(type)
    return render(request, 'companyChar.html', {
        'userInfo': userInfo,
        'typeList':typeList,
        "type":type,
        "rowBarData":rowBarData,
        "columnBarData":columnBarData,
        'pieData':pieData,
        "companyPeople":companyPeople,
        "lineData":lineData
    })

def companTags(request):
    uname = request.session.get('username')
    userInfo = User.objects.get(username=uname)
    return render(request, 'companyTags.html', {
        'userInfo': userInfo
    })

def educational(request):
    uname = request.session.get('username')
    userInfo = User.objects.get(username=uname)
    # 获取所有可选项
    educations, workExperiences = getSalaryCharData.getPageData()
    
    # 获取筛选参数
    defaultEducation = request.GET.get('educational', '不限')
    defaultWorkExperience = request.GET.get('workExperience', '不限')
    
    # 获取图表数据
    charDataColumnOne, charDataColumnTwo, charDataRow = getSalaryCharData.getCharData(defaultEducation, defaultWorkExperience)
    barDataColumn, barDataRow, barLegends = getSalaryCharData.getBarData(defaultEducation, defaultWorkExperience)
    
    # 获取新的图表数据
    heatmap_data, experience_categories, education_categories = getSalaryCharData.getHeatmapData(defaultEducation, defaultWorkExperience)
    boxplot_data = getSalaryCharData.getBoxplotData(defaultEducation, defaultWorkExperience)
    
    # 获取薪资分布数据
    salary_distribution = getSalaryCharData.getSalaryCharData(defaultEducation, defaultWorkExperience)
    
    # 获取年底多薪数据
    salary_months = getSalaryCharData.getLouDouData()
    
    # 获取实习生薪资数据
    intern_salary = getSalaryCharData.getInternSalaryData()
    
    return render(request, 'educationalChar.html', {
        'userInfo': userInfo,
        'educations': educations,
        'workExperiences': workExperiences,
        'defaultEducation': defaultEducation,
        'defaultWorkExperience': defaultWorkExperience,
        'charDataColumnOne': charDataColumnOne,
        'charDataColumnTwo': charDataColumnTwo,
        'charDataRow': charDataRow,
        'barDataColumn': barDataColumn,
        'barDataRow': barDataRow,
        'barLegends': barLegends,
        'heatmap_data': heatmap_data,
        'experience_categories': experience_categories,
        'education_categories': education_categories,
        'boxplot_data': boxplot_data,
        'salary_distribution': salary_distribution,
        'salary_months': salary_months,
        'intern_salary': intern_salary
    })

def companyStatus(request):
    uname = request.session.get('username')
    userInfo = User.objects.get(username=uname)
    defaultType = '不限'
    if request.GET.get('type'): defaultType = request.GET.get('type')
    typeList = getCompanyStatusCharData.getPageData()
    teachnologyRow,teachnologyColumn = getCompanyStatusCharData.getTechnologyData(defaultType)
    # 获取模拟的公司状态数据
    simulatedCompanyStatusData = getCompanyStatusCharData.generateSimulatedCompanyStatusData()
    # 原有的获取真实公司状态数据的代码，根据需要选择保留或移除
    # companyStatusData = getCompanyStatusCharData.getCompanyStatusData()

    return render(request, 'companyStatusChar.html', {
        'userInfo': userInfo,
        'typeList':typeList,
        'defaultType':defaultType,
        'teachnologyRow':teachnologyRow,
        'teachnologyColumn':teachnologyColumn,
        # 将模拟数据传递给模板
        'simulatedCompanyStatusData': simulatedCompanyStatusData,
        # 如果原有的真实数据仍需在页面其他地方使用，则保留下面一行
        # 'companyStatusData':companyStatusData
    })

def address(request):
    if request.method == 'GET':
        try:
            jobs = JobInfo.objects.all()
            company_tags_data = [job.companyTags for job in jobs]

            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            target_image_path = os.path.join(base_dir, 'static', '3.png')
            output_image_path = os.path.join(base_dir, 'static', 'companyTags_cloud.png')

            success = word_cloud_picture.get_img(company_tags_data, target_image_path, output_image_path)

            if success:
                return render(request, 'address.html')
            else:
                return render(request, 'error.html', {'error_message': '词云图片生成失败'})

        except Exception as e:
            print(f"Error in address view: {e}")
            return render(request, 'error.html', {'error_message': f'服务器内部错误: {e}'})

    else:
        return JsonResponse({
            'status':405,
            'msg':'方法不允许'
        })