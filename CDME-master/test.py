# # new_same_best = {75: [115], 95:[115,34],16:[27],85: [66], 66:[52]}
# # new_same_best = {9696: [9930],
# #                  9818: [9858, 9989, 9957, 9874, 9909],
# #                  9644: [9960],
# #                  9803: [9999],
# #                  9662: [9681],
# #                  9764: [9938],
# #                  9567: [9986, 9835, 9902, 9681, 9971, 9750, 9882, 9918],
# #                  9650: [9787],
# #                  9847: [9968],
# #                  9857: [9978],
# #                  9821: [9894],
# #                  9608: [9695]}
# # new_same_best = { 9681: [9662],
# #                   9567: [9986, 9835, 9902, 9681, 9971, 9750, 9882, 9918]
# #                   }
# import math
#
# # num = math.log2(1887)
# # print(num)
#
#
#
# #OK
# #一开始的group有[9874,9985]和[9644,9960]
# #在对比K-V集合[9642,9985...,9960...,]时，由于顺序限制，这个K-V集合会先和[9874,9985]合并
# #合并完，就直接跳出到下一个K-V了，这就导致[9644,9960]仍然存在于groups里面
# #而没有合并到[9642,9874,9985,...,9960,...]里面
# #从而出现了重复的社区号
# # new_same_best = {
#     9696: [9989, 9996, 9757, 9786, 9681, 9972],
#     9874: [9985],
#     9644: [9960],
#     9642: [9985, 9859, 9987, 9865, 9995, 9910, 9662, 9934, 9960, 9965, 9714, 9716, 9852, 9983],
#     9806: [9930],
#     9714: [9926],
#     9680: [9983],
#     9847: [9950],
#     9662: [9928],
#     9608: [9695]}
#
# groups = []  # 结果分组
#
# # # 为了解决问题1，前一个group把现在的K-V合并了，但是下一个group也和现在的K-V关联怎么办?
# # 那只能遍历所有的group，把有关联的group标记出来，最后一起合并
#
# for key, valuesList in new_same_best.items():  # 遍历所有K-V
#     temp = []  # 和当前K-V相关联的group的下标，每个新K-V都会用新的[]去接收
#     length = 0  # 记录当前K-V是否和所有group都不关联
#     # 遍历不同group
#     for i in range(len(groups)):
#         flag = False  # 每次K-V和当前group默认无关
#         for value in valuesList:
#             # 如果k,v中的一个在当前groups[i]中，那么这个K-V和group有关联，添加到temp中
#             if key in groups[i] or value in groups[i]:
#                 # temp.append([key, valuesList])  # 直接添加内容
#                 temp.append(i)  # 直接添加内容
#                 flag = True  # 这对K-V和当前group关联，标记当前group，比较下一个group
#                 break  # 如果flag为True 说明当前K-V已经和某个group关联，跳出循环，开始下个K-V
#
#         if flag is False:
#             length = length + 1  # 如果key 和 所有value都不在当前group里面，length++
#
#     # 如果遍历完当前groups的所有组别都没有相关，就建一个新组
#     if length == len(groups):
#         new_group = [key]
#         for v in valuesList:
#             new_group.append(v)
#         groups.append(new_group)
#
#     else:  # 把当前K-V和所有在temp里面的group合并到一起
#         # 先添加当前K-V
#         new_group = [key]
#         for v in valuesList:
#             new_group.append(v)
#         # 合并其他关联group
#         # 而且不能边添边删，不然i可能对应不上
#         for i in temp:
#             for element in groups[i]:
#                 if element not in new_group:
#                     new_group.append(element)
#         # 删除旧的组,也不能直接删，删除一个后面的i就要跟着-1
#         # 动态数组增删就是麻烦。
#         # 例如temp里面现在是[1,2,5] 对应groups(1)和groups(2)
#         # 但是你删掉groups(1)后，groups(2)就变成了groups(1)
#         # groups(5)就成了groups(4)
#         # 所以你每删掉一个group,temp里的数都要跟着减1
#
#         # 所以删除起来就需要点技巧。比如下面这个每次删除掉temp[0]，直到temp为空
#         while temp:
#             del groups[temp[0]]
#             temp.pop(0)
#             temp = [x - 1 for x in temp]
#
#         # 添加新的分组
#         groups.append(new_group)
#
# # 打印结果
# for group in groups:
#     print(list(group))


t =  int(3 / 2)
print(t)