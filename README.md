# 智联招聘数据可视化分析系统

## 项目简介
这是一个基于 Django 框架开发的 Boss 直聘数据可视化分析系统，用于分析和展示招聘市场的数据趋势和洞察。

## 技术栈
- 后端：Django
- 数据库：SQLite
- 前端：HTML, CSS, JavaScript
- 数据可视化：ECharts
- 数据采集：Python爬虫

## 主要功能
1. 数据采集
   - 自动爬取 Boss 直聘招聘数据
   - 数据清洗和预处理
   - 数据存储和管理

2. 数据可视化
   - 职位分布分析
   - 薪资水平分析
   - 技能要求分析
   - 公司规模分析
   - 行业趋势分析

3. 数据分析
   - 多维度数据统计
   - 趋势分析
   - 对比分析
   - 预测分析

## 项目结构
```
├── myApp/                # Django 应用主目录
├── spider/              # 爬虫模块
├── static/              # 静态资源文件
├── templates/           # HTML 模板
├── media/              # 媒体文件
├── middleware/         # 中间件
├── import_data.py      # 数据导入脚本
├── requirements.txt    # 项目依赖
└── manage.py           # Django 管理脚本
```

## 安装和使用
1. 环境要求
   - Python 3.8+
   - pip

2. 安装步骤
   ```bash
   # 创建虚拟环境
   python -m venv venv
   
   # 激活虚拟环境
   # Windows:
   venv\Scripts\activate
   # Linux/Mac:
   source venv/bin/activate
   
   # 安装依赖
   pip install -r requirements.txt
   
   # 初始化数据库
   python manage.py migrate
   
   # 运行开发服务器
   python manage.py runserver
   ```

3. 访问系统
   - 打开浏览器访问 http://localhost:8000

## 数据更新
1. 自动更新
   - 系统支持定时自动更新数据
   - 可通过配置调整更新频率

2. 手动更新
   - 使用数据导入脚本更新数据
   ```bash
   python import_data.py
   ```

## 注意事项
1. 请确保数据库有足够的存储空间
2. 定期备份重要数据
3. 遵守网站爬虫协议和规则

## 开发计划
- [ ] 优化数据采集效率
- [ ] 增加更多可视化图表
- [ ] 添加数据导出功能
- [ ] 优化用户界面
- [ ] 增加数据分析报告功能

## 贡献指南
欢迎提交 Issue 和 Pull Request 来帮助改进项目。

## 许可证
MIT License 