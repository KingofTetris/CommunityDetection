import networkx as nx
class Solution:
    def largestComponentSize(self,nums):
        edges = []
        G = nx.Graph()
        for i in nums:
            for j in nums:
                if( i != j and gcd(i,j) > 1):
                    edges.append([i,j])
        G.add_edges_from(edges)
        max = 0;
        for i in nx.connected_components(G):
            num = 0; #每轮令nums = 0
            for nodes in i:
                num = num + 1; #每有一个连通就+1
            if num > max:
                max = num; #取最大的那个连通分量
        return max;

def gcd(a,b):
    reminder = a % b
    while(reminder != 0):
        a = b
        b = reminder
        reminder = a % b
    return b

if __name__ == '__main__':
    nums = [2,3,6,7,4,12,21,39]
    s = Solution()
    print(s.largestComponentSize(nums))