#!/bin/bash

# 获得脚本所在的路径
FOLDER_PATH=$(dirname "$0")
REMOTE_URL="https://github.com/HarryCCC/Various-Codes.git"  

# 跳转到目标文件夹
cd "$FOLDER_PATH" || exit

# 初始化 Git 仓库（如果已经存在，此命令不会有任何效果）
git init

# 添加所有文件到 Git
git add .

# 提交文件
git commit -m "脚本同步"

# 添加远程仓库（如果已经存在，此命令不会有任何效果）
git remote add origin "$REMOTE_URL" 2> /dev/null || git remote set-url origin "$REMOTE_URL"

# 获取远程主分支的最新更改
git pull origin main --rebase

# 推送到远程仓库的主分支
git push origin main

# 放弃合并:   git rebase --abort
# 初始配置：  git config --global user.name "Your Name"      git config --global user.email "your@email.com"
# 脚本赋权:   chmod +x sync.sh

