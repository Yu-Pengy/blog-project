#!/usr/bin/env python3
"""
修复main.py中所有的头像URL处理，确保适配Docker容器环境
"""

import re

def fix_avatar_urls():
    # 读取main.py文件
    with open('main.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 替换所有的 post_dict['author_avatar'] = avatar_url
    content = re.sub(
        r"post_dict\['author_avatar'\] = avatar_url",
        "post_dict['author_avatar'] = get_full_avatar_url(avatar_url)",
        content
    )
    
    # 替换其他相关的头像URL赋值
    patterns = [
        (r"'avatar_url': avatar_url", "'avatar_url': get_full_avatar_url(avatar_url)"),
        (r"'author_avatar': avatar_url", "'author_avatar': get_full_avatar_url(avatar_url)"),
    ]
    
    for pattern, replacement in patterns:
        content = re.sub(pattern, replacement, content)
    
    # 备份原文件
    with open('main.py.backup', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("备份文件已创建: main.py.backup")
    
    # 写回修改后的内容
    with open('main.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("已修复main.py中的头像URL处理")

if __name__ == '__main__':
    fix_avatar_urls()
