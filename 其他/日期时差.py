from datetime import datetime
from dateutil.relativedelta import relativedelta

# 硬编码的日期
old_date = datetime(2001, 9, 5)
new_date = datetime(2024, 5, 3)

# 计算日期差异
delta = relativedelta(new_date, old_date)

# 提取年、月、日
years = delta.years
months = delta.months
days = delta.days

# 打印详细的日期差异
print(f"The difference is {years} years, {months} months, and {days} days.")

# 计算总天数、月数和年数的估计
# 一年按365.25天计算，一个月按30.44天计算
total_days = (new_date - old_date).days
total_months = total_days / 30.44
total_years = total_days / 365.25

# 打印总天数、月数和年数
print(f"Total days between dates: {total_days} days")
print(f"Total months between dates: {total_months:.2f} months")
print(f"Total years between dates: {total_years:.2f} years")