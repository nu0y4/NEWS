#!/bin/bash

# 获取当前用户的crontab内容，并添加一行新的作业，确保不会覆盖现有的crontab
(crontab -l 2>/dev/null; echo "0 8 * * * /usr/bin/python3 /path/to/tui.py") | crontab -
