import math
import numpy as np
def NMI(com, real_com):
    """
    Compute the Normalized Mutual Information(NMI)
    Parameters
    --------
    com, real_com : list or numpy.array
        number of community of nodes

    com是一个列表，其中的元素对是从1-n个节点对应的社区序号
    eg:[1,1,2,2,1,1,...] 就是1，2，5，6在1号社区，3，4在2号社区。
    """
    if len(com) != len(real_com):
        return ValueError('len(A) should be equal to len(B)')

    com = np.array(com)
    real_com = np.array(real_com)
    total = len(com)
    com_ids = set()
    real_com_ids = set()
    for item in com:
        for i in item:
            com_ids.add(i)
    for item in real_com:
        for i in item:
            real_com_ids.add(i)
    # com_ids = set(com)
    # real_com_ids = set(real_com)
    #Mutual information
    MI = 0
    eps = 1.4e-45
    for id_com in com_ids:
        for id_real in real_com_ids:
            idAOccur = np.where(com == id_com)
            idBOccur = np.where(real_com == id_real)
            idABOccur = np.intersect1d(idAOccur, idBOccur)
            px = 1.0*len(idAOccur[0])/total
            py = 1.0*len(idBOccur[0])/total
            pxy = 1.0*len(idABOccur)/total
            MI = MI + pxy*math.log(pxy/(px*py) + eps,2)
    # Normalized Mutual information
    Hx = 0
    for idA in com_ids:
        idAOccurCount = 1.0*len(np.where(com == idA)[0])
        Hx = Hx - (idAOccurCount/total)*math.log(idAOccurCount/total + eps, 2)
    Hy = 0
    for idB in real_com_ids:
        idBOccurCount = 1.0*len(np.where(real_com == idB)[0])
        Hy = Hy - (idBOccurCount/total) * math.log(idBOccurCount/total + eps, 2)
    MIhat = 2.0*MI/(Hx + Hy)
    return MIhat