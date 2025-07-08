import sqlite3
from datetime import datetime

# 配置SQLite数据库路径
DATABASE = 'blog.db'

def init_db():
    """初始化数据库"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    # 用户表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            birthday DATE,
            bio TEXT,
            avatar_url TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 添加新字段到现有用户表（如果不存在）
    try:
        cursor.execute('ALTER TABLE users ADD COLUMN birthday DATE')
    except sqlite3.OperationalError:
        pass  # 字段已存在
    
    try:
        cursor.execute('ALTER TABLE users ADD COLUMN bio TEXT')
    except sqlite3.OperationalError:
        pass  # 字段已存在
    
    try:
        cursor.execute('ALTER TABLE users ADD COLUMN avatar_url TEXT')
    except sqlite3.OperationalError:
        pass  # 字段已存在
        
    try:
        cursor.execute('ALTER TABLE users ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP')
    except sqlite3.OperationalError:
        pass  # 字段已存在
        
    try:
        cursor.execute('ALTER TABLE users ADD COLUMN updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP')
    except sqlite3.OperationalError:
        pass  # 字段已存在
    
    # 文章分类表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS categories(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 文章表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS posts(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            author_id INTEGER NOT NULL,
            category_id INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (author_id) REFERENCES users (id),
            FOREIGN KEY (category_id) REFERENCES categories (id)
        )
    ''')
    
    # 评论表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS comments(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            post_id INTEGER NOT NULL,
            author_id INTEGER NOT NULL,
            content TEXT NOT NULL,
            parent_id INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (post_id) REFERENCES posts (id) ON DELETE CASCADE,
            FOREIGN KEY (author_id) REFERENCES users (id),
            FOREIGN KEY (parent_id) REFERENCES comments (id) ON DELETE CASCADE
        )
    ''')
    
    # 插入默认用户
    cursor.execute('INSERT OR IGNORE INTO users (username, password) VALUES (?, ?)', 
                   ('admin', '123456'))
    
    # 插入默认分类
    default_categories = [
        ('技术', '技术相关文章'),
        ('生活', '生活感悟与分享'),
        ('项目', '项目开发记录'),
        ('教程', '学习教程与指南')
    ]
    
    for category in default_categories:
        cursor.execute('INSERT OR IGNORE INTO categories (name, description) VALUES (?, ?)', category)
    
    # 获取admin用户ID和分类ID
    admin_user = cursor.execute('SELECT id FROM users WHERE username = ?', ('admin',)).fetchone()
    if admin_user:
        admin_id = admin_user[0]
        
        # 获取分类ID
        tech_cat = cursor.execute('SELECT id FROM categories WHERE name = ?', ('技术',)).fetchone()
        life_cat = cursor.execute('SELECT id FROM categories WHERE name = ?', ('生活',)).fetchone()
        project_cat = cursor.execute('SELECT id FROM categories WHERE name = ?', ('项目',)).fetchone()
        tutorial_cat = cursor.execute('SELECT id FROM categories WHERE name = ?', ('教程',)).fetchone()
        
        # 默认文章数据
        default_articles = [
            # 技术主题 - 2篇
            ('Python Web开发实战指南', '''# Python Web开发实战指南

Python作为一门优雅的编程语言，在Web开发领域有着广泛的应用。

## Flask框架优势

Flask是一个轻量级的Web框架，具有以下特点：
- **简单易学**：最小化的核心功能
- **灵活扩展**：丰富的扩展库生态  
- **高度定制**：可以根据需求自由组合

## 项目架构设计

在实际项目中，我们通常采用MVC架构：
- Models：数据模型层
- Views：视图展示层
- Controllers：业务逻辑层

## 数据库操作

使用SQLAlchemy ORM让数据库操作更加Pythonic，支持多种数据库后端。

## 部署实践

现代Web应用推荐使用Docker容器化部署，确保环境一致性。

这个博客系统就是基于这些最佳实践开发的！''', tech_cat[0] if tech_cat else 1),
            
            ('前端Vue.js最佳实践', '''# Vue.js前端开发最佳实践

Vue.js以其简洁的语法和强大的功能，成为了现代前端开发的热门选择。

## 组件化开发思想

Vue.js的核心是组件化开发：
- 单文件组件(.vue)
- 组件通信机制
- 插槽(Slots)使用

## 状态管理

对于复杂应用，推荐使用Pinia进行状态管理：
- 类型安全的Store
- 开发工具友好
- 更好的树摇优化

## 路由设计

Vue Router提供了强大的路由功能：
- 嵌套路由支持
- 路由守卫机制
- 懒加载优化

## 性能优化技巧

1. 合理使用v-if和v-show
2. 列表渲染使用key
3. 组件懒加载
4. 图片懒加载

前端开发是一个不断学习的过程，Vue.js让这个过程变得更加愉快！''', tech_cat[0] if tech_cat else 1),
            
            # 生活主题 - 2篇
            ('程序员的自我修养', '''# 程序员的自我修养

作为一名程序员，技术能力固然重要，但自我修养同样不可忽视。

## 持续学习的心态

技术日新月异，保持学习热情是程序员的基本素养：
- **跟上技术趋势**：关注新技术动态
- **深入理解原理**：不仅知其然，更要知其所以然
- **实践验证理论**：通过项目实践巩固知识

## 代码质量意识

写出优雅的代码是每个程序员的追求：
- 命名规范要清晰
- 代码结构要合理
- 注释文档要完善

## 沟通协作能力

程序员不是独行侠，团队协作能力很重要：
- 技术文档要清晰
- 代码审查要认真
- 知识分享要积极

## 工作与生活平衡

避免过度加班，保持身心健康：
- 规律的作息时间
- 适当的体育锻炼
- 培养兴趣爱好

程序员的路很长，保持初心，持续成长！''', life_cat[0] if life_cat else 2),
            
            ('远程工作的那些事儿', '''# 远程工作的那些事儿

疫情改变了很多人的工作方式，远程工作也成为了新常态。

## 远程工作的优势

作为一名程序员，远程工作带来了很多便利：
- **时间灵活性**：避免通勤，选择高效时段
- **环境舒适性**：熟悉的工作环境
- **工作生活平衡**：更好的时间分配

## 面临的挑战

但远程工作也有一些挑战需要克服：
- **自律性要求高**：需要强大的自我管理能力
- **沟通成本增加**：缺少面对面交流
- **团队协作**：需要更多的在线协作工具

## 提升效率的技巧

经过实践，总结了一些提升远程工作效率的方法：
1. 固定工作时间，建立规律作息
2. 专门工作空间，区分工作和生活
3. 定期休息，避免长时间连续工作
4. 保持沟通，主动与团队成员交流

## 工具推荐

好的工具能够大大提升远程工作效率：
- 通讯工具：钉钉、腾讯会议
- 协作工具：石墨文档、飞书
- 代码管理：Git、GitHub
- 项目管理：Jira、Trello

远程工作是趋势，学会适应并享受这种工作方式！''', life_cat[0] if life_cat else 2),
            
            # 项目主题 - 2篇
            ('个人博客系统开发记录', '''# 个人博客系统开发记录

这个博客系统是我最近完成的一个项目，记录一下开发过程中的心得体会。

## 项目背景

一直想要一个属于自己的博客平台，能够：
- 自由定制界面风格
- 完全控制数据
- 学习全栈开发技术

于是决定从零开始开发这个博客系统。

## 技术选型

### 后端技术栈
- **Python Flask**：轻量级Web框架
- **SQLite**：嵌入式数据库，简单实用
- **Gunicorn**：WSGI服务器，生产环境部署

### 前端技术栈
- **Vue.js 3**：现代化前端框架
- **Vue Router**：单页应用路由
- **Pinia**：状态管理
- **Element Plus**：UI组件库

### 部署方案
- **Docker**：容器化部署
- **Docker Compose**：多容器编排
- **Nginx**：反向代理和静态文件服务

## 核心功能实现

### 用户系统
- 用户注册登录
- 权限管理（管理员/普通用户）
- 头像上传功能

### 文章系统
- Markdown编辑器
- 文章分类管理
- 分页展示
- 搜索功能

### 评论系统
- 多级评论回复
- 评论管理

## 开发中的挑战

1. **前后端分离架构**：需要设计好API接口
2. **权限控制**：确保安全性
3. **性能优化**：分页、缓存等
4. **部署配置**：Docker网络配置

通过这个项目，我收获了完整的全栈开发经验！''', project_cat[0] if project_cat else 3),
            
            ('Docker容器化部署实践', '''# Docker容器化部署实践

将博客系统进行Docker容器化部署，是一次很好的DevOps实践。

## 为什么选择Docker

Docker容器化有很多优势：
- **环境一致性**：开发、测试、生产环境完全一致
- **部署便利性**：一次构建，到处运行
- **资源利用率**：比虚拟机更轻量

## 容器设计原则

### 单一职责
每个容器只运行一个服务：
- 前端容器：Nginx + 静态文件
- 后端容器：Python Flask应用

### 数据持久化
重要数据使用Volume持久化：
- 数据库文件
- 用户上传文件
- 日志文件

## Docker Compose编排

使用Docker Compose管理多容器应用：
- 网络配置
- 服务依赖
- 环境变量管理

## 部署流程

1. **代码推送**：提交代码到Git仓库
2. **镜像构建**：GitHub Actions自动构建镜像
3. **镜像推送**：推送到容器镜像仓库
4. **服务器部署**：拉取镜像并启动服务

## 遇到的问题

### 网络配置
容器间通信需要正确配置网络，特别是前后端API调用。

### 数据持久化
数据库文件和上传文件需要使用Volume持久化。

### 静态文件服务
头像等静态文件的URL处理需要考虑容器环境。

Docker让部署变得简单而可靠！''', project_cat[0] if project_cat else 3),
            
            # 教程主题 - 2篇
            ('Git版本控制入门教程', '''# Git版本控制入门教程

Git是现代软件开发中必不可少的版本控制工具，掌握Git是每个开发者的基本功。

## Git基础概念

### 仓库（Repository）
Git仓库是一个包含所有版本历史的目录：
- **本地仓库**：在你的计算机上
- **远程仓库**：在GitHub、GitLab等平台上

### 工作区和暂存区
- **工作区**：你实际编辑文件的地方
- **暂存区**：准备提交的文件区域
- **版本库**：已提交的版本历史

## 常用命令详解

### 初始化和克隆
```bash
# 初始化新仓库
git init

# 克隆远程仓库
git clone https://github.com/user/repo.git
```

### 基本操作
```bash
# 查看状态
git status

# 添加文件到暂存区
git add filename
git add .  # 添加所有文件

# 提交更改
git commit -m "提交信息"

# 查看历史
git log
```

### 分支操作
```bash
# 查看分支
git branch

# 创建新分支
git branch feature-name

# 切换分支
git checkout feature-name

# 创建并切换到新分支
git checkout -b feature-name
```

## 最佳实践

### 提交信息规范
- 使用现在时："添加功能"而不是"添加了功能"
- 保持简洁明了
- 可以使用约定式提交格式

### 分支策略
- **main/master**：主分支，保持稳定
- **develop**：开发分支
- **feature/**：功能分支
- **hotfix/**：紧急修复分支

Git是开发者的好朋友，熟练掌握会让开发效率大大提升！''', tutorial_cat[0] if tutorial_cat else 4),
            
            ('Markdown写作完全指南', '''# Markdown写作完全指南

Markdown是一种轻量级标记语言，使用简单的语法就能创建格式丰富的文档。

## 基础语法

### 标题
```markdown
# 一级标题
## 二级标题
### 三级标题
```

### 文本格式
```markdown
**粗体文本**
*斜体文本*
***粗斜体文本***
~~删除线~~
`行内代码`
```

### 列表

#### 无序列表
```markdown
- 第一项
- 第二项
  - 子项目1
  - 子项目2
- 第三项
```

#### 有序列表
```markdown
1. 第一项
2. 第二项
   1. 子项目1
   2. 子项目2
3. 第三项
```

### 链接和图片
```markdown
[链接文本](https://example.com)
![图片描述](image-url.jpg)
```

## 高级语法

### 代码块
````markdown
```python
def hello_world():
    print("Hello, World!")
```
````

### 表格
```markdown
| 表头1 | 表头2 | 表头3 |
|-------|-------|-------|
| 内容1 | 内容2 | 内容3 |
| 内容4 | 内容5 | 内容6 |
```

### 引用
```markdown
> 这是一个引用
> 
> 可以有多行
```

## 工具推荐

### 编辑器
- **Typora**：所见即所得编辑器
- **Mark Text**：实时预览编辑器
- **VS Code**：配合Markdown扩展
- **Obsidian**：知识管理工具

## 写作技巧

### 结构化思维
1. 确定文章主题
2. 列出大纲结构
3. 逐步完善内容
4. 检查格式和语法

### 善用格式
- 使用标题分层次
- 列表让内容更清晰
- 代码块突出技术内容
- 表格整理数据信息

Markdown让写作变得简单而高效，是技术写作的最佳选择！''', tutorial_cat[0] if tutorial_cat else 4)
        ]
        
        # 插入默认文章
        for title, content, category_id in default_articles:
            cursor.execute('''
                INSERT OR IGNORE INTO posts (title, content, author_id, category_id, created_at, updated_at) 
                VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
            ''', (title, content, admin_id, category_id))
    
    conn.commit()
    conn.close()

def get_db_connection():
    """获取数据库连接"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def is_admin(username, password):
    return username == 'admin' and password == '123456'

