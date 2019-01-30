# -*- coding: utf-8 -*-
import scrapy
import urllib.request
import re
import random
from jdgoods.items import JdgoodsItem
from scrapy.http import Request
import time

class GoodSpider(scrapy.Spider):
    name = 'good'
    allowed_domains = ['jd.com']
    # start_urls = ['http://jd.com/']

    def start_requests(self):

        ua = ["Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.87 Safari/537.36",
              "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.101 Safari/537.36",
              "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.80 Safari/537.36 Core/1.47.277.400"]

        """
        req1 = urllib.request.Request("https://book.jd.com/")
        req1.add_header("User-Agent",random.choice(ua))
        allpddata=urllib.request.urlopen(req1).read().decode("utf-8","ignore")
        pat1 = 'title.*?"URL":"(.*?)","YFLAG":"1"}],'
        allpd = re.compile(pat1).findall(allpddata)

        # 对各个新闻链接的url进行格式处理
        for i in range(0, len(allpd)):
            allpd[i] = re.sub("\\\/","/",allpd[i])
            print(allpd[i])

        catall=[]
        for i in allpd:
            thispd = "https:" + i
            print("当前测试的网址是：%s" % thispd)
            req2 = urllib.request.Request(thispd)
            req2.add_header("User-Agent", random.choice(ua))
            pddata = urllib.request.urlopen(req2).read().decode("utf-8", "ignore")
            # print(len(pddata))
        """

        allpd = ["https://channel.jd.com/p_wenxuezongheguan.html",
                 "https://channel.jd.com/1713-3267.html",
                 "https://book.jd.com/library/socialscience.html"]

        # 存放所有的频道id
        catall = []

        for thispd in allpd:
            print("当前测试的网址是：%s" % thispd)
            req2 = urllib.request.Request(thispd)
            req2.add_header("User-Agent", random.choice(ua))
            pddata = urllib.request.urlopen(req2).read().decode("utf-8", "ignore")
            # print("这个馆的数据是 %d" % len(pddata))
            pat2 = 'href="..list.jd.com.list.html.cat=([0-9,]*?)[&"]'
            catdata = re.compile(pat2).findall(pddata)
            # print(catdata)
            for j in catdata:
                catall.append(j)


        #去重的两种方法：布隆过滤器和数据库约束
        #简单的数据可以使用集合去重
        catall2 = set(catall)
        print("去重后的数据有%d个" % len(catall2))

        #获得总页数,每一页对应一个网址
        allurl = []  #[{"cat":"pagenum"}]
        x=0
        for m in catall2:
            thispdnum = m
            req3 = urllib.request.Request("https://list.jd.com/list.html?cat=" + thispdnum)
            req3.add_header("User-Agent", random.choice(ua))
            listdata = urllib.request.urlopen(req3).read().decode("utf-8", "ignore")
            pat3 = '<em>共<b>(.*?)</b>页'
            allpage=re.compile(pat3).findall(listdata)
            if len(allpage) > 0:
                pass
            else:
                allpage = [1]
            allurl.append({thispdnum: allpage[0]})

            #为了测试
            if x>2:
                break
            x += 1



        x=0
        for n in catall2:
            thispage = allurl[x][n]
            for p in range(1,int(thispage)+1):
                thispageurl = "https://list.jd.com/list.html?cat=" + str(n) + "&page=" + str(p)
                print("当前要ppp爬的网站 %s" % thispageurl)
                yield Request(thispageurl,callback=self.parse)
            x += 1

    def parse(self, response):

        item = JdgoodsItem()
        listdata = response.body.decode("utf-8", "ignore")
        # 频道1、2
        pd = response.xpath("//span[@class='curr']/text()").extract()
        if (len(pd) == 0):
            pd = ["缺省", "缺省"]
        if (len(pd) == 1):
            pda = pd[0]
            pd = [pda, "缺省"]
        pd1 = pd[0]
        pd2 = pd[1]
        print(pd1)
        # 图书名(从下标为3的地方开始取)
        bookname = response.xpath("//div[@class='p-name']/a/em/text()").extract()
        print(bookname[0])
        # 价格https://p.3.cn/prices/mgets?callback=jQuery5975516&type=1&skuIds=J_10924526
        allskupat = '<a data-sku="(.*?)"'
        allsku = re.compile(allskupat).findall(listdata)
        # print(allsku)
        # 评论数https://club.jd.com/comment/productCommentSummaries.action?my=pinglun&referenceIds=10650505&callback=jQuery599131
        # 作者
        author = response.xpath("//span[@class='author_type_1']/a/@title").extract()
        # 出版社
        pub = response.xpath("//span[@class='p-bi-store']/a/@title").extract()
        # 店家
        seller = response.xpath("//span[@class='curr-shop']/text()").extract()
        # 处理当前页的数据
        for n in range(0, len(seller)):
            name = bookname[n + 3]
            thissku = allsku[n]
            priceurl = "https://p.3.cn/prices/mgets?callback=jQuery8271929&skuIds=J_" + str(thissku)
            pricedata = urllib.request.urlopen(priceurl).read().decode("utf-8", "ignore")
            pricepat = '"p":"(.*?)"'
            price = re.compile(pricepat).findall(pricedata)[0]
            pnumurl = "https://club.jd.com/comment/productCommentSummaries.action?my=pinglun&referenceIds=" + str(thissku)
            pnumdata = urllib.request.urlopen(pnumurl).read().decode("utf-8", "ignore")
            pnumpat = '"CommentCount":(.*?),'
            pnum = re.compile(pnumpat,re.S).findall(pnumdata)[0]
            thisauthor = author[n]
            # print(author)
            thispub = pub[n]
            thisseller = seller[n]

            print(pd1)
            print(pd2)
            print(name)
            print(price)
            print(pnum)
            print(thisauthor)
            print(thispub)
            print(thisseller)
            item["pd1"] = pd1
            item["pd2"] = pd2
            item["name"] = name
            item["price"] = price
            item["pnum"] = pnum
            item["author"] = thisauthor
            item["pub"] = thispub
            item["seller"] = thisseller
            yield item

