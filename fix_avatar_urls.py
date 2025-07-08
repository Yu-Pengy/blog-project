#!/usr/bin/env python3
"""
修复main.py中的头像URL硬编码问题
移除所有localhost:5000的硬编码，确保头像URL只返回相对路径
"""

import re

# 读取文件
with open('blog/main.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 替换所有形如 "if avatar_url and not avatar_url.startswith('http'):\n                        avatar_url = f\"http://localhost:5000{avatar_url}\"" 的代码
pattern = r'\s*if avatar_url and not avatar_url\.startswith\(\'http\'\):\s*\n\s*avatar_url = f"http://localhost:5000\{avatar_url\}"'
content = re.sub(pattern, '', content)

# 替换头像上传中的完整URL返回
content = content.replace(
    'full_avatar_url = f"http://localhost:5000{avatar_url}"\n                return jsonify({\n                    \'success\': True,\n                    \'message\': \'头像上传成功\',\n                    \'data\': {\n                        \'avatar_url\': full_avatar_url\n                    }\n                })',
    'return jsonify({\n                    \'success\': True,\n                    \'message\': \'头像上传成功\',\n                    \'data\': {\n                        \'avatar_url\': avatar_url\n                    }\n                })'
)

# 替换获取用户资料中的硬编码
content = content.replace(
    'if avatar_url and not avatar_url.startswith(\'http\'):\n            avatar_url = f"http://localhost:5000{avatar_url}"\n            print(f"完整头像URL: {avatar_url}")',
    'print(f"头像URL: {avatar_url}")'
)

content = content.replace(
    'if avatar_url and not avatar_url.startswith(\'http\'):\n            avatar_url = f"http://localhost:5000{avatar_url}"',
    ''
)

# 移除其他零散的硬编码
lines = content.split('\n')
new_lines = []
i = 0
while i < len(lines):
    line = lines[i]
    # 跳过包含localhost:5000硬编码的行（除了最后的打印语句）
    if 'avatar_url = f"http://localhost:5000{avatar_url}"' in line and 'print(' not in line:
        # 同时检查上一行是否是相关的if语句
        if i > 0 and 'if avatar_url and not avatar_url.startswith(\'http\')' in lines[i-1]:
            # 移除上一行的if语句
            new_lines.pop()
        i += 1
        continue
    new_lines.append(line)
    i += 1

content = '\n'.join(new_lines)

# 写回文件
with open('blog/main.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("已修复main.py中的头像URL硬编码问题")
print("现在所有头像URL都将返回相对路径，由Nginx处理代理")
