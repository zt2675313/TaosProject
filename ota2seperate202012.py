# -*- coding: utf-8 -*-
'''
# 搜索所有qdss.txt 收尾的文件，提取制定指标 and ota,thermal
Sim , band ,attend rsvp, s
V1: only pdsch status
current version : ota ,(pdsch status,ssb rsrp ,CSF report using same function)

'''

import os, sys, re, time, datetime
import pandas as pd

logtime = []
### LTE L1 serving cell measurement
eleDict = {}
eleDict.setdefault('Date', [])
eleDict.setdefault('Time', [])
## NR pdsch status
pdschPD = pd.DataFrame(columns=['Timestamp', '#', 'Slot', 'Numerology', 'Frame', 'Num PDSCH Status', 'Carrier ID', 'TechID', 'OpCode', 'ConnID', \
                                'Bandwidth', 'BandType', 'Variant ID', 'PCI', 'EARFCN', 'TB Index', 'TB Size', 'SCS MU', 'MCS', 'NumRBs', \
                                'RV', 'HARQ ID', 'RNTI Type', 'K1', 'TCI', 'NUM Layer', 'iteration Index', 'CRC State', 'CRC State', 'NewTxFlag', \
                                'NDI', 'Discard Mode', 'Bypass Decode', 'Bypass Harq', 'Num ReTx', 'HD Onload Timeout', 'Harq Onload Timeout', 'HD Onload Timeout',
                                'HARQ Offload Timeout', 'DID Recomb', \
                                'IS IOVec Valid', 'Mod Type', 'High Clock Mode', 'Num RX', 'RxANT_Map0', 'RxANT_Map1', 'RxANT_Map2', 'RxANT_Map3'])
## LTE , NR OTA include mib
LTENROta = ['0xB0C0', '0xB0C1', '0xB0E2', '0xB0E3', '0xB0EC', '0xB0ED', '0xB800', '0xB801', '0xB80A', '0xB80B', '0xB814', '0xB821', '0xB822', '0xB89c', '0xB981', '0xB1E5',
            '0x156E', '0x1830', '0x1831', '0x1832', '0x3184', '0x1807', '0x2480', '0x2239']

def parseMsg(lfile):
    if os.path.isfile(lfile) == False:
        print(lfile + 'is not valide file path')
        return
    print('Start to take metrics from ' + lfile)
    fname = os.path.split(lfile)[1].replace('.txt', '')
    fp = open(lfile)
    contents = fp.readlines()
    indexlist = []
    for i, each in enumerate(contents):  # 得到所有以2020开头的行的index，消息的分割依据
        try:
            # print(each)
            fm = re.match(r'202\d.+(\d\d:\d\d:\d\d).+', each)
            if fm:
                tm = fm.group(1)
                indexlist.append(i)

        except Exception as e1:
            print(e1)
            exit
    logfolder, logfile = os.path.split(lfile)
    # write head

    ## 针对 Is Restricted             = false  这种结构，用 value是数组的方式，eleDict.setdefault函数， 左边是字段，右边是 不停添加的值，生成多个键和值，最后生成 dataframe
    for j in range(len(indexlist)):
        try:
            title = contents[indexlist[j]]
            print(title)
            tt1 = datetime.datetime.now()
            if (title.startswith('2021') or title.startswith('2020')) and len([x for x in LTENROta if x in title]) > 0 and 'Paging' not in title:  # LTE , NR ota message
                contlist = []
                for k in range(indexlist[j], indexlist[j + 1]):  # indexlist[j] is line index in contents
                    contlist.append(contents[k])
                if contlist:

                    if os.path.isdir(logfolder + os.sep + fname + '_ota') == False:
                        os.mkdir(logfolder + os.sep + fname + '_ota')
                    fname_ota = re.sub('\W', '_', title)
                    fp = open(logfolder + os.sep + fname + '_ota' + os.sep + fname_ota + '.txt', 'w')
                    fp.writelines(contlist)
                    fp.close()
        except Exception as e1:
            print(e1)
            continue


if __name__ == '__main__':
    scrptpath = os.path.dirname(os.path.realpath(__file__))
    # Filterfile = scrptpath+os.sep+'NR-LTE_Filter2-ota_nRpdsch.txt'
    #tmplate = scrptpath + os.sep + 'rsrpsnrTemplate.txt'
    if os.path.isdir(sys.argv[1]):
        print("Log path entered: " + sys.argv[1])
    else:
        print(sys.argv[1] + ' is not valid path!')
        exit(0)
        time.sleep(3)
    logpath = sys.argv[1]
    for root, dirs, fiels in os.walk(logpath):
        if 'systemlogs.logarchive' in root:
            continue
        try:
            for each in fiels:
                if each.endswith('qdss.txt') and not each.startswith('.') :
                    parseMsg(root + os.sep + each)

        except Exception as e1:
            print(e1)
            print('Something wrong at parseing ' + root + os.sep + each)
            continue