"""
根据频道号构建网址
"""

"""
爬取的思路：
1.爬取book.jd.com，找出所有图书分类（什么什么馆）的地址
2.依次爬取各个馆，在馆中得到相应的所有频道id
"""


"""
        listdata = response.body.decode("utf-8", "ignore")

        # 获取频道1 ，2
        pd = response.xpath("//span[@class='curr']/text()").extract()
        if len(pd) == 0:
            pd = ["缺失","缺失"]
        if len(pd) == 1:
            pd.append("缺失")

        pd1 = pd[0]
        pd2 = pd[1]
        print("标题 %s" % pd1)
        print(pd2)

        # 图书名
        bookname = response.xpath('//div[@ class="p-name]/a/em/text()').extract()
        print(bookname[0])

        #价格
        # https://p.3.cn/prices/mgets?callback=jQuery8271929&skuIds=J_11537963
        allskupat = '<a data-sku="(.*?)"'
        allsku = re.compile(allskupat).findall(listdata)
        print(allsku)

        #评论数
        # https://club.jd.com/comment/productCommentSummaries.action?my=pinglun&referenceIds=11537963

        #作者
        author = response.xpath("//span[@class='author_type_1']/a/@title").extract()
        #出版社
        pub = response.xpath("//span[@class='p-bi-store']/a/@title").extract()
        #店家
        seller = response.xpath("//span[@class='curr - shop']/text()").extract()

        #处理当前页面的数据
        for n in range(0,len(seller)):
            name = bookname[n]
            thissku = allsku[n]
            priceurl = "https://p.3.cn/prices/mgets?callback=jQuery8271929&skuIds=J_" + str(thissku)
            pricedata = urllib.request.urlopen(priceurl).read().decode("utf-8","ignore")
            pricepat = '"p":"(.*?)"'
            price = re.compile(pricepat).findall(pricedata)[0]

            pnumeurl = "https://club.jd.com/comment/productCommentSummaries.action?my=pinglun&referenceIds=" + str(thissku)
            pnumdata = urllib.request.urlopen(pnumeurl).read().decode("utf-8","ignore")
            pnumpat = '"CommentCountStr":"(.*?)'
            pnum = re.compile(pnumpat).findall(pnumdata)[0]
            # thisauthor = author[n]
            print(author)
            # thispub = pub[n]
            # thisseller = seller[n]
            print(pub)
            print(seller)


            print("书名%" % name)
            print(price)
            print(pnum)
            print("循环中标题 %s" % pd1)
            # print(thisauthor)
            # print(thispub)
            # print(thisseller)
"""

