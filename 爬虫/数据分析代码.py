import pandas as pd
import matplotlib.pyplot as plt
plt.rcParams['font.sans-serif'] = ['SimHei']  # 解决中文乱码


def picture_one():
    """
    豆瓣电影前top250国家次数前8的柱状图。
    :return:
    """
    df = pd.read_excel('清洗后的数据.xlsx')
    lists = df.values.tolist()
    c = []
    for li in lists:
        content = li[6]
        content = content.replace('(', '')
        content = content.replace(')', '')
        c.append(content)
    Demo_list = c
    List_to_set = set(c)
    Demo_dict = {}  # 定义字典，以国家为键，国家出现的次数为值。
    for item in List_to_set:
        Demo_dict.update({item: Demo_list.count(item)})  # 更新字典中的键值对信息。进行统计每个国家出现的次数。
    print(f'统计出来之后的结果: {Demo_dict}')   # 打印统计出来之后的结果。
    key_list = []
    value_list = []
    for key, value in Demo_dict.items():
        key_list.append(key)
        value_list.append(value)
    value_list = sorted(value_list, reverse=True)  # 进行排序。
    value_list = value_list[0:8]   # 取出前 8 名的国家出现的次数。
    print(f'前 8 出现的次数排名: {value_list}')  # 打印前 8 的出现次数，查看是否有相同的次数
    name_list = []
    num_list = []
    for i in value_list:
        k2 = [k for k, v in Demo_dict.items() if v == i]
        num_list.append(i)
        name_list.append(k2[0])
    # print(name_list)
    # print(num_list)
    plt.barh(range(len(num_list)),
             num_list,
             align="center",
             # 设置标签
             tick_label=name_list, )
    plt.title('电影所在国家前八柱状图')
    plt.show()

def picture_two():
    df = pd.read_excel('清洗后的数据.xlsx')
    lists = df.values.tolist()
    labels = '评分在 9.0 以下', '评分在 9.0~9.5', '评分在 9.5 以上'    # 定义一个元组
    p1 = 0
    p2 = 0
    p3 = 0
    for li in lists:
        if li[1] < 9.0:
            p1 = p1 + 1
        elif li[1] > 9.0 and li[1] < 9.5:
            p2 = p2 + 1
        else:
            p3 = p3 + 1
    fraces = [p1, p2, p3]
    # 使画出来的图形为标准圆
    plt.axes(aspect=1)
    # 突出分离出数量最多的第二部分
    explode = [0, 0.1, 0]
    colors = ['skyblue', 'pink', 'yellow']
    plt.pie(x=fraces,
            labels=labels,
            colors=colors,
            # 显示比例
            autopct='%0f%%',
            explode=explode,
            # 显示阴影，使图形更加美观
            shadow=True)
    plt.show()

def picture_three():
    X = pd.read_excel('清洗后的数据.xlsx', usecols=[2]).values  # 读取评论数
    plt.imshow(X)
    plt.xticks(range(0, 1, 1), ['评论数'])  # 设置x轴刻度标签
    plt.colorbar()  # 显示颜色条
    plt.title('评价数统计热力图')
    plt.show()

def picture_four():
    df = pd.read_excel('清洗后的数据.xlsx')
    lists = df.values.tolist()
    data = []
    for li in lists:
        data.append(li[5])
    plt.hist(data, bins=20, facecolor="#08D9D6", alpha=0.30, rwidth=0.7)
    plt.subplots_adjust(left=0.30)
    plt.title('年份直方图')
    plt.show()

if __name__ == '__main__':
    picture_one()
    picture_two()
    picture_three()
    picture_four()