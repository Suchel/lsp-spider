#!/usr/bin/python
# -*- coding:utf-8 -*-
"""
__auth__ = fuyouduhai
__date__ = 2021/7/19
__soft__ = PyCharm
"""
import os
import platform
import tempfile
import time

import requests
from fake_useragent import UserAgent
from lxml import etree

# 获取当前操作系统
operation_system = platform.system().lower()
# 获取当前系统临时目录绝对路径
tempdir = tempfile.gettempdir()
# 获取项目目录的绝对路径
current_dir = os.path.dirname(os.path.abspath(__file__))
# fake-useragent的json文件，缺少该文件在使用时会报错，该文件应该位于临时目录内
fu_file = 'fake_useragent_0.1.11.json'
# 配置fake-useragent文件应在的绝对路径，即临时目录绝对路径+文件名称
fu_file_path = os.path.join(tempdir, fu_file)
# 拼接当前json文件绝对路径
this_fu_file = os.path.join(current_dir, fu_file)

# 判断临时目录是否存在json文件，如果不存在，则根据相应操作系统执行命令拷贝文件到临时目录
# 暂不考虑windows，linux以及macos以外的系统
if os.path.exists(fu_file_path):
    print('恭喜，文件已存在，请等待')
else:
    if operation_system == 'windows':
        os.popen(f'copy {this_fu_file} {tempdir}')
    else:
        os.system(f'cp {this_fu_file} {tempdir}')

# 设置请求headers，需要手动访问https://imoemei.com/，然后F12，获取cookie，填入自己的cookie，如果
# 不了解，可以请叫度娘。
headers = {
    'cookie': 'Hm_lvt_dfe895979d782c8636398ef8a5fef959=1626659466; wordpress_test_cookie=WP+Cookie+check; Hm_lpvt_dfe895979d782c8636398ef8a5fef959=1626665540',
    'referer': 'https://imoemei.com/',
    'user-agent': str(UserAgent().random)
}


# 首次请求，获取总索引情况
def get_index(page_index):
    request_url = 'https://imoemei.com/wp-json/b2/v1/getModulePostList'
    data = {
        'index': 1,
        'post_paged': page_index
    }
    response = requests.post(request_url, headers=headers, data=data)
    return response


if __name__ == '__main__':
    # 假设当前页数和总页数都为1
    page = total_pages = 1
    # 列表下标索引，初始为0，没什么好讲的
    index = 0
    # 当页数小于等于总页数时，循环执行。 目的是自动爬取所有内容
    while page <= total_pages:
        # 测试，打印当前进行到第几页
        print(f'当前准备爬取第{page}页')
        # 首次请求默认为第一页，获取第一页响应对象
        resp = get_index(page)
        # page+1，表示下次循环时爬取下一页内容
        page += 1
        # 获取总页数
        total_pages = resp.json()['pages']
        # 获取返回状态
        if resp.status_code == requests.codes.ok:
            # 用etree解析页面内容
            html_data = etree.HTML(resp.json()['data'])
            # 二级页面链接
            next_list = html_data.xpath('//div[@class="post-module-thumb"]//a/@href')
            # 头像
            title_list = html_data.xpath("//div[@class='post-info']/h2/a/text()")
            # 标题
            photo_list = html_data.xpath('//div[@class="post-module-thumb"]//img/@src')
            # 遍历小图（理解为索引图）和标题，原文中有爬取小图，我考虑后删除了，不清晰，没什么用
            for pic, name in zip(photo_list, title_list):
                # 自动根据标题创文件夹，防止图片爬取错乱，找不到想要的
                if name not in os.listdir(path=os.getcwd()):
                    os.mkdir(name)
                    print('创建文件夹{}成功'.format(name))
                # 就是这里删除了保存小图的代码，想要的自己去公众号补上吧

                # 索引+1，循环创建page页所有的标题目录
                index += 1
            # 这里是解析页面内容获取连接和标题后，访问标题详情连接，爬取detail图片
            # ，代码极其易懂，不多注释了
            for url, name in zip(next_list, title_list):
                # 判断文件夹是否存在
                if not os.path.exists(name):
                    os.mkdir(name)
                resp = requests.get(url, headers=headers)
                html_data = etree.HTML(resp.text)
                pic_links = html_data.xpath("//div[@class='entry-content']/p/img/@src")
                count = 1
                for pic in pic_links:
                    r = requests.get(pic).content
                    print(f'当前 {name} {count}')
                    try:
                        with open('./{}/{}.jpg'.format(name, count), 'wb') as fin:
                            print(f'正在爬取{name}第{count}张图片!!!!')
                            fin.write(r)
                            print('{}{}.jpg----下载成功'.format(name, count))
                            # 休眠0.1秒，防止过快爬取导致网络错误
                            time.sleep(0.1)
                    except Exception as e:
                        print(e.__repr__())
                        print('下载失败！！！！！')
                        continue
                    count += 1
        print(f'{page}页所有爬取完成！')
