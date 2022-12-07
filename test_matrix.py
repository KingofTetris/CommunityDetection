import numpy as np

A = np.array([ [1,3,5],[2,4,6] ])
B = np.array([ [1,1],[2,2],[3,3] ])
print(A.shape)
print(B.shape)

C = np.dot(A,B)

print(C)