def check_user(username, password):
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE username = ? AND password = ?', 
                       (username, password)).fetchone()
    conn.close()
    return user is not None

def user_exists(username):
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
    conn.close()
    return user is not None

def add_user(username, password):
    try:
        conn = get_db_connection()
        conn.execute('INSERT INTO users (username, password) VALUES (?, ?)', 
                    (username, password))
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        return False

def get_all_users():
    conn = get_db_connection()
    users = conn.execute('SELECT * FROM users').fetchall()
    conn.close()
    return users

def delete_user(user_id):
    """删除用户及其所有文章和评论"""
    try:
        conn = get_db_connection()
        user = conn.execute('SELECT username FROM users WHERE id = ?', (user_id,)).fetchone()
        if user and user['username'] == 'admin':
            conn.close()
            return False
        
        # 开始事务
        # 1. 先删除该用户的所有评论
        conn.execute('DELETE FROM comments WHERE author_id = ?', (user_id,))
        
        # 2. 删除该用户的所有文章
        conn.execute('DELETE FROM posts WHERE author_id = ?', (user_id,))
        
        # 3. 最后删除用户
        conn.execute('DELETE FROM users WHERE id = ?', (user_id,))
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"删除用户失败: {e}")
        return False

def get_user_by_id(user_id):
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
    conn.close()
    return user

