
fnamelist = ["karate","dolphins", 'football', 'polblogs', 'polbooks']
for fname in fnamelist:
    with open('./output/' + fname + '_partition.txt', 'r') as f:
        data = f.readlines()
    nums = set()
    duplicates = []
    for line in data:
        nodes = line.strip().split(', ')
        # print(nodes)
        for node in nodes:
            # print(node)
            if node in nums:
                duplicates.append(node)
            else:
                nums.add(node)

    if duplicates:
        print(fname + "_partition.txt中重复的数字：", duplicates)
    else:
        print(fname + "_partition.txt没有重复的数字。")
