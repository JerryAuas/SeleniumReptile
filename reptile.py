# author  : jerrylee
# data    : 2022/12/4
# time    : 19:52
# encoding: utf-8
import os
import re
import sys
import time
import urllib.request
import warnings
from selenium import webdriver
from concurrent.futures import ThreadPoolExecutor
import threading

hrefNameDict = dict()


def _progress(block_num, block_size, total_size):
    """回调函数
       @block_num: 已经下载的数据块
       @block_size: 数据块的大小
       @total_size: 远程文件的大小
    """
    sys.stdout.write('\r>> Downloading %s %.1f%%' % ("filename",
                                                     float(block_num * block_size) / float(total_size) * 100.0))
    sys.stdout.flush()


def getPageUrl(htmlString: str, driver, pages: int):
    """
    获取单页当中的所有a标签的url
    :param pages:
    :param htmlString: 列表页
    :param driver: 浏览器实例
    :return: 一页当中的url列表
    """
    if pages == 1:
        HrefList = []
        driver.get(htmlString)
        for i in range(1, 25):
            aPath = f'//*[@id="i_cecream"]/div/div[2]/div[2]/div/div/div/div[1]/div/div[{i}]/div/div[2]/a'
            iCecreamHref = driver.find_element_by_xpath(aPath).get_attribute('href')
            print(iCecreamHref)
            HrefList.append(iCecreamHref)
        return HrefList
    else:
        HrefList = []
        driver.get(htmlString)
        for i in range(1, 25):
            aPath = f'/html/body/div[3]/div/div[2]/div[2]/div/div/div[1]/div[{i}]/div/div[2]/a'
            while 1:
                if checkExist(driver, aPath):
                    break
            iCecreamHref = driver.find_element_by_xpath(aPath).get_attribute('href')
            print(iCecreamHref)
            HrefList.append(iCecreamHref)
        return HrefList


def getVideoUrl(keyWord: str, pages: int):
    """
    获取视频URL列表
    :param keyWord: 关键词
    :param pages: 页数
    :return: 视频真实url列表
    """
    print("------------开始获取视频URL列表----------\n")

    htmlString2 = f'https://search.bilibili.com/all?vt=55519787&keyword={keyWord}&from_source=webtop_search&spm_id_from=333" \
                      ".1007&search_source=5 '
    if pages == 1:
        Driver = webdriver.Chrome()
        print("--------开始获取第 1 页------\n")
        hrefList = getPageUrl(htmlString=htmlString2, driver=Driver, pages=pages)
        Driver.close()
        print("--------获取第 1 页成功------\n")
        return hrefList
    elif pages > 1:
        Driver = webdriver.Chrome()
        print("--------开始获取第 1 页------\n")
        hrefList = getPageUrl(htmlString=htmlString2, driver=Driver, pages=1)
        Driver.close()
        print("--------获取第 1 页成功------\n")
        for page in range(2, pages + 1):
            htmlString1 = f'https://search.bilibili.com/all?keyword={keyWord}&from_source=webtop_search&spm_id_from=333.1007" \
                                  "&search_source=5&page={page}&o=24'
            print("--------开始获取第 {} 页------\n".format(page))
            # time.sleep(3)
            Driver = webdriver.Chrome()
            tempList = getPageUrl(htmlString=htmlString1, driver=Driver, pages=pages)
            for temp in tempList:
                hrefList.append(temp)
            # if page == 24:
            #     break
            Driver.close()
            print("--------获取第 {} 页成功------\n".format(page))
        # Driver.close()
        print("--------获取第 {} 页成功------\n".format(pages))
        return hrefList
    else:
        warnings.WarningMessage(message="您输入的页数有问题！", category=Warning)


def checkExist(driver, xpath):
    """
    检查元素存在
    :param driver: 浏览前
    :param xpath: xpath
    :return:
    """
    print("---------开始检查元素是否存在----------\n")
    try:
        driver.find_element_by_xpath(xpath).get_attribute('href')
        print("---------------Exist!--------------\n")
        return True
    except Exception as e:
        print(e)
        return False


