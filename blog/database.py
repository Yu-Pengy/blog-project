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
        ('学习', '学习笔记与心得'),
        ('随笔', '随心所欲的文字')
    ]
    
    for category in default_categories:
        cursor.execute('INSERT OR IGNORE INTO categories (name, description) VALUES (?, ?)', category)
    
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
    try:
        conn = get_db_connection()
        user = conn.execute('SELECT username FROM users WHERE id = ?', (user_id,)).fetchone()
        if user and user['username'] == 'admin':
            conn.close()
            return False
        
        conn.execute('DELETE FROM users WHERE id = ?', (user_id,))
        conn.commit()
        conn.close()
        return True
    except Exception:
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
            SELECT p.*, u.username as author, c.name as category_name
            FROM posts p
            JOIN users u ON p.author_id = u.id
            LEFT JOIN categories c ON p.category_id = c.id
            WHERE p.category_id = ?
            ORDER BY p.created_at DESC
        ''', (category_id,)).fetchall()
    else:
        posts = conn.execute('''
            SELECT p.*, u.username as author, c.name as category_name
            FROM posts p
            JOIN users u ON p.author_id = u.id
            LEFT JOIN categories c ON p.category_id = c.id
            ORDER BY p.created_at DESC
        ''').fetchall()
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
        SELECT p.*, u.username as author, c.name as category_name
        FROM posts p
        JOIN users u ON p.author_id = u.id
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