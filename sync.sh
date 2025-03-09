#!/bin/bash
set -e  # 退出脚本如果有命令返回非零状态
set -u  # 变量未设置时报错并退出

# 创建日志函数
log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1"
}

# 错误处理函数
handle_error() {
    log "错误: $1"
    exit 1
}

# 检查git是否安装
if ! command -v git &> /dev/null; then
    handle_error "Git未安装，请先安装Git"
fi

# 获得脚本所在的路径
FOLDER_PATH=$(dirname "$0")
REMOTE_URL="https://github.com/HarryCCC/Various-Codes.git"
LOG_FILE="$FOLDER_PATH/sync_log.txt"

# 创建日志文件
touch "$LOG_FILE"
log "开始同步操作" | tee -a "$LOG_FILE"

# 跳转到目标文件夹
cd "$FOLDER_PATH" || handle_error "无法进入目录 $FOLDER_PATH"

# 初始化 Git 仓库
log "初始化Git仓库" | tee -a "$LOG_FILE"
git init || handle_error "Git初始化失败"

# 获取当前分支名称（如果不存在则默认使用master）
BRANCH=$(git branch --show-current 2>/dev/null || echo "master")
log "当前分支: $BRANCH" | tee -a "$LOG_FILE"

# 创建或确保.gitignore存在
if [ ! -f ".gitignore" ]; then
    log "创建.gitignore文件" | tee -a "$LOG_FILE"
    echo "backups/" > .gitignore
    echo "sync_log.txt" >> .gitignore
else
    # 确保忽略备份目录和日志文件
    if ! grep -q "backups/" .gitignore; then
        echo "backups/" >> .gitignore
    fi
    if ! grep -q "sync_log.txt" .gitignore; then
        echo "sync_log.txt" >> .gitignore
    fi
fi

# 检测变更文件
log "检测变更文件" | tee -a "$LOG_FILE"
CHANGED_FILES=$(git status --porcelain | grep -v "??" | awk '{print $2}')

if [ -z "$CHANGED_FILES" ]; then
    log "没有发现变更文件，检查未跟踪文件" | tee -a "$LOG_FILE"
    UNTRACKED_FILES=$(git status --porcelain | grep "??" | awk '{print $2}')
    
    if [ -z "$UNTRACKED_FILES" ]; then
        log "没有文件需要同步，操作完成" | tee -a "$LOG_FILE"
        exit 0
    else
        log "发现 $(echo "$UNTRACKED_FILES" | wc -l) 个未跟踪文件需要添加" | tee -a "$LOG_FILE"
        # 选择性添加文件，避免添加大型二进制文件或不必要文件
        for FILE in $UNTRACKED_FILES; do
            # 跳过备份目录和日志文件
            if [[ "$FILE" != backups/* && "$FILE" != *sync_log.txt ]]; then
                FILE_SIZE=$(du -k "$FILE" | cut -f1)
                if [ "$FILE_SIZE" -lt 1024 ]; then  # 小于1MB的文件
                    git add "$FILE"
                    log "添加文件: $FILE ($(($FILE_SIZE/1))KB)" | tee -a "$LOG_FILE"
                else
                    log "跳过大文件: $FILE ($(($FILE_SIZE/1024))MB)" | tee -a "$LOG_FILE"
                fi
            fi
        done
    fi
else
    log "发现 $(echo "$CHANGED_FILES" | wc -l) 个已变更文件" | tee -a "$LOG_FILE"
    # 打印前5个变更文件以供参考
    log "变更文件预览:" | tee -a "$LOG_FILE"
    echo "$CHANGED_FILES" | head -5 | sed 's/^/  - /' | tee -a "$LOG_FILE"
    git add --update  # 只添加已跟踪的变更文件
fi

# 检查是否有文件需要提交
if [ "$(git status --porcelain)" = "" ]; then
    log "没有文件需要提交，同步操作完成" | tee -a "$LOG_FILE"
    exit 0
else
    # 有文件变更，进行提交
    COMMIT_MSG="同步更新 $(date +'%Y-%m-%d %H:%M:%S')"
    log "提交变更: $COMMIT_MSG" | tee -a "$LOG_FILE"
    git commit -m "$COMMIT_MSG" || handle_error "提交失败"
fi

# 添加远程仓库
log "设置远程仓库: $REMOTE_URL" | tee -a "$LOG_FILE"
git remote add origin "$REMOTE_URL" 2> /dev/null || git remote set-url origin "$REMOTE_URL"

# 使用克隆深度为1，减少历史数据
log "尝试获取最新分支信息（轻量级）" | tee -a "$LOG_FILE"
if ! git fetch --depth=1 origin $BRANCH; then
    log "无法获取远程分支，可能是新仓库或分支不存在" | tee -a "$LOG_FILE"
else
    # 检查本地和远程的差异
    log "检查本地与远程的差异" | tee -a "$LOG_FILE"
    if git rev-parse --verify origin/$BRANCH >/dev/null 2>&1; then
        DIFF_FILES=$(git diff --name-only HEAD origin/$BRANCH)
        if [ -z "$DIFF_FILES" ]; then
            log "本地与远程没有差异，无需推送" | tee -a "$LOG_FILE"
            exit 0
        else
            DIFF_COUNT=$(echo "$DIFF_FILES" | wc -l)
            log "发现 $DIFF_COUNT 个文件与远程不同" | tee -a "$LOG_FILE"
        fi
    fi
fi

# 开始增量推送
log "开始增量推送..." | tee -a "$LOG_FILE"

# 尝试使用标准推送（轻量级，只推送差异）
if git push -u origin $BRANCH; then
    log "推送成功" | tee -a "$LOG_FILE"
else
    log "普通推送失败，尝试自定义增量推送" | tee -a "$LOG_FILE"
    
    # 如果常规推送失败，尝试创建一个孤立分支进行推送
    TEMP_BRANCH="temp_${BRANCH}_$(date +%Y%m%d%H%M%S)"
    log "创建临时分支: $TEMP_BRANCH" | tee -a "$LOG_FILE"
    
    # 创建一个新的、空的分支
    git checkout --orphan $TEMP_BRANCH
    
    # 添加当前文件并提交
    git add .
    git commit -m "增量同步 $(date +'%Y-%m-%d %H:%M:%S')"
    
    # 尝试推送这个新分支
    if git push -u origin $TEMP_BRANCH; then
        log "临时分支推送成功" | tee -a "$LOG_FILE"
        
        # 在GitHub上创建PR或直接合并（这一步需要手动操作）
        log "请在GitHub上将分支 $TEMP_BRANCH 合并到 $BRANCH" | tee -a "$LOG_FILE"
        
        # 切回原始分支
        git checkout $BRANCH
    else
        log "所有推送尝试失败" | tee -a "$LOG_FILE"
        git checkout $BRANCH
        handle_error "无法推送到远程仓库，请检查网络和权限"
    fi
fi

log "同步操作完成" | tee -a "$LOG_FILE"
log "================" | tee -a "$LOG_FILE"