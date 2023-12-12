# coding:utf-8
import pandas as pd
import re
# 解决数据输出时列名不对齐的问题
pd.set_option('display.unicode.east_asian_width', True)


L = []
# 定义清洗之后数据的列标签
columns = ['Name', 'Score', 'Comment_num', 'Director', 'Actor', 'Year', 'Country', 'Type', 'detail', 'picture']
L.append(columns)
data = pd.read_excel('原始数据.xls')   # 读取原始数据
lists = data.values.tolist()  # 转变成二维列表
for list in lists:
    detail = list[0]
    picture = list[1]
    name = list[2]  # 电影名
    score = list[4] # 电影评分
    comment_num = list[5]  # 电影评论数
    s = list[7].split(' ')
    director = s[1]  # 导演
    year_g = re.search(r'[0-9]+', list[7])
    year = year_g.group(0)  # 年份
    m = list[7].split('...')  # 关键分割
    mm = m[0].split('主演:')
    if len(mm) == 2:
        actor = mm[1]  # 主演
    elif len(mm) == 1:
        actor = '无数据'
    p = list[7].split(year)
    c_and_type = p[1]
    c_and_type.strip()
    q = c_and_type.replace('\xa0', '')
    q = q.strip()
    l = q.split(' ')
    country = l[0]   # 国家
    type = l[1:]
    type = ' '.join(type) # 类型
    l = [name, score, comment_num, director, actor, year, country, type, detail, picture]
    L.append(l)

# 利用DataFrame数据对象的to_excel()方法将数据写入到“清洗后的数据.xlsx”的excel文件之中。
df = pd.DataFrame(data=L[1:], columns=L[0])
df.to_excel('清洗后的数据.xlsx', index=False)
print('数据清洗完成!')