def videoDownloadLink(videoOriUrl: str, driver, _i):
    """
    获取视频真实下载链接
    :param videoOriUrl: 视频原始url
    :return:
    """
    print("--------开始获取真实地址链接------\n")

    inputXpath = f'//*[@id="url"]'
    buttonXpath = f'//*[@id="search"]'
    downloadUrl = f'/html/body/div[3]/div/form/div/div[3]/div[1]/a[1]'
    titleXpath = f'/html/body/div[3]/div/form/div/div[3]/div[1]/p'
    print(_i)
    if _i != 0:
        driver.find_element_by_xpath(inputXpath).clear()
    time.sleep(1)
    driver.find_element_by_xpath(inputXpath).send_keys(videoOriUrl)
    time.sleep(1)
    driver.find_element_by_xpath(buttonXpath).click()
    # while element2:
    #     break
    while 1:
        if checkExist(driver, downloadUrl):
            break
    element3 = driver.find_element_by_xpath(downloadUrl).get_attribute('href')
    # print(element3)
    element4 = driver.find_element_by_xpath(titleXpath).text
    # print(element4)
    element4 = re.sub(u"([^\u4e00-\u9fa5\u0030-\u0039\u0041-\u005a\u0061-\u007a])", "", element4)
    print(element4)
    hrefNameDict[element4] = element3
    print('当前字典共有 {} 项数据'.format(len(hrefNameDict)))
    _i += 1


def startDownload(parmList):
    """
    执行下载
    :param parmList:
    :param trulyUrl: 真实url
    :param savePath: 保存路径
    :return: True & False
    """
    print("-----------开始下载----------\n")
    trulyUrl = parmList[1]
    savePath = parmList[2]
    saveName = parmList[0]

    # 添加header
    opener = urllib.request.build_opener()
    opener.addheaders = [
        ('User-agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                       'Chrome/108.0.0.0 Safari/537.36')]
    urllib.request.install_opener(opener)

    # if not os.path.exists(pathLocal + savePath + '/'):
    #     os.makedirs(pathLocal + savePath)
    if urllib.request.urlretrieve(trulyUrl, f'../code/{savePath}/' + saveName + '.mp4', _progress):
        print("-----------下载 {} 完成----------\n".format(saveName))
        return True
    # else:
    #     os.makedirs(pathLocal + savePath)
    #     print("-----------创建 {} 完成----------\n".format(pathLocal + savePath))
    #     if urllib.request.urlretrieve(trulyUrl, f'../code/{savePath}/' + saveName + '.mp4', _progress):
    #         print("-----------下载 {} 完成----------\n".format(saveName))
    #         return True


def get_target(keyWord: str, page: int, saveName: str):
    """
    实际主函数
    :param keyWord:
    :param page:
    :param saveName:
    :return:
    """
    pathLocal = 'T:/大三/python程序设计实践/作业/code/'
    if not os.path.exists(pathLocal + saveName + '/'):
        print("-----------创建 {} 成功----------".format(pathLocal + saveName))
        os.makedirs(pathLocal + saveName)
    urlList = getVideoUrl(keyWord=keyWord, pages=page)
    _i = 0

    webUrl = f'https://www.fodownloader.com/bilibili-video-downloader'
    driver = webdriver.Chrome()
    driver.get(webUrl)
    for url in urlList:
        videoDownloadLink(url, driver, _i)
        time.sleep(5)
        _i += 1
        # 用以测试效果，故缩短
        # if _i == 4:
        #     break
    driver.close()

    titleNames = []
    urls = []
    print("------------------")
    for key in hrefNameDict:
        titleNames.append(key)
        urls.append(hrefNameDict[key])
    for i in urls:
        print("-----------将要下载的url如下所示----------")
        print(i)
    with ThreadPoolExecutor(max_workers=4) as pool:
        x = len(titleNames)
        i = 0
        goalPool = 0
        while i < x:
            taskList = [
                [titleNames[i], urls[i], saveName],
                [titleNames[i + 1], urls[i + 1], saveName],
                [titleNames[i + 2], urls[i + 2], saveName],
                [titleNames[i + 3], urls[+3], saveName]
            ]
            print(taskList)
            print("------------ 线程池开始工作------------")
            results = pool.map(startDownload, taskList)
            for result in results:
                if result:
                    goalPool += 1
                    if goalPool % 4 == 0:
                        i += 4
    print("Success !!!")


if __name__ == "__main__":
    keyword = input("请输入要搜索的关键词: ")
    page = int(input("请输入要爬取的页数: "))
    saveName = input("请输入要保存的文件名: ")
    get_target(keyword, page, saveName)
