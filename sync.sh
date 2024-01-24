#!/bin/bash
set -e  # 退出脚本如果有命令返回非零状态
set -u  # 变量未设置时报错并退出

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

# 同步远程仓库的最新更改
git pull origin main --rebase

# 尝试推送多次，直到成功或达到尝试次数上限
MAX_ATTEMPTS=3
ATTEMPT=0
while [ $ATTEMPT -lt$MAX_ATTEMPTS ]; do
    git push origin main && break
    ATTEMPT=$((ATTEMPT+1))
    echo "尝试推送失败，将在5秒后重试..."
    sleep 5
done

# 检查是否成功推送
if [ $ATTEMPT -eq$MAX_ATTEMPTS ]; then
    echo "推送失败，已达到最大尝试次数。"
    exit 1
fi

echo "推送成功。"


# 放弃合并:   git rebase --abort
# 初始配置：  git config --global user.name "Your Name"      git config --global user.email "your@email.com"
# 脚本赋权:   chmod +x sync.sh
