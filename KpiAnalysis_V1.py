# -*- coding: utf-8 -*-
'''
 读取kpi CSV , 进行分析
 用法， python scrpt +path
'''

import os,sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from numpy.random import randn

# 从各种csv 中获取清洗后的关键值，如msc，rsrp，snr，cqi 的关系 （msc 映射到R*QAM）
def getMestric(csvname,flag):
    pd1 = pd.read_csv(csvname)
    pd1.drop_duplicates()  # 去重复
    pd1.dropna(how='all')  #去NA
    pd1.drop([0], inplace=True) # 去掉第一行
    pd1.rename(columns=lambda x: x.replace('"', '').strip(), inplace=True)
    #flag='rsrp_csv'
    if flag=='rsrp_csv':  # handle RSRP csv

        pd1 = pd1[['timestamp', 'serving_ssb', 'serving_cell_pci', 'pci', 'cell_quality_rsrp','subscription_id']]
        #pd1 = pd1[~pd1['cell_quality_rsrp'].str.contains('N')] # 仅保留有数字的记录 , 这里不能用\N, \是特殊字符，～ 表示取非 pass
        pd1 = pd1[pd1['cell_quality_rsrp'].str.contains(r'-\d+\.*\d*',regex=True)] #用正则 筛选出数据， -\d+\.*\d* 对应如 -90.56
        pd1 = pd1[pd1['serving_cell_pci']==pd1['pci']]
        del pd1['pci']
        pass
    elif flag=='snr_csv':
        pd1 = pd1[['timestamp','subscription_id' , 'rx0_ftl_snr', 'rx1_ftl_snr']]
        pd1['snr']=(pd1['rx0_ftl_snr']+pd1['rx1_ftl_snr'])/2
        #print(pd1.head(10))
        pass
    elif flag=='pdsch_csv':
        pd1 = pd1[['timestamp','subscription_id' , 'tb_size', 'mcs','num_rbs']]
        #print(pd1.head(10))
        pass
    return pd1

if __name__ == '__main__':
    if os.path.isdir(sys.argv[1]):
        print("Log path entered: " + sys.argv[1])
        csvpath=sys.argv[1]

    else:
        print(sys.argv[1] + ' is not valid path!')
        exit(0)
    os.chdir(csvpath)
    listfiles=os.listdir(csvpath)

    for each1 in listfiles:
        if each1.endswith('NR5G_RSRP.csv'):
            csvfileRsrp=csvpath+os.sep+each1
            continue
        elif each1.endswith('NR5G_SNR.csv'):
            csvfileSNR=csvpath+os.sep+each1
            continue
        elif each1.endswith('NR5G_MAC_PDSCH_Status.csv'):
            csvfilePDSCHstatus=csvpath+os.sep+each1
            continue

    pdrsrp=getMestric(csvfileRsrp,'rsrp_csv').copy()
    pdsnr=getMestric(csvfileSNR,'snr_csv').copy()
    pdpdsch=getMestric(csvfilePDSCHstatus,'pdsch_csv').copy()

    pdm=pd.merge(pdrsrp,pdsnr,how='outer',on='timestamp',sort=True)


    pdm['cell_quality_rsrp'] = pdm['cell_quality_rsrp'].astype('float')
    pdm['snr'] = pdm['snr'].astype('float')
    pdm['rx0_ftl_snr'] = pdm['rx0_ftl_snr'].astype('float')
    pdm['rx1_ftl_snr'] = pdm['rx1_ftl_snr'].astype('float')

    pdm=pd.merge(pdm,pdpdsch,how='outer',on='timestamp',sort=True)
    pdm[['serving_cell_pci', 'serving_ssb', 'subscription_id_x', 'subscription_id_y','subscription_id']] = pdm[['serving_cell_pci', 'serving_ssb', 'subscription_id_x', 'subscription_id_y','subscription_id']].fillna(method='bfill')
    pdm[['serving_cell_pci', 'serving_ssb', 'subscription_id_x', 'subscription_id_y', 'subscription_id']] = pdm[
        ['serving_cell_pci', 'serving_ssb', 'subscription_id_x', 'subscription_id_y', 'subscription_id']].fillna(method='ffill')
    # 重要： 从数据记录看，pdsch几乎是1ms就一次上报，但rsrp,snr..是几十号码才上报一次，二者记录正好交错，对rsrp,snr进行插值，删除没有msc调度的记录
    pdm[['cell_quality_rsrp', 'rx0_ftl_snr', 'rx1_ftl_snr', 'snr']]=pdm[['cell_quality_rsrp','rx0_ftl_snr','rx1_ftl_snr','snr']].interpolate()

    #pdm.dropna(axis=1,how='any',inplace=True) # 删除全空的列
    pdm.dropna(how='any',inplace=True)
    pdm['snr'] = pdm['snr'].astype('int')
    pdm['mcs'] = pdm['mcs'].astype('int')
    pdm = pdm.reset_index(drop=True)
    snr_msc=pdm[['snr', 'mcs']]
    try:
        os.mkdir('./result')
    except Exception as e1:
        print(e1)



   # 在一个画布上，画出rsrp ， snr和msc的箱体图，并保存
    np.random.seed(19680801)
    data = np.random.randn(2, 100)
    fig, axs = plt.subplots(2, 2)
    axs[0, 0].boxplot(pdm['cell_quality_rsrp'])
    axs[0, 0].set_title('rsrp')
    axs[1, 0].boxplot(pdm['snr'])
    axs[1, 0].set_title('snr')
    axs[0, 1].boxplot(pdm['mcs'])
    axs[0, 1].set_title('mcs')
    #axs[1, 1].xcorr(pdm['snr'],pdm['mcs'])
    plt.show()


    pass

    #进行snr和msc 对应统计
    pd.pivot_table(snr_msc, index=['snr', 'mcs'],values=['mcs'],aggfunc=np.count_nonzero).to_csv('./result/pivot.csv')
    pdpivot1= pd.read_csv('./result/pivot.csv')
    pdpivot1.rename(columns={'0':'freq'}, inplace = True)
    pdpivot1['sum']=pdpivot1['mcs']*pdpivot1['freq']
    grouped = pdpivot1.groupby('snr')
    smlst=[[]]

    for snrvalue, group in grouped:
        group=group[group['mcs']<29]  #大于28的msc是重发的
        avgmsc=round(group['sum'].agg(np.sum)/group['freq'].agg(np.sum),1) #得到每个snr的加权平均msc
        smlst.append([snrvalue,avgmsc,group['sum'].agg(np.sum)])
    print(smlst)

   #下面时绘制 snr和 msc对应关系的，带泡泡的散点图
    pd_sm=pd.DataFrame(smlst,columns=['snr','avgmsc','samples'])
    pd_sm['samples']=(pd_sm['samples']/pd_sm['samples'].max())*100     #定义散点的大小，以最大样本数为1，在msc和snr值范围内恰当的表达出来
    pd_sm.plot.scatter(x='snr', y='avgmsc',s=pd_sm['samples'])  #使用散点泡泡图看出了了不同snr下msc 均值以及其大小（说明参考意义是否大）





    pdm.to_csv('./result/RSRP_SNR_PDSCH.csv')
    pdm.corr().to_csv('./result/corr.csv')

    picture= pdm[['mcs','snr']].plot.hist(bins=100,alpha=0.5) # alpha是透明度
    fig = picture.get_figure()
    fig.savefig('./fig.png')
    pdm.plot.scatter(x='snr', y='mcs') # alpha是透明度
    pass