def get_user_by_username(username):
    """根据用户名获取用户信息"""
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
    conn.close()
    return user

def get_user_id_by_username(username):
    """根据用户名获取用户ID"""
    conn = get_db_connection()
    user = conn.execute('SELECT id FROM users WHERE username = ?', (username,)).fetchone()
    conn.close()
    return user['id'] if user else None

# === 新增：文章相关函数 ===

def get_all_categories():
    """获取所有文章分类"""
    conn = get_db_connection()
    categories = conn.execute('SELECT * FROM categories ORDER BY name').fetchall()
    conn.close()
    return categories

def get_all_posts(category_id=None):
    """获取所有文章或指定分类的文章"""
    conn = get_db_connection()
    if category_id:
        posts = conn.execute('''
            SELECT p.*, COALESCE(u.username, '已删除用户') as author, c.name as category_name
            FROM posts p
            LEFT JOIN users u ON p.author_id = u.id
            LEFT JOIN categories c ON p.category_id = c.id
            WHERE p.category_id = ?
            ORDER BY p.created_at DESC
        ''', (category_id,)).fetchall()
    else:
        posts = conn.execute('''
            SELECT p.*, COALESCE(u.username, '已删除用户') as author, c.name as category_name
            FROM posts p
            LEFT JOIN users u ON p.author_id = u.id
            LEFT JOIN categories c ON p.category_id = c.id
            ORDER BY p.created_at DESC
        ''').fetchall()
    conn.close()
    return posts

