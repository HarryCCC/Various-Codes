# 导入必要的库
import numpy as np
import matplotlib.pyplot as plt
from sklearn.datasets import load_breast_cancer
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier, AdaBoostClassifier, VotingClassifier

# 加载乳腺癌数据集
cancer = load_breast_cancer()
X = cancer.data # 特征矩阵，每个样本有30个特征
y = cancer.target # 目标向量，每个样本有一个目标值，是乳腺癌的类别

# 将数据集分成训练集和测试集
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=0) # 测试集占20%，设置随机种子为0

# 创建一个决策树分类器的实例
tree = DecisionTreeClassifier(random_state=0) # 设置随机种子为0

# 创建一个随机森林分类器的实例，设置基分类器的个数为100
forest = RandomForestClassifier(n_estimators=100, random_state=0) # 设置随机种子为0

# 创建一个AdaBoost分类器的实例，设置基分类器的个数为100
adaboost = AdaBoostClassifier(n_estimators=100, random_state=0) # 设置随机种子为0

# 创建一个投票分类器的实例，设置基分类器为决策树、随机森林和AdaBoost
voting = VotingClassifier(estimators=[("tree", tree), ("forest", forest), ("adaboost", adaboost)], voting="hard")

# 使用训练集来训练各个模型
tree.fit(X_train, y_train)
forest.fit(X_train, y_train)
adaboost.fit(X_train, y_train)
voting.fit(X_train, y_train)

# 使用测试集来评估各个模型的准确率
y_pred_tree = tree.predict(X_test)
y_pred_forest = forest.predict(X_test)
y_pred_adaboost = adaboost.predict(X_test)
y_pred_voting = voting.predict(X_test)

acc_tree = accuracy_score(y_test, y_pred_tree)
acc_forest = accuracy_score(y_test, y_pred_forest)
acc_adaboost = accuracy_score(y_test, y_pred_adaboost)
acc_voting = accuracy_score(y_test, y_pred_voting)

print("决策树的准确率：", acc_tree)
print("随机森林的准确率：", acc_forest)
print("AdaBoost的准确率：", acc_adaboost)
print("投票分类器的准确率：", acc_voting)
