import os,sys,re
import datetime
import time
import json
from ftplib import FTP
from multiprocessing import Pool



def convert(file_name):
    
    output_dir, __ = os.path.split(file_name)
    filter_file = output_dir + '/filter.txt'
    print(file_name)
    command = '/Applications/Qualcomm/QCAT/QCAT.app/Contents/MacOS/QCAT -txt  -export -property="Timestamp Location":Local -property="Show Hex Dump":false -property="Use PC Time":false  -filter=' + filter_file + r' -outputdir='+output_dir + ' '+file_name
    os.system(command)

def download_qsr4file(json_file):
    fp = open(os.path.join(json_file)).read()
    data = json.loads(fp)
    BB_version = data.get('ABM Common Information')['Baseband Version']
    print('Current BB_version', BB_version)
    
    #connect to Shanghai Server to download qsr4 file 
    ftpclient = FTP()
    ftpclient.connect('17.88.51.123')
    ftpclient.login('FTServer','Freedom')
    
    filelist = []
    ftpclient.cwd('BB_Release/Mav20_BB/Mav20-'+ BB_version)
    ftpclient.retrlines('LIST', filelist.append)

    for file_name in filelist:
        if file_name.endswith('qsr4'):
            qsr4_file = file_name.split(' ')[-1]
            remote_file = ftpclient.pwd() + '/' + qsr4_file
    
    local_file = r'/Users/intern/Documents/QCAT/QShrink/' + qsr4_file

    if os.path.exists(local_file):
        pass
    else:
        print('Download BB_version', BB_version)
        try:
            buf_size = 1024
            file_handler = open(local_file, 'wb')
            ftpclient.retrbinary('RETR %s' % remote_file, file_handler.write, buf_size)
            file_handler.close()
        except Exception as err:
            print(err)
#by Tao 202012
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
            fm = re.match(r'2020.+(\d\d:\d\d:\d\d).+', each)
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
            if title.startswith('2020') and len([x for x in LTENROta if x in title]) > 0 and 'Paging' not in title:  # LTE , NR ota message
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
    qdsspath=''
    if os.path.isdir(sys.argv[1]):
        print("Log path entered: " + sys.argv[1])
        qdsspath=sys.argv[1]

    else:
        print(sys.argv[1] + ' is not valid log folder!')
        exit(0)
    os.chdir(qdsspath)
    packets = [
                '0xB0C0', '0xB0C1', '0xB0E2', '0xB0E3', '0xB0EC', '0xB0ED', '0xB800', '0xB801', '0xB80A', '0xB80B', '0xB814', '0xB821', '0xB822', '0xB89c', '0xB981', '0xB1E5',
            '0x156E', '0x1830', '0x1831', '0x1832', '0x3184', '0x1807', '0x2480', '0x2239'
               ]
    
    path_list = [
                qdsspath
                ]

    start_time = time.time()
    for path in path_list:
        log_list = []

        for root, folders, files in os.walk(path):
            for f in files:
                if f.endswith('hdf') and 'BEFORE' not in root and 'Iter-0' not in root:
                    # if os.path.exists(os.path.join(root, f[0:-4] + '.txt')):
                        # pass
                    # else:
                    full_path = os.path.abspath(os.path.join(root, f))
                    log_list.append(full_path)
        
        for root, folders, files in os.walk(path):
            for f in files:
                if f.endswith('json'):
                     json_file = root + '/' + f
                     download_qsr4file(json_file)
                     
        print(len(log_list))
        for file_name in log_list:
            output_dir, __ = os.path.split(file_name)
            
            filter_file = output_dir + '/filter.txt'
            
            with open(filter_file, 'w') as outputtxt:
                print('0', file=outputtxt)
                for item in packets:
                    print(int(item, 16), file=outputtxt)
                print('-1', file=outputtxt)
        
        start_time = time.time()
        print('start processing:', datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'))
        
        pool = Pool(processes=8)
        pool.map(convert, log_list)
        
        print(len(log_list))
        print('end processing:', datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'), time.time() - start_time)

        #add by Tao 202012
        logpath=path
        for root, dirs, fiels in os.walk(logpath):
            if 'systemlogs.logarchive' in root:
                continue
            try:
                for each in fiels:
                    if each.endswith('qdss.txt'):
                        parseMsg(root + os.sep + each)

            except Exception as e1:
                print(e1)
                print('Something wrong at parseing ' + root + os.sep + each)
                continue

    

            

  