def get_posts_count(category_id=None):
    """获取文章总数"""
    conn = get_db_connection()
    if category_id:
        result = conn.execute('''
            SELECT COUNT(*) FROM posts WHERE category_id = ?
        ''', (category_id,)).fetchone()
    else:
        result = conn.execute('''
            SELECT COUNT(*) FROM posts
        ''').fetchone()
    conn.close()
    return result[0] if result else 0

def get_posts_paginated(page=1, per_page=7, category_id=None):
    """获取分页文章数据"""
    conn = get_db_connection()
    offset = (page - 1) * per_page
    
    if category_id:
        posts = conn.execute('''
            SELECT p.*, COALESCE(u.username, '已删除用户') as author, c.name as category_name
            FROM posts p
            LEFT JOIN users u ON p.author_id = u.id
            LEFT JOIN categories c ON p.category_id = c.id
            WHERE p.category_id = ?
            ORDER BY p.created_at DESC
            LIMIT ? OFFSET ?
        ''', (category_id, per_page, offset)).fetchall()
    else:
        posts = conn.execute('''
            SELECT p.*, COALESCE(u.username, '已删除用户') as author, c.name as category_name
            FROM posts p
            LEFT JOIN users u ON p.author_id = u.id
            LEFT JOIN categories c ON p.category_id = c.id
            ORDER BY p.created_at DESC
            LIMIT ? OFFSET ?
        ''', (per_page, offset)).fetchall()
    conn.close()
    return posts

