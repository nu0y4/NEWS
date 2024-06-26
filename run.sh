#!/bin/bash

# 定义脚本路径
SCRIPT_PATH="runscript.sh"

# 检查是否存在run_scripts.sh
if [ ! -f "$SCRIPT_PATH" ]; then
    # 如果不存在，则创建该文件并写入内容
    echo "#!/bin/bash" > "$SCRIPT_PATH"
    echo "python3 /Crawler/zgc.py" >> "$SCRIPT_PATH"
    echo "python3 /Crawler/cctv.py" >> "$SCRIPT_PATH"

    # 设置脚本的可执行权限
    chmod +x "$SCRIPT_PATH"
fi

# 添加cron任务
(crontab -l 2>/dev/null; echo "0 8 * * * $SCRIPT_PATH") | crontab -
