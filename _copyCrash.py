import os,sys
import json
import csv

def read_json(folder = '.'):
    crashpath = '/Users/taozeng/Desktop/tmpCrash/'
    for root, folders, files in os.walk(folder):

                #if 'DiagnosticLogs' in root
                for fname in files:
                    try:
                        if fname.endswith('.json'):
                            fp = open(os.path.join(root, fname)).read()
                            data = json.loads(fp)
                            print root +' file:' + fname
                            log_info = data.get('Log Dump Information')

                            '''
                                                if log_info != None and len(log_info) > 6:
                                if 'ARI_TIMEOUT' in log_info['Dump Reason']:
                                    os.rename(root + '/' + fname, root + '/' + fname + '_ARI_TIMEOUT_BBCrash.json')
                                    crashfile = root + '/' + fname.split()[0]  #only the first part
                                    trmpcpstr=  tmpstr='cp -rf ' + crashfile +'* ' + crashpath
                                    os.system(trmpcpstr)
                                if log_info['Baseband Crash Reason'] == '':
                                    continue
                                else:
                                    if '_BBCrash' not in fname and 'crash' not in  fname:
                                        os.rename(root+'/'+fname,root+'/'+fname+'_BBCrash.json')
                                        crashfile = root + '/' + fname.split()[0]  # only the first part
                                        trmpcpstr = tmpstr = 'cp -rf ' + crashfile + '* ' + crashpath
                                        os.system(trmpcpstr)
                            '''

                    except Exception as e:
                        print(e)
                        continue



if __name__ == '__main__':
    log_dir = sys.argv[1]
    if not (os.path.isdir(log_dir)):
        print "No dir inputed \n"
        os._exit(-1)
    read_json(log_dir)
    pass