def create_post(title, content, author_id, category_id=None):
    """创建新文章"""
    conn = get_db_connection()
    
    # 使用当前时间，格式化为易读格式
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    try:
        conn.execute('''
            INSERT INTO posts (title, content, author_id, category_id, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (title, content, author_id, category_id, current_time, current_time))
        conn.commit()
        return True
    except Exception as e:
        print(f"创建文章失败: {e}")
        return False
    finally:
        conn.close()

def get_post_by_id(post_id):
    """根据ID获取文章详情"""
    conn = get_db_connection()
    post = conn.execute('''
        SELECT p.*, COALESCE(u.username, '已删除用户') as author, c.name as category_name
        FROM posts p
        LEFT JOIN users u ON p.author_id = u.id
        LEFT JOIN categories c ON p.category_id = c.id
        WHERE p.id = ?
    ''', (post_id,)).fetchone()
    conn.close()
    return post

def update_post(post_id, title, content, category_id=None):
    """更新文章"""
    conn = get_db_connection()
    
    # 更新时间
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    try:
        conn.execute('''
            UPDATE posts 
            SET title = ?, content = ?, category_id = ?, updated_at = ?
            WHERE id = ?
        ''', (title, content, category_id, current_time, post_id))
        conn.commit()
        return True
    except Exception as e:
        print(f"更新文章失败: {e}")
        return False
    finally:
        conn.close()

def delete_post(post_id):
    """删除文章"""
    try:
        conn = get_db_connection()
        conn.execute('DELETE FROM posts WHERE id = ?', (post_id,))
        conn.commit()
        conn.close()
        return True
    except Exception:
        return False

def get_posts_by_author(author_id):
    """获取指定作者的文章"""
    conn = get_db_connection()
    posts = conn.execute('''
        SELECT p.*, u.username as author, c.name as category_name
        FROM posts p
        JOIN users u ON p.author_id = u.id
        LEFT JOIN categories c ON p.category_id = c.id
        WHERE p.author_id = ?
        ORDER BY p.created_at DESC
    ''', (author_id,)).fetchall()
    conn.close()
    return posts

# ============= 评论相关函数 =============

def create_comment(post_id, author_id, content, parent_id=None):
    """创建评论"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO comments (post_id, author_id, content, parent_id) 
            VALUES (?, ?, ?, ?)
        ''', (post_id, author_id, content, parent_id))
        conn.commit()
        comment_id = cursor.lastrowid
        conn.close()
        return comment_id
    except Exception as e:
        print(f"创建评论错误: {e}")
        return None

def get_comments_by_post(post_id):
    """获取文章的所有评论（按时间排序）"""
    try:
        conn = get_db_connection()
        comments = conn.execute('''
            SELECT c.*, u.username as author_name
            FROM comments c
            JOIN users u ON c.author_id = u.id
            WHERE c.post_id = ?
            ORDER BY c.created_at ASC
        ''', (post_id,)).fetchall()
        conn.close()
        return comments
    except Exception as e:
        print(f"获取评论错误: {e}")
        return []

def get_comment_by_id(comment_id):
    """根据ID获取评论"""
    try:
        conn = get_db_connection()
        comment = conn.execute('''
            SELECT c.*, u.username as author_name
            FROM comments c
            JOIN users u ON c.author_id = u.id
            WHERE c.id = ?
        ''', (comment_id,)).fetchone()
        conn.close()
        return comment
    except Exception as e:
        print(f"获取评论错误: {e}")
        return None

def update_comment(comment_id, content):
    """更新评论内容"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE comments 
            SET content = ?
            WHERE id = ?
        ''', (content, comment_id))
        conn.commit()
        success = cursor.rowcount > 0
        conn.close()
        return success
    except Exception as e:
        print(f"更新评论错误: {e}")
        return False

def delete_comment(comment_id):
    """删除评论（会级联删除回复）"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM comments WHERE id = ?', (comment_id,))
        conn.commit()
        success = cursor.rowcount > 0
        conn.close()
        return success
    except Exception as e:
        print(f"删除评论错误: {e}")
        return False

def get_comment_count_by_post(post_id):
    """获取文章的评论总数"""
    try:
        conn = get_db_connection()
        count = conn.execute('''
            SELECT COUNT(*) as count
            FROM comments
            WHERE post_id = ?
        ''', (post_id,)).fetchone()
        conn.close()
        return count['count'] if count else 0
    except Exception as e:
        print(f"获取评论数量错误: {e}")
        return 0

def get_recent_comments(limit=10):
    """获取最近的评论"""
    try:
        conn = get_db_connection()
        comments = conn.execute('''
            SELECT c.*, u.username as author_name, p.title as post_title
            FROM comments c
            JOIN users u ON c.author_id = u.id
            JOIN posts p ON c.post_id = p.id
            ORDER BY c.created_at DESC
            LIMIT ?
        ''', (limit,)).fetchall()
        conn.close()
        return comments
    except Exception as e:
        print(f"获取最近评论错误: {e}")
        return []

