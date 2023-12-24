# 预定义三元组，作为物体的三个属性的数值
values = [
    (94, 86, 0),
    (56, 72, 40),
    (15, 75, 78),
    (5, 80, 83),

    (12, 62, 88),
    (64, 80, 18),
    (64, 20, 78),
    (80, 0, 76),

    (48, 23, 85),
    (66, 60, 15),
    (10, 58, 73),
    (54, 16, 71),

    (56, 15, 64),
    (68, 57, 10),
    (42, 22, 65),
    (78, 9, 39),

    (10, 66, 50),
    (63, 0, 63),
    (44, 54, 10),
    (54, 54, 0)
]
# 预定义不同的名字，作为物体的名字
names = [
    "1",
    "2",
    "3",
    "4",
    "5",
    "6",
    "7",
    "8",
    "9",
    "10",
    "11",
    "12",
    "13",
    "14",
    "15",
    "16",
    "17",
    "18",
    "19",
    "20"
]
# 创建一个列表boxes，用于存储盒子的信息
boxes = [
    {"A_box": 99, "B_box": 70, "C_box": 135, "objects": []},
    {"A_box": 195, "B_box": 137, "C_box": 43, "objects": []},
    {"A_box": 105, "B_box": 210, "C_box": 165, "objects": []},
    {"A_box": 115, "B_box": 125, "C_box": 145, "objects": []}
]

# 导入itertools模块，用于生成所有可能的组合
import itertools

# 定义一个函数，用于检查一个组合是否满足一个盒子的要求
def check_combination(combination, box):
    # 计算组合中的物体的A,B,C属性的总和
    A_sum = sum(values[i][0] for i in combination)
    B_sum = sum(values[i][1] for i in combination)
    C_sum = sum(values[i][2] for i in combination)
    # 检查总和是否大于盒子的要求
    if A_sum > box["A_box"] and B_sum > box["B_box"] and C_sum > box["C_box"]:
        # 返回True表示满足
        return True
    else:
        # 返回False表示不满足
        return False

# 定义一个函数，用于寻找一个可行的方案，将物体分配到盒子中
def find_solution():
    # 生成所有可能的三个物体的组合，共有16*15*14/6 = 560种
    combinations = list(itertools.combinations(range(16), 3))
    # 遍历所有的组合
    for c1 in combinations:
        # 从剩余的组合中选择一个满足第一个盒子的要求的组合
        if check_combination(c1, boxes[0]):
            # 从剩余的组合中选择一个满足第二个盒子的要求的组合
            for c2 in combinations:
                # 检查是否和第一个组合有重复的物体
                if len(set(c1) & set(c2)) == 0 and check_combination(c2, boxes[1]):
                    # 从剩余的组合中选择一个满足第三个盒子的要求的组合
                    for c3 in combinations:
                        # 检查是否和前两个组合有重复的物体
                        if len(set(c1) & set(c3)) == 0 and len(set(c2) & set(c3)) == 0 and check_combination(c3, boxes[2]):
                            # 从剩余的组合中选择一个满足第四个盒子的要求的组合
                            for c4 in combinations:
                                # 检查是否和前三个组合有重复的物体
                                if len(set(c1) & set(c4)) == 0 and len(set(c2) & set(c4)) == 0 and len(set(c3) & set(c4)) == 0 and check_combination(c4, boxes[3]):
                                    # 找到了一个可行的方案，返回四个组合
                                    return c1, c2, c3, c4
    # 没有找到可行的方案，返回None
    return None

# 调用函数，寻找一个可行的方案
solution = find_solution()

# 如果找到了方案，打印出来
if solution:
    print("找到了一个可行的方案，如下：")
    # 遍历四个盒子
    for i in range(4):
        # 打印出每个盒子的信息
        # print(f"盒子{i+1}的要求是：A_box = {boxes[i]['A_box']}, B_box = {boxes[i]['B_box']}, C_box = {boxes[i]['C_box']}")
        # 打印出每个盒子中的物体的名字和属性
        print(f"盒子{i+1}中的物体是：")
        for j in solution[i]:
            print(f"{names[j]}: A = {values[j][0]}, B = {values[j][1]}, C = {values[j][2]}")
        # 打印出每个盒子中的物体的属性的总和
        #print(f"盒子{i+1}中的物体的属性的总和是：A_sum = {sum(values[j][0] for j in solution[i])}, B_sum = {sum(values[j][1] for j in solution[i])}, C_sum = {sum(values[j][2] for j in solution[i])}")
        print()
# 如果没有找到方案，打印出来
else:
    print("没有找到可行的方案。")
