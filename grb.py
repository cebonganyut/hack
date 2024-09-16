import bs4
from bs4 import BeautifulSoup
import requests
import os
from concurrent.futures import ThreadPoolExecutor

linux = "clear"
windows = "cls"
os.system([linux, windows][os.name == "nt"])

banner = '''insan'''.format('\033[33m')
print('insan1337 grabber')
green = '\033[32m'
print('\033[1;37m')
def cobain():
    global green
    domain_ip = input('pilih domain id,th, dan lainnya : ')
    go_page = int(input('mulai dari page : '))
    page=(go_page-1)
    end_page = int(input('akhir page : '))
    epage=(end_page+1)
    save_ip = input('save result : ')
    while True:
        page += 1
        url = 'https://www.topsitessearch.com/domains/'+domain_ip+'/'+str(page)
        Agents = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.5304.107 Safari/537.36'}
        r = requests.get(url , headers=Agents).text
        bs = BeautifulSoup(r, 'html.parser')
        try:
            find = bs.find('tbody').find_all('tr')
        except:
            pass
        stop = 'https://www.topsitessearch.com/domains/.com/'+str(epage)
        if stop in url:
            break
        else:
            for a in find:
             c = a.find('td').text
             rmv = c.replace('1','').replace('2','').replace('3','').replace('4','').replace('5','').replace('6','').replace('7','').replace('8','').replace('9','').replace('10','').replace(':','').replace('0','')
             spc_rmv = rmv.strip()
             print(f'{green}{page}{spc_rmv}')
             open(save_ip,'a').write(spc_rmv+'\n')
             print('\033[1;37m')
cobain()
        