def get_all_comments(page=1, per_page=20, post_id=None, author_id=None):
    """获取所有评论，支持分页和筛选"""
    try:
        conn = get_db_connection()
        offset = (page - 1) * per_page
        
        # 构建基础查询
        base_query = '''
            SELECT c.*, u.username as author_name, p.title as post_title
            FROM comments c
            JOIN users u ON c.author_id = u.id
            JOIN posts p ON c.post_id = p.id
        '''
        
        count_query = '''
            SELECT COUNT(*) as total
            FROM comments c
            JOIN users u ON c.author_id = u.id
            JOIN posts p ON c.post_id = p.id
        '''
        
        # 添加筛选条件
        conditions = []
        params = []
        
        if post_id:
            conditions.append('c.post_id = ?')
            params.append(post_id)
            
        if author_id:
            conditions.append('c.author_id = ?')
            params.append(author_id)
        
        if conditions:
            where_clause = ' WHERE ' + ' AND '.join(conditions)
            base_query += where_clause
            count_query += where_clause
        
        # 获取总数
        total_count = conn.execute(count_query, params).fetchone()['total']
        
        # 获取评论列表
        base_query += ' ORDER BY c.created_at DESC LIMIT ? OFFSET ?'
        comments = conn.execute(base_query, params + [per_page, offset]).fetchall()
        
        conn.close()
        
        return {
            'comments': comments,
            'total': total_count,
            'page': page,
            'per_page': per_page,
            'total_pages': (total_count + per_page - 1) // per_page
        }
    except Exception as e:
        print(f"获取所有评论错误: {e}")
        return {
            'comments': [],
            'total': 0,
            'page': page,
            'per_page': per_page,
            'total_pages': 0
        }

# ============= 搜索相关函数 =============

def search_posts(keyword, page=1, per_page=10, category_id=None, author_id=None):
    """根据关键字搜索文章，支持分页和筛选"""
    try:
        conn = get_db_connection()
        offset = (page - 1) * per_page
        
        # 构建基础查询
        base_query = '''
            SELECT p.*, u.username as author, c.name as category_name
            FROM posts p
            JOIN users u ON p.author_id = u.id
            LEFT JOIN categories c ON p.category_id = c.id
            WHERE (p.title LIKE ? OR p.content LIKE ?)
        '''
        
        count_query = '''
            SELECT COUNT(*) as total
            FROM posts p
            JOIN users u ON p.author_id = u.id
            LEFT JOIN categories c ON p.category_id = c.id
            WHERE (p.title LIKE ? OR p.content LIKE ?)
        '''
        
        # 准备搜索参数
        search_pattern = f'%{keyword}%'
        params = [search_pattern, search_pattern]
        
        # 添加额外筛选条件
        if category_id:
            base_query += ' AND p.category_id = ?'
            count_query += ' AND p.category_id = ?'
            params.append(category_id)
            
        if author_id:
            base_query += ' AND p.author_id = ?'
            count_query += ' AND p.author_id = ?'
            params.append(author_id)
        
        # 获取总数
        total_count = conn.execute(count_query, params).fetchone()['total']
        
        # 获取文章列表
        base_query += ' ORDER BY p.created_at DESC LIMIT ? OFFSET ?'
        posts = conn.execute(base_query, params + [per_page, offset]).fetchall()
        
        conn.close()
        
        return {
            'posts': posts,
            'total': total_count,
            'page': page,
            'per_page': per_page,
            'total_pages': (total_count + per_page - 1) // per_page,
            'keyword': keyword
        }
    except Exception as e:
        print(f"搜索文章错误: {e}")
        return {
            'posts': [],
            'total': 0,
            'page': page,
            'per_page': per_page,
            'total_pages': 0,
            'keyword': keyword
        }

def search_posts_by_title(keyword, limit=10):
    """根据标题搜索文章（用于自动补全）"""
    try:
        conn = get_db_connection()
        posts = conn.execute('''
            SELECT p.id, p.title, u.username as author, c.name as category_name
            FROM posts p
            JOIN users u ON p.author_id = u.id
            LEFT JOIN categories c ON p.category_id = c.id
            WHERE p.title LIKE ?
            ORDER BY p.created_at DESC
            LIMIT ?
        ''', (f'%{keyword}%', limit)).fetchall()
        conn.close()
        return posts
    except Exception as e:
        print(f"按标题搜索文章错误: {e}")
        return []

def get_search_suggestions(keyword, limit=5):
    """获取搜索建议（基于标题和分类）"""
    try:
        conn = get_db_connection()
        
        # 搜索相关标题
        title_suggestions = conn.execute('''
            SELECT DISTINCT title as suggestion, 'post' as type, id
            FROM posts
            WHERE title LIKE ?
            ORDER BY created_at DESC
            LIMIT ?
        ''', (f'%{keyword}%', limit)).fetchall()
        
        # 搜索相关分类
        category_suggestions = conn.execute('''
            SELECT DISTINCT name as suggestion, 'category' as type, id
            FROM categories
            WHERE name LIKE ?
            LIMIT ?
        ''', (f'%{keyword}%', limit)).fetchall()
        
        conn.close()
        
        # 合并建议
        suggestions = []
        for item in title_suggestions:
            suggestions.append(dict(item))
        for item in category_suggestions:
            suggestions.append(dict(item))
            
        return suggestions[:limit]
    except Exception as e:
        print(f"获取搜索建议错误: {e}")
        return []

