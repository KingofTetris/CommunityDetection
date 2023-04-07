#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import datetime
import based_CDME_GTCD
import GTCD_zhijieqinmidu
import GTCD_jiarubuxianglinshequ
import GTCD_修改亲密度计算公式v2
import based_CDME_GTCD_test
import based_CDME_GTCD_改成shuffle
import based_CDME_GTCD_先合作再非合作
import based_CDME_GTCD_overlapping
if __name__ == '__main__':
    # "Input: a dataset name "
    #真实数据集
    # fnamelist = ["karate", "dolphins", 'football', 'polblogs', 'polbooks']
    # fnamelist = ["dolphins"]
    # fnamelist = ['karate']
    #人工数据集
    fnamelist = ["10","20","30","40","50","60","70","80"]
    # fnamelist = ["10"]
    #处理类型 1真实
    # datasetType = 1
    # 2人工
    datasetType = 2
    for fname in fnamelist:
        dirpath = '.'
        nodenum = 10000
        if os.path.isdir(dirpath):
            "Set a output folder"
            outdirpath = dirpath + "/output"
            if not os.path.isdir(outdirpath):
                os.mkdir(outdirpath)
            if datasetType == 1:
                datafile = dirpath + "/dataset/" + fname + '.dat'
            if datasetType == 2:
                # datafile = dirpath + "/dataset/LFR/LFR1000_u10to80/LFR1000_u" + fname + '/network.dat'
                datafile = dirpath + "/dataset/LFR/LFR10000_u10to80_c100to300/LFR10000_u" + fname + '/network.dat'
            if os.path.isfile(datafile):
                "Set up the graph list"
                #当前版本
                cur_graph = based_CDME_GTCD.non_overlap_game(datafile, fname)
                # cur_graph = based_CDME_GTCD_overlapping.overlap_game(datafile,fname)
                # 先合作再非合作太慢了。效果上也没有提升
                # cur_graph = based_CDME_GTCD_先合作再非合作.non_overlap_game(datafile, fname)
                #改成随机遍历所有节点和上面的随机选择节点也没多大区别。纠正：是根本没区别
                # cur_graph = based_CDME_GTCD_改成shuffle.non_overlap_game(datafile, fname)
                # cur_graph = based_CDME_GTCD_test.non_overlap_game(datafile, fname)
                #改为尝试加入所有社区，而非相邻社区，效用函数改为与社区所有节点的亲密度之和  改为非相邻社区，运行时间就长了很多。
                # print("GTCD_jiarubuxianglinshequ算法")
                # cur_graph = GTCD_jiarubuxianglinshequ.non_overlap_game(datafile, fname)
                #使用simRank定义亲密度的版本
                # cur_graph = GTCD_v5_simRank.non_overlap_game(datafile, fname)
                #使用直接让亲密度就是双向亲密度的版本
                # cur_graph = GTCD_zhijieqinmidu.non_overlap_game(datafile, fname)
                #修改亲密度 加入互动频率的亲密度
                # cur_graph = GTCD_修改亲密度计算公式v2.non_overlap_game(datafile,fname)
                print("start:")
                starttime = datetime.datetime.now()
                # community detection by game
                #datasetType用于区分算什么数据集 1真实，2人工
                cur_graph.community_detection_game(outdirpath, fname,datasetType=datasetType)
                endtime = datetime.datetime.now()
                time_cost = (endtime - starttime).seconds
                print("runtime:" + str(time_cost) + " s")
                # output the result
                #往生成的结果里面添加运行时间
                if datasetType == 1:
                    f = open(outdirpath + "/" + fname + ".txt", "a")
                if datasetType == 2:
                    # f = open(outdirpath + "/LFR_LFR1000/u" + fname + "_result.txt", "a")
                    f = open(outdirpath + "/LFR_LFR10000/u" + fname + "_result.txt", "a")

                f.write("\n\n")
                f.write("runtime:  \n")
                f.write(str(time_cost) + " s")
                f.write("\n")
                f.close()
                print("Done!")
                print("\n")
                '''
                    TODO:
                    Do some analysis and plot 
                '''
            else:
                print("The dataset is not a directory!")
        else:
            print("The input is not a directory!")