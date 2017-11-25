# lianjia-scrawler
+ This repo provides a tool to scrawl house info at LianJia.com and data would be stored in Mysql datatbase (Currently it also supports Sqlite and Postgres). It is easy to export to CSV or other formates. 
+ You also can [sync Mysql to Elasticsearch](https://github.com/siddontang/go-mysql-elasticsearch). In this way, you can use [kibana](https://github.com/elastic/kibana) to analyse these data.
+ This tool could collect community infomation from each region at first, then you'd like to use these communities to learn about onsale, history price, sold and rent information.
+ Please modify cookie info when this tool is blocked by lianjia due to ip traffic issue.
+ Discard config.ini and use settings.py instead

## 可视化数据分析示例:
![alt text](https://github.com/XuefengHuang/lianjia-scrawler/blob/master/screenshots/example1.png)
![alt text](https://github.com/XuefengHuang/lianjia-scrawler/blob/master/screenshots/example3.png)
![alt text](https://github.com/XuefengHuang/lianjia-scrawler/blob/master/screenshots/example2.png)

## 使用说明
+ 下载源码并安装依赖包
```
1. git clone https://github.com/XuefengHuang/lianjia-scrawler.git
2. cd lianjia-scrawler
# If you'd like not to use [virtualenv](https://virtualenv.pypa.io/en/stable/), please skip step 3 and 4.
3. virtualenv lianjia
4. source lianjia/bin/activate
5. pip install -r requirements.txt
6. python scrawl.py
```
+ 设置数据库信息以及爬取城市行政区信息（支持三种数据库格式）
```
DBENGINE = 'mysql' #ENGINE OPTIONS: mysql, sqlite3, postgresql
DBNAME = 'test'
DBUSER = 'root'
DBPASSWORD = ''
DBHOST = '127.0.0.1'
DBPORT = 3306
CITY = 'bj' # only one, shanghai=sh shenzhen=sh......
REGIONLIST = [u'chaoyang', u'xicheng'] # 只支持拼音
```

+ 运行 `python scrawl.py`! (请注释14行如果已爬取完所想要的小区信息)

+ 可以修改`scrawl.py`来只爬取在售房源信息或者成交房源信息或者租售房源信息

## 数据库信息
```
Community小区信息（id, title, link, district, bizcurcle, taglist）

Houseinfo在售房源信息（houseID, title, link, community, years, housetype, square, direction, floor, taxtype, totalPrice, unitPrice, followInfo, validdate)

Hisprice历史成交信息（houseID，totalPrice，date）

Sellinfo成交房源信息(houseID, title, link, community, years, housetype, square, direction, floor, status, source,, totalPrice, unitPrice, dealdate, updatedate)

Rentinfo租售房源信息 (houseID, title, link, region, zone, meters, other, subway, decoration, heating, price, pricepre, updatedate)

```

## 新增北京建委存放量房源信息爬虫(http://210.75.213.188/shh/portal/bjjs2016/index.aspx)
+ 代码存放在`jianwei`目录

## 爬虫代码分析
+ 开始抓取前先观察下目标页面或网站的结构，其中比较重要的是URL的结构。链家网的二手房列表页面共有100个，URL结构为http://bj.lianjia.com/ershoufang/pg9/
+ 其中bj表示城市，/ershoufang/是频道名称，pg9是页面码。我们要抓取的是北京的二手房频道，所以前面的部分不会变，属于固定部分，后面的页面码需要在1-100间变化，属于可变部分。将URL分为两部分，前面的固定部分赋值给url，后面的可变部分使用for循环。我们以根据小区名字搜索二手房出售情况为例：
```
BASE_URL = u"http://bj.lianjia.com/"
url = BASE_URL + u"ershoufang/rs" + urllib2.quote(communityname.encode('utf8')) + "/"
total_pages = misc.get_total_pages(url) //获取总页数信息
for page in range(total_pages):
    if page > 0:
        url_page = BASE_URL + u"ershoufang/pg%drs%s/" % (page+1, urllib2.quote(communityname.encode('utf8')))

//获取总页数信息代码
def get_total_pages(url):
    source_code = get_source_code(url)
    soup = BeautifulSoup(source_code, 'lxml')
    total_pages = 0
    try:
        page_info = soup.find('div',{'class':'page-box house-lst-page-box'})
    except AttributeError as e:
        page_info = None

    if page_info == None:
        return None
    page_info_str = page_info.get('page-data').split(',')[0]  #'{"totalPage":5,"curPage":1}'
    total_pages = int(page_info_str.split(':')[1])
    return total_pages
```

+ 页面抓取完成后无法直接阅读和进行数据提取，还需要进行页面解析。我们使用BeautifulSoup对页面进行解析。
```
soup = BeautifulSoup(source_code, 'lxml')
nameList = soup.findAll("li", {"class":"clear"})
```

+ 完成页面解析后就可以对页面中的关键信息进行提取了。下面我们分别对房源各个信息进行提取。
```
for name in nameList: # per house loop
    i = i + 1
    info_dict = {}
    try:
        housetitle = name.find("div", {"class":"title"})
        info_dict.update({u'title':housetitle.get_text().strip()})
        info_dict.update({u'link':housetitle.a.get('href')})

        houseaddr = name.find("div", {"class":"address"})
        info = houseaddr.div.get_text().split('|')
        info_dict.update({u'community':info[0].strip()})
        info_dict.update({u'housetype':info[1].strip()})
        info_dict.update({u'square':info[2].strip()})
        info_dict.update({u'direction':info[3].strip()})

        housefloor = name.find("div", {"class":"flood"})
        floor_all = housefloor.div.get_text().split('-')[0].strip().split(' ')
        info_dict.update({u'floor':floor_all[0].strip()})
        info_dict.update({u'years':floor_all[-1].strip()})

        followInfo = name.find("div", {"class":"followInfo"})
        info_dict.update({u'followInfo':followInfo.get_text()})

        tax = name.find("div", {"class":"tag"})
        info_dict.update({u'taxtype':tax.get_text().strip()})

        totalPrice = name.find("div", {"class":"totalPrice"})
        info_dict.update({u'totalPrice':int(totalPrice.span.get_text())})

        unitPrice = name.find("div", {"class":"unitPrice"})
        info_dict.update({u'unitPrice':int(unitPrice.get('data-price'))})
        info_dict.update({u'houseID':unitPrice.get('data-hid')})
    except:
        continue
```

+ 提取完后，为了之后数据分析，要存进之前配置的数据库中。
```
model.Houseinfo.insert(**info_dict).upsert().execute()
model.Hisprice.insert(houseID=info_dict['houseID'], totalPrice=info_dict['totalPrice']).upsert().execute()
```
