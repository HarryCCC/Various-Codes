import urllib.request
from bs4 import BeautifulSoup
import re
import xlwt



# 影片详情链接的规则
findLink = re.compile(r'<a href="(.*?)">')    # 创建正则表达式对象，表示规则
# 影片图片的链接
findImgSrc = re.compile(r'<img.*src="(.*?)"', re.S)    # re.S忽略换行符
# 影片片名
findTitle = re.compile(r'<span class="title">(.*)</span>')
# 影片评分
findRating = re.compile(r'<span class="rating_num" property="v:average">(.*)</span>')
# 评价人数
findComment = re.compile(r'<span>(\d*)人评价</span>')
# 概况
findInq = re.compile(r'<span class="inq">(.*)</span>')
# 找到影片相关内容
findBd = re.compile(r'<p class="">(.*?)</p>', re.S)



def getData(baseurl):   #baseurl指所爬网址的基本URL部分，如豆瓣https://movie.douban.com/top250?start=
    datalist = []
    for i in range(0, 10):   # 调用获取页面信息的函数
        url = baseurl+str(i * 25)   #每个页面显示25部电影，baseurl+str(i * 25)为url变量赋值所爬网页的字符串，例https://movie.douban.com/top250?start=75
        html = askURL(url)    # askURL 函数来获取指定 URL 的 HTML 源代码储存在html变量中
        soup = BeautifulSoup(html, 'html.parser')  # 把返回的html源代码，进行解析。
        # 现在，你可以使用 soup 对象来查找、提取和修改文档中的元素。
        # 例如，你可以使用 soup.title 来获取文档的标题元素，或者使用 soup.find_all('p') 来获取文档中所有的段落元素。
        for item in soup.findAll('div', class_='item'):

            data = []    # 保存每一个电影的信息
            item = str(item)  # 转换成item字符串对象

            link = re.findall(findLink,item)[0]  # 获取影片详情的超链接
            data.append(link)

            imgSrc = re.findall(findImgSrc, item)[0]      # 获取图片链接
            data.append(imgSrc)

            titles = re.findall(findTitle, item)     # 添加片名，片名可能有一个，也可能有两个
            if len(titles)==2:  #如果有两个片名
                ctitle = titles[0]          # 中文名
                data.append(ctitle)
                otitle = titles[1].replace("/", "")   # 英文名中有无关的符号/，去除
                data.append(otitle)         # 英文名other-title=otitle
            else:
                data.append(titles[0])  #否则，一个片名
                data.append(' ')    # 留空 ，因为要放到数据库

            rating = re.findall(findRating, item)[0]
            data.append(rating)                         # 评分

            commentNum = re.findall(findComment,item)[0]
            data.append(commentNum)                   # 添加评价人数

            inq = re.findall(findInq,item)
            if len(inq) != 0:
                inq=inq[0].replace("。", "")
                data.append(inq)                        # 添加概述
            else:
                data.append("无概述")

            bd = re.findall(findBd, item)[0]
            bd = re.sub('<br(\s+)?/>(\s+)?', ' ', bd)  # 去掉<br/> ; 匹配形如 <br> 或 <br/> 的标签，以及它们前后可能存在的空白字符
            bd = re.sub('/',' ',bd)    # 去掉/
            data.append(bd.strip())    # 去掉前后空格; strip() 用于删除字符串两端的空白字符。空白字符包括空格、制表符、换行符等。

            datalist.append(data)    # 将一个电影的信息放到datalist；并循环10页共250个item
    return datalist



def askURL(url):
    """
    该函数，通过参数传进来的url对该url发起一个请求，并获取服务器返回的响应response，最后把获取的响应的html数据return，返回出去。
    """
    head = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36'
    } #定义了一个字典 head，用于存储 HTTP 请求头中的 User-Agent 字段。这个字段用于告诉服务器客户端的类型，以便服务器能够返回适当的响应。
    request = urllib.request.Request(url,headers=head) #创建一个 HTTP 请求对象
    html = ""
    try:
        response=urllib.request.urlopen(request) #发送 HTTP 请求，并获取服务器返回的响应
        html=response.read().decode('utf-8') #read() 方法读取响应的内容，并使用 decode('utf-8') 方法将其解码为字符串
    except urllib.error.URLError as e: #发生异常，hasattr() 函数来检查异常对象是否包含 code 或 reason 属性。如果包含，则打印出这些属性的值。
        if hasattr(e,'code'):
            print(e.code)
        if hasattr(e,'reason'):
            print(e.reason)
    return html

# 保存信息
def saveDate(datalist, savepath):
    book = xlwt.Workbook(encoding='utf-8', style_compression=0)        # 创建工作簿对象
    sheet = book.add_sheet('豆瓣电影Top250', cell_overwrite_ok=True)   # 创建工作表，允许覆盖单元格
    col = ('电影详情链接', '图片链接', '影片中文片名', '影片外国名', '评分', '评价数', '概况', '相关信息')
    for i in range(0,8):
        sheet.write(0, i, col[i])   # 写入第一行为列名
    for i in range(0,250): #共有250部电影item
        data = datalist[i]
        for j in range(0,8): #每部电影有八项属性
            sheet.write(i+1, j, data[j])    # 第二行到第251行，第一列到第八列，写入数据
    book.save(savepath)       # 保存

# 程序入口
if __name__ == '__main__':
    baseurl = "https://movie.douban.com/top250?start="  # 定义爬取的网页根
    datalist = getData(baseurl)  # 获取数据
    savepath = "C:\\Users\\11470\\Desktop\\原始数据.xls"  # 定义保存路径
    saveDate(datalist, savepath)  # 保存数据
    print('爬取完成!')

