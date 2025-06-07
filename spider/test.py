salaries = '100-150元/天'.split('·')
salary = list(map(lambda x: int(x), salaries[0].replace('元/天', '').split('-')))

print(salary)