import tkinter as tk
from tkinter import messagebox, simpledialog
import json
import os
import random
import math

# 新增导入库
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# ===========================
# 初始生成用户数据的参数
# ===========================
NUM_USERS = 999  # 生成的用户数量
BASE_FRIENDSHIP_PROBABILITY = 0.99  # 基础好友关系建立概率

FIRST_NAMES = [
    "Alice", "Bob", "Charlie", "David", "Eve", "Frank", "Grace", "Hannah",
    "Ivan", "Judy", "Kevin", "Laura", "Mallory", "Niaj", "Olivia", "Peggy",
    "Quentin", "Rupert", "Sybil", "Trent", "Uma", "Victor", "Wendy", "Xavier",
    "Yvonne", "Zach"
]

LAST_NAMES = [
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Miller", "Davis",
    "Wilson", "Taylor", "Anderson", "Thomas", "Jackson", "White", "Harris",
    "Martin", "Thompson", "Garcia", "Martinez", "Robinson", "Clark"
]

INTERESTS_POOL = [
    "Music", "Movies", "Sports", "Books", "Art", "Travel", "Cooking", "Gaming",
    "Fitness", "Photography", "Dancing", "Hiking", "Programming", "Gardening",
    "Fishing", "Crafting", "Yoga", "Blogging", "Drawing", "Cycling"
]

# ===========================
# 用户类
# ===========================
class User:
    def __init__(self, user_id, name, age, interests=None):
        self.user_id = user_id
        self.name = name
        self.age = age
        self.friends = set()
        self.interests = interests if interests else set()

    def add_friend(self, friend_id):
        self.friends.add(friend_id)

    def remove_friend(self, friend_id):
        self.friends.discard(friend_id)

    def add_interest(self, interest):
        self.interests.add(interest)

    def to_dict(self):
        return {
            'user_id': self.user_id,
            'name': self.name,
            'age': self.age,
            'friends': list(self.friends),
            'interests': list(self.interests)
        }

    @staticmethod
    def from_dict(data):
        user = User(
            user_id=data['user_id'],
            name=data['name'],
            age=data['age'],
            interests=set(data.get('interests', []))
        )
        user.friends = set(data.get('friends', []))
        return user

