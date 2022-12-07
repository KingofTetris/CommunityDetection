def read_algorithm_community(filepath):
    partition = []
    temp = []
    with open(filepath, 'r') as fp:
        for line in fp.readlines():  ##readlines(),函数把所有的行都读取进来；
            # temp = list(line.strip().split('\t'))  ##删除行后的换行符并按\t分割，temp 就是每行的内容啦
            temp = list(line.strip().split(' '))  ##删除行后的换行符并按\t分割，temp 就是每行的内容啦
            #temp = list(line.strip())  ##删除行后的换行符并按\t分割，temp 就是每行的内容啦
            partition.append(temp)
            temp = []

    for community in partition:
        print(community)
    return partition


if __name__ == '__main__':
    # 算法社区分布 algorithm_com_partition
    algorithm_com_partition = read_algorithm_community(
        './data/real_network/football_com.dat')
    # algorithm_com_list = []
    # community_index = 0
    # for c in algorithm_com_partition:
    #     community_index = community_index + 1
    #     for element in c:
    #         algorithm_com_list.insert(int(element) - 1, community_index)
    # print(len(algorithm_com_list))
    # print(algorithm_com_list)