def get_popular_keywords(limit=10):
    """获取热门关键词（基于文章标题中的常见词汇）"""
    try:
        conn = get_db_connection()
        
        # 获取所有文章标题
        titles = conn.execute('SELECT title FROM posts').fetchall()
        conn.close()
        
        # 简单的关键词提取（可以优化）
        keywords = {}
        for title_row in titles:
            title = title_row['title']
            # 简单分词（按空格和常见标点符号）
            words = title.replace('，', ' ').replace('。', ' ').replace('！', ' ').replace('？', ' ').split()
            for word in words:
                word = word.strip()
                if len(word) > 1:  # 忽略单字符
                    keywords[word] = keywords.get(word, 0) + 1
        
        # 按频率排序
        popular = sorted(keywords.items(), key=lambda x: x[1], reverse=True)
        return [{'keyword': k, 'count': v} for k, v in popular[:limit]]
    except Exception as e:
        print(f"获取热门关键词错误: {e}")
        return []

# ============= 用户资料相关函数 =============

def update_user_profile(user_id, birthday=None, bio=None, avatar_url=None):
    """更新用户资料"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 检查表结构中是否有 updated_at 字段
        table_info = cursor.execute("PRAGMA table_info(users)").fetchall()
        has_updated_at = any(column[1] == 'updated_at' for column in table_info)
        
        # 构建更新语句
        update_fields = []
        params = []
        
        if birthday is not None:
            update_fields.append('birthday = ?')
            params.append(birthday)
            
        if bio is not None:
            update_fields.append('bio = ?')
            params.append(bio)
            
        if avatar_url is not None:
            update_fields.append('avatar_url = ?')
            params.append(avatar_url)
        
        if not update_fields:
            conn.close()
            return False
        
        # 只有当字段存在时才添加更新时间
        if has_updated_at:
            update_fields.append('updated_at = ?')
            params.append(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        
        # 添加用户ID
        params.append(user_id)
        
        query = f"UPDATE users SET {', '.join(update_fields)} WHERE id = ?"
        cursor.execute(query, params)
        conn.commit()
        success = cursor.rowcount > 0
        conn.close()
        return success
    except Exception as e:
        print(f"更新用户资料错误: {e}")
        return False

def get_user_profile(user_id):
    """获取用户资料"""
    try:
        conn = get_db_connection()
        user = conn.execute('''
            SELECT id, username, birthday, bio, avatar_url, created_at, updated_at
            FROM users 
            WHERE id = ?
        ''', (user_id,)).fetchone()
        conn.close()
        return user
    except Exception as e:
        print(f"获取用户资料错误: {e}")
        return None

def get_user_profile_by_username(username):
    """根据用户名获取用户资料"""
    try:
        conn = get_db_connection()
        user = conn.execute('''
            SELECT id, username, birthday, bio, avatar_url, created_at, updated_at
            FROM users 
            WHERE username = ?
        ''', (username,)).fetchone()
        conn.close()
        return user
    except Exception as e:
        print(f"根据用户名获取用户资料错误: {e}")
        return None

def update_user_avatar(user_id, avatar_url):
    """更新用户头像"""
    try:
        print(f"尝试更新用户头像 - 用户ID: {user_id}, 头像URL: {avatar_url}")  # 调试日志
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 先检查用户是否存在
        user_check = cursor.execute('SELECT id FROM users WHERE id = ?', (user_id,)).fetchone()
        if not user_check:
            print(f"错误: 用户ID {user_id} 不存在")
            conn.close()
            return False
        
        # 检查表结构中是否有 updated_at 字段
        table_info = cursor.execute("PRAGMA table_info(users)").fetchall()
        has_updated_at = any(column[1] == 'updated_at' for column in table_info)
        
        if has_updated_at:
            # 如果有 updated_at 字段，使用它
            cursor.execute('''
                UPDATE users 
                SET avatar_url = ?, updated_at = ?
                WHERE id = ?
            ''', (avatar_url, datetime.now().strftime('%Y-%m-%d %H:%M:%S'), user_id))
        else:
            # 如果没有 updated_at 字段，只更新 avatar_url
            cursor.execute('''
                UPDATE users 
                SET avatar_url = ?
                WHERE id = ?
            ''', (avatar_url, user_id))
        
        conn.commit()
        success = cursor.rowcount > 0
        
        print(f"更新操作结果 - 受影响行数: {cursor.rowcount}, 成功: {success}")  # 调试日志
        
        # 验证更新结果
        if success:
            updated_user = cursor.execute('SELECT avatar_url FROM users WHERE id = ?', (user_id,)).fetchone()
            print(f"验证更新结果 - 新头像URL: {updated_user[0] if updated_user else 'None'}")
        
        conn.close()
        return success
    except Exception as e:
        print(f"更新用户头像错误: {e}")
        import traceback
        traceback.print_exc()  # 打印完整错误堆栈
        return False

def update_user_birthday(user_id, birthday):
    """更新用户生日"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 检查表结构中是否有 updated_at 字段
        table_info = cursor.execute("PRAGMA table_info(users)").fetchall()
        has_updated_at = any(column[1] == 'updated_at' for column in table_info)
        
        if has_updated_at:
            cursor.execute('''
                UPDATE users 
                SET birthday = ?, updated_at = ?
                WHERE id = ?
            ''', (birthday, datetime.now().strftime('%Y-%m-%d %H:%M:%S'), user_id))
        else:
            cursor.execute('''
                UPDATE users 
                SET birthday = ?
                WHERE id = ?
            ''', (birthday, user_id))
            
        conn.commit()
        success = cursor.rowcount > 0
        conn.close()
        return success
    except Exception as e:
        print(f"更新用户生日错误: {e}")
        return False