# ===========================
# 社交网络类
# ===========================
class SocialNetwork:
    def __init__(self):
        self.users = {}
        self.adj_list = {}
        self.data_file = 'social_network_data.json'
        self.load_data()

    # 保存数据
    def save_data(self):
        data = {
            'users': [user.to_dict() for user in self.users.values()]
        }
        with open(self.data_file, 'w') as f:
            json.dump(data, f, indent=4)
        print("Data saved successfully.")

    # 加载数据
    def load_data(self):
        if os.path.exists(self.data_file):
            with open(self.data_file, 'r') as f:
                data = json.load(f)
                for user_data in data['users']:
                    user = User.from_dict(user_data)
                    self.users[user.user_id] = user
                    self.adj_list[user.user_id] = user.friends
            print("Data loaded successfully.")
        else:
            print("No existing data found. Generating random initial data...")
            self.generate_random_data()
            self.save_data()

    # 生成随机初始数据
    def generate_random_data(self):
        # 创建用户
        for i in range(1, NUM_USERS + 1):
            user_id = i
            name = random.choice(FIRST_NAMES) + " " + random.choice(LAST_NAMES)
            age = random.randint(18, 65)
            interests = set(random.sample(INTERESTS_POOL, k=random.randint(1, 3)))
            user = User(user_id, name, age, interests)
            self.users[user_id] = user
            self.adj_list[user_id] = set()

        # 调整好友关系建立方式
        user_ids = list(self.users.keys())

        # 初始化每个用户的社区为自身
        communities = {user_id: {user_id} for user_id in user_ids}

        # 遍历所有可能的用户对
        for i in range(len(user_ids)):
            for j in range(i + 1, len(user_ids)):
                user_id_1 = user_ids[i]
                user_id_2 = user_ids[j]

                # 获取两个用户所属的社区
                community_1 = communities[user_id_1]
                community_2 = communities[user_id_2]

                # 计算两个社区的大小
                size_1 = len(community_1)
                size_2 = len(community_2)

                # 计算好友关系建立概率，采用平方衰减
                size_factor = 1 / (max(size_1, size_2) ** 2)
                friendship_probability = BASE_FRIENDSHIP_PROBABILITY * size_factor

                if random.random() < friendship_probability:
                    self.add_friendship(user_id_1, user_id_2, save=False)

                    # 合并社区
                    if community_1 is not community_2:
                        merged_community = community_1.union(community_2)
                        for uid in merged_community:
                            communities[uid] = merged_community

    # 其他方法保持不变（略）

    # 添加用户
    def add_user(self, user_id, name, age, interests=None):
        if user_id in self.users:
            messagebox.showerror("Error", f"User ID {user_id} already exists.")
            return False
        user = User(user_id, name, age, interests)
        self.users[user_id] = user
        self.adj_list[user_id] = set()
        self.save_data()
        return True

    # 删除用户
    def remove_user(self, user_id):
        if user_id not in self.users:
            messagebox.showerror("Error", f"User ID {user_id} does not exist.")
            return False
        for friend_id in self.adj_list[user_id]:
            self.adj_list[friend_id].remove(user_id)
            self.users[friend_id].remove_friend(user_id)
        del self.users[user_id]
        del self.adj_list[user_id]
        self.save_data()
        return True

    # 建立朋友关系
    def add_friendship(self, user_id_1, user_id_2, save=True):
        if user_id_1 not in self.users or user_id_2 not in self.users:
            if save:
                messagebox.showerror("Error", "One or both users do not exist.")
            return False
        if user_id_2 in self.adj_list[user_id_1]:
            if save:
                messagebox.showinfo("Info", "Friendship already exists.")
            return False
        self.adj_list[user_id_1].add(user_id_2)
        self.adj_list[user_id_2].add(user_id_1)
        self.users[user_id_1].add_friend(user_id_2)
        self.users[user_id_2].add_friend(user_id_1)
        if save:
            self.save_data()
        return True

    # 取消朋友关系
    def remove_friendship(self, user_id_1, user_id_2):
        if user_id_1 in self.adj_list and user_id_2 in self.adj_list[user_id_1]:
            self.adj_list[user_id_1].remove(user_id_2)
            self.users[user_id_1].remove_friend(user_id_2)
            self.adj_list[user_id_2].remove(user_id_1)
            self.users[user_id_2].remove_friend(user_id_1)
            self.save_data()
            return True
        else:
            messagebox.showerror("Error", "Friendship does not exist.")
            return False

    # 推荐新朋友，基于共同好友数量
    def recommend_friends(self, user_id):
        if user_id not in self.users:
            messagebox.showerror("Error", f"User ID {user_id} does not exist.")
            return []
        user_friends = self.adj_list[user_id]
        recommendations = {}
        for friend_id in user_friends:
            friends_of_friend = self.adj_list[friend_id]
            for potential_friend in friends_of_friend:
                if potential_friend != user_id and potential_friend not in user_friends:
                    recommendations[potential_friend] = recommendations.get(potential_friend, 0) + 1
        if not recommendations:
            return []
        sorted_recommendations = sorted(recommendations.items(), key=lambda x: x[1], reverse=True)
        return sorted_recommendations

    # 使用 BFS 找到两个用户之间的最短路径
    def find_shortest_path(self, user_id_1, user_id_2):
        from collections import deque
        if user_id_1 not in self.users or user_id_2 not in self.users:
            messagebox.showerror("Error", "One or both users do not exist.")
            return []
        visited = set()
        queue = deque()
        queue.append((user_id_1, [user_id_1]))
        visited.add(user_id_1)
        while queue:
            current_user, path = queue.popleft()
            if current_user == user_id_2:
                return path
            for neighbor in self.adj_list[current_user]:
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, path + [neighbor]))
        return []

    # 找出网络中的关键用户，基于度中心性
    def find_influencers(self):
        if not self.users:
            return []
        degree_centrality = {}
        for user_id in self.users:
            degree_centrality[user_id] = len(self.adj_list[user_id])
        max_degree = max(degree_centrality.values())
        influencers = [user_id for user_id, degree in degree_centrality.items() if degree == max_degree]
        return influencers

    # 使用 DFS 找到网络中的社区
    def find_communities(self):
        visited = set()
        communities = []

        def dfs(current_user, community):
            visited.add(current_user)
            community.append(current_user)
            for neighbor in self.adj_list[current_user]:
                if neighbor not in visited:
                    dfs(neighbor, community)

        for user_id in self.users:
            if user_id not in visited:
                community = []
                dfs(user_id, community)
                communities.append(community)
        return communities

    # 基于兴趣推荐朋友
    def recommend_friends_by_interest(self, user_id):
        if user_id not in self.users:
            messagebox.showerror("Error", f"User ID {user_id} does not exist.")
            return []
        user = self.users[user_id]
        recommendations = {}
        for other_id, other_user in self.users.items():
            if other_id != user_id and other_id not in user.friends:
                common_interests = user.interests.intersection(other_user.interests)
                if common_interests:
                    recommendations[other_id] = len(common_interests)
        if not recommendations:
            return []
        sorted_recommendations = sorted(recommendations.items(), key=lambda x: x[1], reverse=True)
        return sorted_recommendations

    # 判断网络是否连通
    def is_network_connected(self):
        if not self.users:
            return False
        from collections import deque
        visited = set()
        start_user = next(iter(self.users))
        queue = deque()
        queue.append(start_user)
        while queue:
            current_user = queue.popleft()
            if current_user not in visited:
                visited.add(current_user)
                queue.extend(self.adj_list[current_user] - visited)
        return len(visited) == len(self.users)

    # 绘制网络图
    def draw_network(self, canvas_frame):
        G = nx.Graph()
        G.add_nodes_from(self.users.keys())
        for user_id, friends in self.adj_list.items():
            for friend_id in friends:
                if G.has_edge(user_id, friend_id) or user_id == friend_id:
                    continue
                G.add_edge(user_id, friend_id)

        plt.clf()  # 清除之前的图像
        pos = nx.spring_layout(G)
        nx.draw_networkx_nodes(G, pos, node_color='skyblue', node_size=200)
        nx.draw_networkx_edges(G, pos)
        labels = {user_id: user_id for user_id in G.nodes()}
        nx.draw_networkx_labels(G, pos, labels, font_size=5)

        fig = plt.gcf()  # 获取当前图表
        canvas = FigureCanvasTkAgg(fig, master=canvas_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

# ===========================
# GUI 应用程序
# ===========================
class SocialNetworkApp:
    def __init__(self, root):
        self.network = SocialNetwork()
        self.root = root
        self.root.title("Social Network Simulator")
        self.root.configure(bg="#2e2e2e")  # 设置黑暗背景色
        self.root.geometry("800x600")  # 扩大窗口大小
        self.create_widgets()

    def create_widgets(self):
        # 设置全局字体和颜色
        self.btn_font = ('Arial', 12)
        self.btn_bg = "#4d4d4d"
        self.btn_fg = "#ffffff"

        # 按钮框架
        frame = tk.Frame(self.root, bg="#2e2e2e")
        frame.pack(pady=10)

        # 按钮列表
        buttons = [
            ("Add User", self.add_user),
            ("Remove User", self.remove_user),
            ("Add Friendship", self.add_friendship),
            ("Remove Friendship", self.remove_friendship),
            ("Recommend Friends", self.recommend_friends),
            ("Find Shortest Path", self.find_shortest_path),
            ("Find Influencers", self.find_influencers),
            ("Find Communities", self.find_communities),
            ("Recommend by Interest", self.recommend_by_interest),
            ("Check Connectivity", self.check_connectivity),
            ("Display Users", self.display_users),
            ("Refresh Network Graph", self.refresh_network_graph),
            ("Exit", self.root.quit)
        ]

        # 动态创建按钮
        for idx, (text, command) in enumerate(buttons):
            row = idx // 2
            col = idx % 2
            btn = tk.Button(
                frame,
                text=text,
                width=25,
                command=command,
                font=self.btn_font,
                bg=self.btn_bg,
                fg=self.btn_fg,
                relief='raised',
                bd=2
            )
            btn.grid(row=row, column=col, padx=10, pady=5)

        # 网络图显示区域
        self.canvas_frame = tk.Frame(self.root, bg="#2e2e2e")
        self.canvas_frame.pack(fill=tk.BOTH, expand=True)

        # 绘制初始网络图
        self.network.draw_network(self.canvas_frame)

    # 处理添加用户
    def add_user(self):
        try:
            user_id = int(simpledialog.askstring("Add User", "Enter User ID:"))
            name = simpledialog.askstring("Add User", "Enter Name:")
            age = int(simpledialog.askstring("Add User", "Enter Age:"))
            interests_input = simpledialog.askstring("Add User", "Enter Interests (comma-separated):")
            interests = set(map(str.strip, interests_input.split(','))) if interests_input else set()
            success = self.network.add_user(user_id, name, age, interests)
            if success:
                messagebox.showinfo("Success", f"User {user_id} added successfully.")
                self.refresh_network_graph()
        except (ValueError, TypeError):
            messagebox.showerror("Error", "Invalid input.")

    # 处理删除用户
    def remove_user(self):
        try:
            user_id = int(simpledialog.askstring("Remove User", "Enter User ID to remove:"))
            success = self.network.remove_user(user_id)
            if success:
                messagebox.showinfo("Success", f"User {user_id} removed successfully.")
                self.refresh_network_graph()
        except (ValueError, TypeError):
            messagebox.showerror("Error", "Invalid input.")

    # 处理添加朋友关系
    def add_friendship(self):
        try:
            user_id_1 = int(simpledialog.askstring("Add Friendship", "Enter First User ID:"))
            user_id_2 = int(simpledialog.askstring("Add Friendship", "Enter Second User ID:"))
            success = self.network.add_friendship(user_id_1, user_id_2)
            if success:
                messagebox.showinfo("Success", f"Friendship between {user_id_1} and {user_id_2} added.")
                self.refresh_network_graph()
        except (ValueError, TypeError):
            messagebox.showerror("Error", "Invalid input.")

    # 处理取消朋友关系
    def remove_friendship(self):
        try:
            user_id_1 = int(simpledialog.askstring("Remove Friendship", "Enter First User ID:"))
            user_id_2 = int(simpledialog.askstring("Remove Friendship", "Enter Second User ID:"))
            success = self.network.remove_friendship(user_id_1, user_id_2)
            if success:
                messagebox.showinfo("Success", f"Friendship between {user_id_1} and {user_id_2} removed.")
                self.refresh_network_graph()
        except (ValueError, TypeError):
            messagebox.showerror("Error", "Invalid input.")

    # 处理好友推荐
    def recommend_friends(self):
        try:
            user_id = int(simpledialog.askstring("Recommend Friends", "Enter User ID:"))
            recommendations = self.network.recommend_friends(user_id)
            if recommendations:
                msg = "\n".join([f"User {rec[0]} with {rec[1]} mutual friends" for rec in recommendations])
                messagebox.showinfo("Recommendations", msg)
            else:
                messagebox.showinfo("Recommendations", "No recommendations available.")
        except (ValueError, TypeError):
            messagebox.showerror("Error", "Invalid input.")

    # 处理最短路径查找
    def find_shortest_path(self):
        try:
            user_id_1 = int(simpledialog.askstring("Find Shortest Path", "Enter Starting User ID:"))
            user_id_2 = int(simpledialog.askstring("Find Shortest Path", "Enter Target User ID:"))
            path = self.network.find_shortest_path(user_id_1, user_id_2)
            if path:
                messagebox.showinfo("Shortest Path", f"Shortest path: {path}")
            else:
                messagebox.showinfo("Shortest Path", "No path found.")
        except (ValueError, TypeError):
            messagebox.showerror("Error", "Invalid input.")

    # 处理查找关键用户
    def find_influencers(self):
        influencers = self.network.find_influencers()
        if influencers:
            msg = "\n".join([f"User {user_id}" for user_id in influencers])
            messagebox.showinfo("Influencers", f"Influencers:\n{msg}")
        else:
            messagebox.showinfo("Influencers", "No influencers found.")

    # 处理社区发现
    def find_communities(self):
        communities = self.network.find_communities()
        if communities:
            msg = ""
            for idx, community in enumerate(communities):
                msg += f"Community {idx + 1}: {community}\n"
            messagebox.showinfo("Communities", msg)
        else:
            messagebox.showinfo("Communities", "No communities found.")

    # 处理基于兴趣的好友推荐
    def recommend_by_interest(self):
        try:
            user_id = int(simpledialog.askstring("Recommend by Interest", "Enter User ID:"))
            recommendations = self.network.recommend_friends_by_interest(user_id)
            if recommendations:
                msg = "\n".join([f"User {rec[0]} with {rec[1]} common interests" for rec in recommendations])
                messagebox.showinfo("Interest-based Recommendations", msg)
            else:
                messagebox.showinfo("Interest-based Recommendations", "No recommendations available.")
        except (ValueError, TypeError):
            messagebox.showerror("Error", "Invalid input.")

    # 处理网络连通性检查
    def check_connectivity(self):
        is_connected = self.network.is_network_connected()
        msg = "The network is connected." if is_connected else "The network is disconnected."
        messagebox.showinfo("Network Connectivity", msg)

    # 显示所有用户信息
    def display_users(self):
        if not self.network.users:
            messagebox.showinfo("Users", "No users in the network.")
            return
        msg = ""
        for user_id, user in self.network.users.items():
            msg += f"User ID: {user_id}, Name: {user.name}, Age: {user.age}, Friends: {sorted(list(user.friends))}\n"
        messagebox.showinfo("Users", msg)

    # 刷新网络图
    def refresh_network_graph(self):
        # 清除旧的图像
        for widget in self.canvas_frame.winfo_children():
            widget.destroy()
        # 重新绘制网络图
        self.network.draw_network(self.canvas_frame)

# 程序入口
if __name__ == "__main__":
    root = tk.Tk()
    app = SocialNetworkApp(root)
    root.mainloop()
