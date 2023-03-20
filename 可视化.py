import networkx as nx
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm
from networkx.algorithms import community
import random
# science and nature journal '#e3a6a1 ;, '#bc5f6a'，'#19b3b1 ;，"#034b61"# star sky science-fiction '#b2a59f,'#023459','#1e646e'’"#002c2f
# delicate & shopping & pettyfashion '#b2d6ca' '#fe5858','#024b40','#5d353e
colors = ['#fe5858','#O34b61', '#5d353e','#b2d6ca']
options = {'font_familyt':'serif', 'font_weight': 'semibold','font_size':'12','font_color': '#ffffff'}
savefig_path = 'F:/Python/NetworkSci/'
def com_postion(size ,scale=1, center=(0, 0), dim=2):
    num = size
    center = np.asarray(center)
    theta = np.linspace(0,1,num+1)[:-1]*2*np.pi
    theta = theta.astype(np.float32)
    pos = np.column_stack([np.cos(theta),np.sin(theta),np.zeros((num,0))])
    pos = scale*pos +center
    return pos