def update_user_bio(user_id, bio):
    """更新用户个性签名"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 检查表结构中是否有 updated_at 字段
        table_info = cursor.execute("PRAGMA table_info(users)").fetchall()
        has_updated_at = any(column[1] == 'updated_at' for column in table_info)
        
        if has_updated_at:
            cursor.execute('''
                UPDATE users 
                SET bio = ?, updated_at = ?
                WHERE id = ?
            ''', (bio, datetime.now().strftime('%Y-%m-%d %H:%M:%S'), user_id))
        else:
            cursor.execute('''
                UPDATE users 
                SET bio = ?
                WHERE id = ?
            ''', (bio, user_id))
            
        conn.commit()
        success = cursor.rowcount > 0
        conn.close()
        return success
    except Exception as e:
        print(f"更新用户个性签名错误: {e}")
        return False

def get_site_stats():
    """获取网站统计信息"""
    try:
        conn = get_db_connection()
        
        # 获取文章总数
        total_posts = conn.execute('SELECT COUNT(*) as count FROM posts').fetchone()['count']
        
        # 获取用户总数
        total_users = conn.execute('SELECT COUNT(*) as count FROM users').fetchone()['count']
        
        # 获取分类总数
        total_categories = conn.execute('SELECT COUNT(*) as count FROM categories').fetchone()['count']
        
        # 获取评论总数
        total_comments = conn.execute('SELECT COUNT(*) as count FROM comments').fetchone()['count']
        
        # 获取最新文章
        latest_posts = conn.execute('''
            SELECT p.*, u.username as author, c.name as category_name
            FROM posts p
            LEFT JOIN users u ON p.author_id = u.id
            LEFT JOIN categories c ON p.category_id = c.id
            ORDER BY p.created_at DESC
            LIMIT 5
        ''').fetchall()
        
        conn.close()
        
        return {
            'total_posts': total_posts,
            'total_users': total_users,
            'total_categories': total_categories,
            'total_comments': total_comments,
            'latest_posts': [dict(post) for post in latest_posts]
        }
    except Exception as e:
        print(f"获取网站统计信息错误: {e}")
        return {
            'total_posts': 0,
            'total_users': 0,
            'total_categories': 0,
            'total_comments': 0,
            'latest_posts': []
        }

def check_user_table_structure():
    """检查用户表结构"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 获取用户表结构
        table_info = cursor.execute("PRAGMA table_info(users)").fetchall()
        print("用户表结构:")
        for column in table_info:
            print(f"  列ID: {column[0]}, 名称: {column[1]}, 类型: {column[2]}, 非空: {column[3]}, 默认值: {column[4]}")
        
        # 检查是否有测试用户
        users = cursor.execute("SELECT id, username, avatar_url FROM users LIMIT 3").fetchall()
        print("现有用户:")
        for user in users:
            print(f"  ID: {user[0]}, 用户名: {user[1]}, 头像: {user[2] if len(user) > 2 else 'None'}")
        
        conn.close()
    except Exception as e:
        print(f"检查用户表结构错误: {e}")
        import traceback
        traceback.print_exc()