#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import datetime
import based_CDME_GTCD
import GTCD_v5_simRank
import GTCD_jiarubuxianglinshequ

if __name__ == '__main__':

    # "Input: a dataset name "

    # fnamelist =['football']
    fnamelist = ["karate", "dolphins", 'football', 'polblogs', 'polbooks']

    for fname in fnamelist:
        dirpath = './'
        if os.path.isdir(dirpath):
            "Set a output folder"
            outdirpath = dirpath + "/output"
            if not os.path.isdir(outdirpath):
                os.mkdir(outdirpath)
            datafile = dirpath + "/dataset/" + fname + '.dat'
            if os.path.isfile(datafile):
                "Set up the graph list"
                #当前版本
                cur_graph = based_CDME_GTCD.non_overlap_game(datafile, fname)
                #改为尝试加入所有社区，而非相邻社区，效用函数改为与社区所有节点的亲密度之和  改为非相邻社区，运行时间就长了很多。
                # print("GTCD_jiarubuxianglinshequ算法")
                # cur_graph = GTCD_jiarubuxianglinshequ.non_overlap_game(datafile, fname)
                #使用simRank定义亲密度的版本
                # cur_graph = GTCD_v5_simRank.non_overlap_game(datafile, fname)
                print("start:")
                starttime = datetime.datetime.now()
                # community detection by game
                cur_graph.community_detection_game(outdirpath, fname)

                endtime = datetime.datetime.now()
                time_cost = (endtime - starttime).seconds
                print("runtime:" + str(time_cost) + " s")
                # output the result
                f = open(outdirpath + "/" + fname + ".txt", "a")

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