from flask import Flask, request, session, jsonify, send_from_directory
from flask_cors import CORS
from database import *
from datetime import datetime
import markdown
from markupsafe import Markup
import os
import time
from werkzeug.utils import secure_filename

# 初始化flask对象，并传入参数
app = Flask(__name__)
CORS(app, supports_credentials=True, resources={
    r"/api/*": {"origins": "*"},
    r"/static/*": {"origins": "*"}
})  # 允许跨域并支持cookies，包括静态文件
app.secret_key = 'Sf8x#mK9$vL2@nQ7*pR4!wE6&tY1+uI3'  # 用于session加密

# 文件上传配置
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

# 确保上传目录存在
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    """检查文件扩展名是否允许"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_full_avatar_url(avatar_url):
    """处理头像URL，返回适合前端使用的URL"""
    if not avatar_url:
        return None
    
    # 如果已经是完整URL，直接返回
    if avatar_url.startswith('http://') or avatar_url.startswith('https://'):
        return avatar_url
    
    # 如果是文件名，转换为静态文件路径
    if not avatar_url.startswith('/static/'):
        avatar_url = f'/static/uploads/{avatar_url}'
    
    return avatar_url

# Markdown渲染函数
def render_markdown(text):
    """将Markdown文本转换为HTML"""
    if not text:
        return ""
    
    md = markdown.Markdown(extensions=[
        'codehilite', 'fenced_code', 'tables', 
        'toc', 'nl2br', 'sane_lists'
    ], extension_configs={
        'codehilite': {
            'css_class': 'codehilite',
            'use_pygments': True,
            'noclasses': False,
            'linenums': False
        }
    })
    
    return md.convert(text.strip())

@app.route('/')
def health_check():
    return {'status': 'healthy', 'message': 'Blog backend is running', 'version': '1.0'}

# ============= 认证API =============

@app.route('/api/auth/login', methods=['POST'])
def api_login():
    """登录API"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'message': '请求数据格式错误'}), 400
            
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({'success': False, 'message': '请填写完整的用户名和密码'}), 400
        
        print(f"登录尝试: {username}")  # 调试信息
        
        # 检查管理员登录
        if is_admin(username, password):
            user_id = get_user_id_by_username(username)
            user = get_user_by_username(username)
            session['username'] = username
            session['user_id'] = user_id
            session['is_admin'] = True
            
            # 处理头像URL
            avatar_url = dict(user).get('avatar_url') if user else None
            
            return jsonify({
                'success': True,
                'message': '管理员登录成功',
                'user': {
                    'username': username,
                    'is_admin': True,
                    'avatar_url': get_full_avatar_url(avatar_url)
                }
            })
        
        # 检查普通用户登录
        elif check_user(username, password):
            user_id = get_user_id_by_username(username)
            user = get_user_by_username(username)
            session['username'] = username
            session['user_id'] = user_id
            session['is_admin'] = False
            
            # 处理头像URL
            avatar_url = dict(user).get('avatar_url') if user else None
            
            return jsonify({
                'success': True,
                'message': '登录成功',
                'user': {
                    'username': username,
                    'is_admin': False,
                    'avatar_url': get_full_avatar_url(avatar_url)
                }
            })
        
        # 用户存在但密码错误
        elif user_exists(username):
            return jsonify({'success': False, 'message': '密码错误'}), 401
        
        # 用户不存在
        else:
            return jsonify({'success': False, 'message': '用户不存在'}), 401
            
    except Exception as e:
        print(f"登录错误: {e}")
        return jsonify({'success': False, 'message': '服务器错误'}), 500

@app.route('/api/auth/logout', methods=['POST'])
def api_logout():
    """登出API"""
    try:
        session.clear()
        return jsonify({'success': True, 'message': '登出成功'})
    except Exception as e:
        print(f"登出错误: {e}")
        return jsonify({'success': False, 'message': '登出失败'}), 500

@app.route('/api/auth/register', methods=['POST'])
def api_register():
    """注册API"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'message': '请求数据格式错误'}), 400
            
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({'success': False, 'message': '请填写完整的用户名和密码'}), 400
        
        if user_exists(username):
            return jsonify({'success': False, 'message': '用户名已存在'}), 400
        
        if add_user(username, password):
            return jsonify({'success': True, 'message': '注册成功'})
        else:
            return jsonify({'success': False, 'message': '注册失败'}), 500
            
    except Exception as e:
        print(f"注册错误: {e}")
        return jsonify({'success': False, 'message': '服务器错误'}), 500

@app.route('/api/auth/user', methods=['GET'])
def api_current_user():
    """获取当前用户信息"""
    try:
        if 'username' in session:
            username = session['username']
            # 获取用户详细信息包括头像
            user = get_user_by_username(username)
            
            avatar_url = None
            if user:
                avatar_url = dict(user).get('avatar_url')
            
            return jsonify({
                'logged_in': True,
                'username': username,
                'is_admin': session.get('is_admin', False),
                'avatar_url': get_full_avatar_url(avatar_url)
            })
        else:
            return jsonify({'logged_in': False})
    except Exception as e:
        print(f"获取用户信息错误: {e}")
        return jsonify({'logged_in': False}), 500

# ============= 文章API =============

@app.route('/api/posts', methods=['GET'])
def api_posts():
    """获取所有文章API - 支持分页"""
    try:
        # 分页参数
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 7))  # 默认每页7篇文章
        category_id = request.args.get('category_id')
        
        # 获取文章总数
        if category_id:
            total_posts = get_posts_count(int(category_id))
            posts = get_posts_paginated(page=page, per_page=per_page, category_id=int(category_id))
        else:
            total_posts = get_posts_count()
            posts = get_posts_paginated(page=page, per_page=per_page)
        
        # 计算分页信息
        total_pages = (total_posts + per_page - 1) // per_page  # 向上取整
        has_prev = page > 1
        has_next = page < total_pages
        
        # 转换为字典列表并添加预览内容和作者头像
        posts_list = []
        for post in posts:
            post_dict = dict(post)
            # 添加Markdown渲染的预览
            if post_dict.get('content'):
                content = post_dict['content']
                preview_content = content[:200] + '...' if len(content) > 200 else content
                post_dict['preview_html'] = render_markdown(preview_content)
            
            # 获取作者头像信息
            if post_dict.get('author'):
                author_info = get_user_by_username(post_dict['author'])
                if author_info:
                    avatar_url = dict(author_info).get('avatar_url')
                    post_dict['author_avatar'] = avatar_url
                else:
                    post_dict['author_avatar'] = None
            else:
                post_dict['author_avatar'] = None
            
            posts_list.append(post_dict)
        
        return jsonify({
            'posts': posts_list,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': total_posts,
                'total_pages': total_pages,
                'has_prev': has_prev,
                'has_next': has_next,
                'prev_page': page - 1 if has_prev else None,
                'next_page': page + 1 if has_next else None
            }
        })
    except Exception as e:
        print(f"获取文章错误: {e}")
        return jsonify({'error': '获取文章失败'}), 500

@app.route('/api/posts/<int:post_id>', methods=['GET'])
def api_post_detail(post_id):
    """获取文章详情API"""
    try:
        post = get_post_by_id(post_id)
        if not post:
            return jsonify({'error': '文章不存在'}), 404
        
        post_dict = dict(post)
        # 渲染Markdown内容
        if post_dict.get('content'):
            post_dict['content_html'] = render_markdown(post_dict['content'])
        
        # 获取作者头像信息
        if post_dict.get('author'):
            author_info = get_user_by_username(post_dict['author'])
            if author_info:
                avatar_url = dict(author_info).get('avatar_url')
                post_dict['author_avatar'] = avatar_url
            else:
                post_dict['author_avatar'] = None
        else:
            post_dict['author_avatar'] = None
        
        return jsonify(post_dict)
    except Exception as e:
        print(f"获取文章详情错误: {e}")
        return jsonify({'error': '获取文章详情失败'}), 500

@app.route('/api/posts', methods=['POST'])
def api_create_post():
    """创建文章API"""
    if 'username' not in session:
        return jsonify({'error': '未登录'}), 401
    
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': '请求数据格式错误'}), 400
            
        title = data.get('title', '').strip()
        content = data.get('content', '').strip()
        category_id = data.get('category_id')
        
        if not title or not content:
            return jsonify({'error': '标题和内容不能为空'}), 400
        
        author_id = get_user_id_by_username(session['username'])
        
        if create_post(title, content, author_id, category_id):
            return jsonify({'success': True, 'message': '文章发布成功'})
        else:
            return jsonify({'error': '发布失败'}), 500
    except Exception as e:
        print(f"创建文章错误: {e}")
        return jsonify({'error': '创建文章失败'}), 500

@app.route('/api/posts/<int:post_id>', methods=['PUT'])
def api_update_post(post_id):
    """更新文章API"""
    if 'username' not in session:
        return jsonify({'error': '未登录'}), 401
    
    try:
        post = get_post_by_id(post_id)
        if not post:
            return jsonify({'error': '文章不存在'}), 404
        
        # 检查权限
        author_id = get_user_id_by_username(session['username'])
        if post['author_id'] != author_id and not session.get('is_admin'):
            return jsonify({'error': '无权限编辑此文章'}), 403
        
        data = request.get_json()
        if not data:
            return jsonify({'error': '请求数据格式错误'}), 400
            
        title = data.get('title', '').strip()
        content = data.get('content', '').strip()
        category_id = data.get('category_id')
        
        if not title or not content:
            return jsonify({'error': '标题和内容不能为空'}), 400
        
        if update_post(post_id, title, content, category_id):
            return jsonify({'success': True, 'message': '文章更新成功'})
        else:
            return jsonify({'error': '更新失败'}), 500
    except Exception as e:
        print(f"更新文章错误: {e}")
        return jsonify({'error': '更新文章失败'}), 500

@app.route('/api/posts/<int:post_id>', methods=['DELETE'])
def api_delete_post(post_id):
    """删除文章API"""
    if 'username' not in session:
        return jsonify({'error': '未登录'}), 401
    
    try:
        post = get_post_by_id(post_id)
        if not post:
            return jsonify({'error': '文章不存在'}), 404
        
        # 检查权限
        author_id = get_user_id_by_username(session['username'])
        if post['author_id'] != author_id and not session.get('is_admin'):
            return jsonify({'error': '无权限删除此文章'}), 403
        
        if delete_post(post_id):
            return jsonify({'success': True, 'message': '文章删除成功'})
        else:
            return jsonify({'error': '删除失败'}), 500
    except Exception as e:
        print(f"删除文章错误: {e}")
        return jsonify({'error': '删除文章失败'}), 500

@app.route('/api/my-posts', methods=['GET'])
def api_my_posts():
    """获取我的文章API"""
    if 'username' not in session:
        return jsonify({'error': '未登录'}), 401
    
    try:
        author_id = get_user_id_by_username(session['username'])
        posts = get_posts_by_author(author_id)
        
        # 转换为字典列表并添加作者头像
        posts_list = []
        for post in posts:
            post_dict = dict(post)
            # 添加预览内容
            if post_dict.get('content'):
                content = post_dict['content']
                preview_content = content[:150] + '...' if len(content) > 150 else content
                post_dict['preview_html'] = render_markdown(preview_content)
            
            # 获取作者头像信息
            if post_dict.get('author'):
                author_info = get_user_by_username(post_dict['author'])
                if author_info:
                    avatar_url = dict(author_info).get('avatar_url')
                    post_dict['author_avatar'] = avatar_url
                else:
                    post_dict['author_avatar'] = None
            else:
                post_dict['author_avatar'] = None
            
            posts_list.append(post_dict)
        
        return jsonify(posts_list)
    except Exception as e:
        print(f"获取我的文章错误: {e}")
        return jsonify({'error': '获取我的文章失败'}), 500

# ============= 分类API =============

@app.route('/api/categories', methods=['GET'])
def api_categories():
    """获取分类API"""
    try:
        categories = get_all_categories()
        return jsonify([dict(category) for category in categories])
    except Exception as e:
        print(f"获取分类错误: {e}")
        return jsonify({'error': '获取分类失败'}), 500

@app.route('/api/categories/<int:category_id>/posts', methods=['GET'])
def api_category_posts(category_id):
    """获取指定分类的文章"""
    try:
        posts = get_all_posts(category_id)
        
        # 转换为字典列表并添加预览内容和作者头像
        posts_list = []
        for post in posts:
            post_dict = dict(post)
            # 添加Markdown渲染的预览
            if post_dict.get('content'):
                content = post_dict['content']
                preview_content = content[:200] + '...' if len(content) > 200 else content
                post_dict['preview_html'] = render_markdown(preview_content)
            
            # 获取作者头像信息
            if post_dict.get('author'):
                author_info = get_user_by_username(post_dict['author'])
                if author_info:
                    avatar_url = dict(author_info).get('avatar_url')
                    post_dict['author_avatar'] = avatar_url
                else:
                    post_dict['author_avatar'] = None
            else:
                post_dict['author_avatar'] = None
            
            posts_list.append(post_dict)
        
        return jsonify(posts_list)
    except Exception as e:
        print(f"获取分类文章错误: {e}")
        return jsonify({'error': '获取分类文章失败'}), 500

# ============= 搜索API =============

@app.route('/api/search', methods=['GET'])
def api_search_posts():
    """搜索文章API"""
    try:
        keyword = request.args.get('keyword', '').strip()
        if not keyword:
            return jsonify({'error': '搜索关键词不能为空'}), 400
        
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 10))
        category_id = request.args.get('category_id')
        author_id = request.args.get('author_id')
        
        # 转换参数类型
        category_id = int(category_id) if category_id else None
        author_id = int(author_id) if author_id else None
        
        # 执行搜索
        result = search_posts(keyword, page=page, per_page=per_page, 
                             category_id=category_id, author_id=author_id)
        
        # 转换文章为字典格式并添加预览内容和作者头像
        posts_list = []
        for post in result['posts']:
            post_dict = dict(post)
            # 添加Markdown渲染的预览
            if post_dict.get('content'):
                content = post_dict['content']
                preview_content = content[:200] + '...' if len(content) > 200 else content
                post_dict['preview_html'] = render_markdown(preview_content)
            
            # 高亮搜索关键词（在标题中）
            if keyword.lower() in post_dict['title'].lower():
                post_dict['title_highlighted'] = post_dict['title'].replace(
                    keyword, f'<mark>{keyword}</mark>'
                )
            else:
                post_dict['title_highlighted'] = post_dict['title']
            
            # 获取作者头像信息
            if post_dict.get('author'):
                author_info = get_user_by_username(post_dict['author'])
                if author_info:
                    avatar_url = dict(author_info).get('avatar_url')
                    post_dict['author_avatar'] = avatar_url
                else:
                    post_dict['author_avatar'] = None
            else:
                post_dict['author_avatar'] = None
            
            posts_list.append(post_dict)
        
        result['posts'] = posts_list
        return jsonify(result)
        
    except Exception as e:
        print(f"搜索文章错误: {e}")
        return jsonify({'error': '搜索失败'}), 500

@app.route('/api/search/suggestions', methods=['GET'])
def api_search_suggestions():
    """获取搜索建议API"""
    try:
        keyword = request.args.get('keyword', '').strip()
        if not keyword:
            return jsonify([])
        
        limit = int(request.args.get('limit', 5))
        suggestions = get_search_suggestions(keyword, limit)
        
        return jsonify([dict(suggestion) for suggestion in suggestions])
        
    except Exception as e:
        print(f"获取搜索建议错误: {e}")
        return jsonify({'error': '获取搜索建议失败'}), 500

@app.route('/api/search/autocomplete', methods=['GET'])
def api_search_autocomplete():
    """搜索自动补全API（基于标题）"""
    try:
        keyword = request.args.get('keyword', '').strip()
        if not keyword:
            return jsonify([])
        
        limit = int(request.args.get('limit', 10))
        posts = search_posts_by_title(keyword, limit)
        
        # 只返回标题和基本信息用于自动补全
        autocomplete_list = []
        for post in posts:
            autocomplete_list.append({
                'id': post['id'],
                'title': post['title'],
                'author': post['author'],
                'category': post['category_name']
            })
        
        return jsonify(autocomplete_list)
        
    except Exception as e:
        print(f"搜索自动补全错误: {e}")
        return jsonify({'error': '自动补全失败'}), 500

@app.route('/api/search/popular', methods=['GET'])
def api_popular_keywords():
    """获取热门搜索关键词API"""
    try:
        limit = int(request.args.get('limit', 10))
        keywords = get_popular_keywords(limit)
        
        return jsonify(keywords)
        
    except Exception as e:
        print(f"获取热门关键词错误: {e}")
        return jsonify({'error': '获取热门关键词失败'}), 500

@app.route('/api/search/advanced', methods=['POST'])
def api_advanced_search():
    """高级搜索API"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': '请求数据格式错误'}), 400
        
        keyword = data.get('keyword', '').strip()
        category_id = data.get('category_id')
        author_id = data.get('author_id')
        date_from = data.get('date_from')  # 格式: YYYY-MM-DD
        date_to = data.get('date_to')      # 格式: YYYY-MM-DD
        page = data.get('page', 1)
        per_page = data.get('per_page', 10)
        
        if not keyword:
            return jsonify({'error': '搜索关键词不能为空'}), 400
        
        # 执行基础搜索
        result = search_posts(keyword, page=page, per_page=per_page, 
                             category_id=category_id, author_id=author_id)
        
        # TODO: 如果需要日期筛选，可以在这里添加额外的过滤逻辑
        # 目前先返回基础搜索结果
        
        # 转换文章为字典格式并添加作者头像
        posts_list = []
        for post in result['posts']:
            post_dict = dict(post)
            # 添加Markdown渲染的预览
            if post_dict.get('content'):
                content = post_dict['content']
                preview_content = content[:200] + '...' if len(content) > 200 else content
                post_dict['preview_html'] = render_markdown(preview_content)
            
            # 获取作者头像信息
            if post_dict.get('author'):
                author_info = get_user_by_username(post_dict['author'])
                if author_info:
                    avatar_url = dict(author_info).get('avatar_url')
                    post_dict['author_avatar'] = avatar_url
                else:
                    post_dict['author_avatar'] = None
            else:
                post_dict['author_avatar'] = None
            
            posts_list.append(post_dict)
        
        result['posts'] = posts_list
        return jsonify(result)
        
    except Exception as e:
        print(f"高级搜索错误: {e}")
        return jsonify({'error': '高级搜索失败'}), 500

# ============= 管理员API =============

@app.route('/api/admin/posts', methods=['GET'])
def api_admin_posts():
    """管理员获取所有文章"""
    if 'username' not in session or not session.get('is_admin'):
        return jsonify({'error': '无权限'}), 403
    
    try:
        posts = get_all_posts()
        posts_list = []
        for post in posts:
            post_dict = dict(post)
            if post_dict.get('content'):
                content = post_dict['content']
                preview_content = content[:150] + '...' if len(content) > 150 else content
                post_dict['preview_html'] = render_markdown(preview_content)
            
            # 获取作者头像信息
            if post_dict.get('author'):
                author_info = get_user_by_username(post_dict['author'])
                if author_info:
                    avatar_url = dict(author_info).get('avatar_url')
                    post_dict['author_avatar'] = avatar_url
                else:
                    post_dict['author_avatar'] = None
            else:
                post_dict['author_avatar'] = None
            
            posts_list.append(post_dict)
        
        return jsonify(posts_list)
    except Exception as e:
        print(f"管理员获取文章错误: {e}")
        return jsonify({'error': '获取文章失败'}), 500

@app.route('/api/admin/users', methods=['GET'])
def api_admin_users():
    """管理员获取所有用户"""
    if 'username' not in session or not session.get('is_admin'):
        return jsonify({'error': '无权限'}), 403
    
    try:
        users = get_all_users()
        return jsonify([dict(user) for user in users])
    except Exception as e:
        print(f"获取用户错误: {e}")
        return jsonify({'error': '获取用户失败'}), 500

@app.route('/api/admin/users/<int:user_id>', methods=['DELETE'])
def api_delete_user(user_id):
    """管理员删除用户"""
    if 'username' not in session or not session.get('is_admin'):
        return jsonify({'error': '无权限'}), 403
    
    try:
        if delete_user(user_id):
            return jsonify({'success': True, 'message': '用户删除成功'})
        else:
            return jsonify({'error': '删除失败（可能是管理员账户）'}), 400
    except Exception as e:
        print(f"删除用户错误: {e}")
        return jsonify({'error': '删除用户失败'}), 500

@app.route('/api/admin/comments/recent', methods=['GET'])
def api_admin_recent_comments():
    """管理员获取最近评论"""
    if 'username' not in session or not session.get('is_admin'):
        return jsonify({'error': '无权限'}), 403
    
    try:
        limit = request.args.get('limit', 10)
        comments = get_recent_comments(int(limit))
        return jsonify([dict(comment) for comment in comments])
    except Exception as e:
        print(f"获取最近评论错误: {e}")
        return jsonify({'error': '获取最近评论失败'}), 500

@app.route('/api/admin/comments', methods=['GET'])
def api_admin_all_comments():
    """管理员获取所有评论"""
    if 'username' not in session or not session.get('is_admin'):
        return jsonify({'error': '无权限'}), 403
    
    try:
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 20))
        post_id = request.args.get('post_id')
        author_id = request.args.get('author_id')
        
        # 转换参数类型
        post_id = int(post_id) if post_id else None
        author_id = int(author_id) if author_id else None
        
        result = get_all_comments(page=page, per_page=per_page, 
                                post_id=post_id, author_id=author_id)
        
        # 转换评论为字典格式
        result['comments'] = [dict(comment) for comment in result['comments']]
        
        return jsonify(result)
    except Exception as e:
        print(f"获取所有评论错误: {e}")
        return jsonify({'error': '获取所有评论失败'}), 500

@app.route('/api/admin/comments/<int:comment_id>', methods=['DELETE'])
def api_admin_delete_comment(comment_id):
    """管理员删除任意评论（不受作者限制）"""
    if 'username' not in session or not session.get('is_admin'):
        return jsonify({'error': '无权限'}), 403
    
    try:
        # 管理员可以删除任意评论，无需检查作者权限
        comment = get_comment_by_id(comment_id)
        if not comment:
            return jsonify({'error': '评论不存在'}), 404
        
        success = delete_comment(comment_id)
        if success:
            return jsonify({'message': '评论删除成功'})
        else:
            return jsonify({'error': '删除评论失败'}), 500
    except Exception as e:
        print(f"管理员删除评论错误: {e}")
        return jsonify({'error': '删除评论失败'}), 500

# ============= 评论API =============

@app.route('/api/posts/<int:post_id>/comments', methods=['GET'])
def api_get_comments(post_id):
    """获取文章评论"""
    try:
        comments = get_comments_by_post(post_id)
        
        # 转换为字典列表并构建树形结构
        comments_list = []
        comment_dict = {}
        
        # 先创建所有评论的字典并添加作者头像
        for comment in comments:
            comment_data = dict(comment)
            comment_data['replies'] = []
            
            # 获取评论作者头像信息
            if comment_data.get('author'):
                author_info = get_user_by_username(comment_data['author'])
                if author_info:
                    avatar_url = dict(author_info).get('avatar_url')
                    comment_data['author_avatar'] = avatar_url
                else:
                    comment_data['author_avatar'] = None
            else:
                comment_data['author_avatar'] = None
            
            comment_dict[comment_data['id']] = comment_data
        
        # 构建树形结构
        for comment_data in comment_dict.values():
            if comment_data['parent_id']:
                # 这是回复评论
                parent = comment_dict.get(comment_data['parent_id'])
                if parent:
                    parent['replies'].append(comment_data)
            else:
                # 这是顶级评论
                comments_list.append(comment_data)
        
        return jsonify(comments_list)
    except Exception as e:
        print(f"获取评论错误: {e}")
        return jsonify({'error': '获取评论失败'}), 500

@app.route('/api/posts/<int:post_id>/comments', methods=['POST'])
def api_create_comment(post_id):
    """创建评论"""
    if 'username' not in session:
        return jsonify({'error': '未登录'}), 401
    
    try:
        # 检查文章是否存在
        post = get_post_by_id(post_id)
        if not post:
            return jsonify({'error': '文章不存在'}), 404
        
        data = request.get_json()
        if not data:
            return jsonify({'error': '请求数据格式错误'}), 400
        
        content = data.get('content', '').strip()
        parent_id = data.get('parent_id')
        
        if not content:
            return jsonify({'error': '评论内容不能为空'}), 400
        
        if len(content) > 1000:
            return jsonify({'error': '评论内容不能超过1000字符'}), 400
        
        # 如果是回复评论，检查父评论是否存在
        if parent_id:
            parent_comment = get_comment_by_id(parent_id)
            if not parent_comment or parent_comment['post_id'] != post_id:
                return jsonify({'error': '回复的评论不存在'}), 400
        
        author_id = get_user_id_by_username(session['username'])
        comment_id = create_comment(post_id, author_id, content, parent_id)
        
        if comment_id:
            # 返回新创建的评论并添加作者头像
            new_comment = get_comment_by_id(comment_id)
            comment_data = dict(new_comment)
            comment_data['replies'] = []
            
            # 获取评论作者头像信息
            if comment_data.get('author'):
                author_info = get_user_by_username(comment_data['author'])
                if author_info:
                    avatar_url = dict(author_info).get('avatar_url')
                    comment_data['author_avatar'] = avatar_url
                else:
                    comment_data['author_avatar'] = None
            else:
                comment_data['author_avatar'] = None
            
            return jsonify({
                'success': True, 
                'message': '评论发布成功',
                'comment': comment_data
            })
        else:
            return jsonify({'error': '评论发布失败'}), 500
            
    except Exception as e:
        print(f"创建评论错误: {e}")
        return jsonify({'error': '创建评论失败'}), 500

@app.route('/api/comments/<int:comment_id>', methods=['PUT'])
def api_update_comment(comment_id):
    """更新评论"""
    if 'username' not in session:
        return jsonify({'error': '未登录'}), 401
    
    try:
        comment = get_comment_by_id(comment_id)
        if not comment:
            return jsonify({'error': '评论不存在'}), 404
        
        # 检查权限（只有评论作者和管理员可以编辑）
        author_id = get_user_id_by_username(session['username'])
        if comment['author_id'] != author_id and not session.get('is_admin'):
            return jsonify({'error': '无权限编辑此评论'}), 403
        
        data = request.get_json()
        if not data:
            return jsonify({'error': '请求数据格式错误'}), 400
        
        content = data.get('content', '').strip()
        if not content:
            return jsonify({'error': '评论内容不能为空'}), 400
        
        if len(content) > 1000:
            return jsonify({'error': '评论内容不能超过1000字符'}), 400
        
        if update_comment(comment_id, content):
            return jsonify({'success': True, 'message': '评论更新成功'})
        else:
            return jsonify({'error': '更新失败'}), 500
            
    except Exception as e:
        print(f"更新评论错误: {e}")
        return jsonify({'error': '更新评论失败'}), 500

@app.route('/api/comments/<int:comment_id>', methods=['DELETE'])
def api_delete_comment(comment_id):
    """删除评论"""
    if 'username' not in session:
        return jsonify({'error': '未登录'}), 401
    
    try:
        comment = get_comment_by_id(comment_id)
        if not comment:
            return jsonify({'error': '评论不存在'}), 404
        
        # 检查权限（只有评论作者和管理员可以删除）
        author_id = get_user_id_by_username(session['username'])
        if comment['author_id'] != author_id and not session.get('is_admin'):
            return jsonify({'error': '无权限删除此评论'}), 403
        
        if delete_comment(comment_id):
            return jsonify({'success': True, 'message': '评论删除成功'})
        else:
            return jsonify({'error': '删除失败'}), 500
            
    except Exception as e:
        print(f"删除评论错误: {e}")
        return jsonify({'error': '删除评论失败'}), 500

# ============= 统计信息API =============

@app.route('/api/stats', methods=['GET'])
def api_stats():
    """获取网站统计信息"""
    try:
        # 获取统计数据
        stats = get_site_stats()
        
        return jsonify({
            'success': True,
            'data': stats
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取统计信息失败: {str(e)}'
        }), 500

# ============= 用户资料管理API =============

@app.route('/api/user/profile', methods=['GET'])
def api_get_user_profile():
    """获取当前用户的资料信息"""
    if 'username' not in session:
        return jsonify({'success': False, 'message': '请先登录'}), 401
    
    try:
        username = session['username']
        user = get_user_by_username(username)
        
        if not user:
            return jsonify({'success': False, 'message': '用户不存在'}), 404
        
        # 调试：打印头像URL信息
        avatar_url = dict(user).get('avatar_url')
        print(f"用户 {username} 的头像URL: {avatar_url}")
        
        return jsonify({
            'success': True,
            'data': {
                'id': user['id'],
                'username': user['username'],
                'email': dict(user).get('email'),
                'birthday': dict(user).get('birthday'),
                'bio': dict(user).get('bio'),
                'avatar_url': avatar_url,
                'created_at': user['created_at']
            }
        })
    except Exception as e:
        print(f"获取用户资料失败: {e}")
        return jsonify({
            'success': False,
            'message': f'获取用户资料失败: {str(e)}'
        }), 500

@app.route('/api/user/profile', methods=['PUT'])
def api_update_user_profile():
    """更新当前用户的资料信息"""
    if 'username' not in session:
        return jsonify({'success': False, 'message': '请先登录'}), 401
    
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'message': '请提供要更新的数据'}), 400
        
        user_id = get_user_id_by_username(session['username'])
        
        # 提取可更新的字段
        birthday = data.get('birthday')
        bio = data.get('bio')
        avatar_url = data.get('avatar_url')
        
        # 更新用户资料
        result = update_user_profile(user_id, birthday=birthday, bio=bio, avatar_url=avatar_url)
        
        if result:
            return jsonify({
                'success': True,
                'message': '用户资料更新成功'
            })
        else:
            return jsonify({
                'success': False,
                'message': '用户资料更新失败'
            }), 500
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'更新用户资料失败: {str(e)}'
        }), 500

@app.route('/api/user/birthday', methods=['PUT'])
def api_update_user_birthday():
    """更新用户生日"""
    if 'username' not in session:
        return jsonify({'success': False, 'message': '请先登录'}), 401
    
    try:
        data = request.get_json()
        if not data or 'birthday' not in data:
            return jsonify({'success': False, 'message': '请提供生日信息'}), 400
        
        user_id = get_user_id_by_username(session['username'])
        birthday = data['birthday']
        
        # 验证日期格式
        try:
            datetime.strptime(birthday, '%Y-%m-%d')
        except ValueError:
            return jsonify({'success': False, 'message': '日期格式错误，请使用YYYY-MM-DD格式'}), 400
        
        result = update_user_birthday(user_id, birthday)
        
        if result:
            return jsonify({
                'success': True,
                'message': '生日更新成功'
            })
        else:
            return jsonify({
                'success': False,
                'message': '生日更新失败'
            }), 500
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'更新生日失败: {str(e)}'
        }), 500

@app.route('/api/user/bio', methods=['PUT'])
def api_update_user_bio():
    """更新用户个性签名"""
    if 'username' not in session:
        return jsonify({'success': False, 'message': '请先登录'}), 401
    
    try:
        data = request.get_json()
        if not data or 'bio' not in data:
            return jsonify({'success': False, 'message': '请提供个性签名'}), 400
        
        user_id = get_user_id_by_username(session['username'])
        bio = data['bio']
        
        # 限制个性签名长度
        if len(bio) > 500:
            return jsonify({'success': False, 'message': '个性签名不能超过500个字符'}), 400
        
        result = update_user_bio(user_id, bio)
        
        if result:
            return jsonify({
                'success': True,
                'message': '个性签名更新成功'
            })
        else:
            return jsonify({
                'success': False,
                'message': '个性签名更新失败'
            }), 500
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'更新个性签名失败: {str(e)}'
        }), 500

@app.route('/api/user/avatar', methods=['POST'])
def api_upload_user_avatar():
    """上传用户头像"""
    if 'username' not in session:
        return jsonify({'success': False, 'message': '请先登录'}), 401
    
    try:
        print(f"头像上传请求 - 用户: {session['username']}")  # 调试日志
        
        # 调试：检查用户表结构
        check_user_table_structure()
        
        if 'file' not in request.files:
            print("错误: 没有文件被上传")
            return jsonify({'success': False, 'message': '没有文件被上传'}), 400
        
        file = request.files['file']
        print(f"收到文件: {file.filename}")  # 调试日志
        
        if file.filename == '':
            print("错误: 没有选择文件")
            return jsonify({'success': False, 'message': '没有选择文件'}), 400
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            # 为文件名添加时间戳避免重名
            timestamp = str(int(time.time()))
            name, ext = os.path.splitext(filename)
            filename = f"{name}_{timestamp}{ext}"
            
            print(f"保存文件名: {filename}")  # 调试日志
            
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            print(f"文件路径: {file_path}")  # 调试日志
            
            file.save(file_path)
            print("文件保存成功")  # 调试日志
            
            # 更新数据库中的头像URL
            user_id = get_user_id_by_username(session['username'])
            print(f"用户ID: {user_id}")  # 调试日志
            
            if user_id is None:
                print("错误: 无法获取用户ID")
                return jsonify({'success': False, 'message': '用户信息错误'}), 500
            
            avatar_url = f"/static/uploads/{filename}"
            print(f"头像URL: {avatar_url}")  # 调试日志
            
            result = update_user_avatar(user_id, avatar_url)
            print(f"数据库更新结果: {result}")  # 调试日志
            
            if result:
                # 返回完整URL给前端
                return jsonify({
                    'success': True,
                    'message': '头像上传成功',
                    'data': {
                        'avatar_url': avatar_url
                    }
                })
            else:
                return jsonify({
                    'success': False,
                    'message': '头像上传失败：数据库更新失败'
                }), 500
        else:
            print(f"错误: 不支持的文件格式 - {file.filename}")
            return jsonify({
                'success': False,
                'message': '不支持的文件格式，请上传jpg、jpeg、png或gif格式的图片'
            }), 400
    except Exception as e:
        print(f"头像上传错误: {e}")
        import traceback
        traceback.print_exc()  # 打印完整的错误堆栈
        return jsonify({
            'success': False,
            'message': f'上传头像失败: {str(e)}'
        }), 500

@app.route('/api/user/<username>/profile', methods=['GET'])
def api_get_user_profile_by_username(username):
    """根据用户名获取用户公开资料"""
    try:
        user = get_user_by_username(username)
        
        if not user:
            return jsonify({'success': False, 'message': '用户不存在'}), 404
        
        # 只返回公开信息
        avatar_url = dict(user).get('avatar_url')
            
        return jsonify({
            'success': True,
            'data': {
                'id': user['id'],
                'username': user['username'],
                'bio': dict(user).get('bio'),
                'avatar_url': avatar_url,
                'created_at': user['created_at']
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取用户资料失败: {str(e)}'
        }), 500

# ============= 健康检查API =============

@app.route('/api/health', methods=['GET'])
def api_health():
    """健康检查API"""
    return jsonify({
        'status': 'healthy',
        'message': 'Blog API is running',
        'timestamp': datetime.now().isoformat()
    })

# ============= 静态文件服务 =============

@app.route('/static/uploads/<filename>')
def uploaded_file(filename):
    """提供上传文件的静态服务"""
    try:
        print(f"请求静态文件: {filename}")  # 调试日志
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        # 检查文件是否存在
        if not os.path.exists(file_path):
            print(f"文件不存在: {file_path}")
            return jsonify({'error': '文件不存在'}), 404
        
        print(f"返回文件: {file_path}")
        
        # 设置正确的MIME类型
        from flask import send_file
        
        return send_file(file_path, 
                        as_attachment=False,
                        mimetype='image/webp' if filename.endswith('.webp') else None)
    except Exception as e:
        print(f"静态文件服务错误: {e}")
        return jsonify({'error': '文件服务错误'}), 500

# ============= 错误处理 =============

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'API端点不存在'}), 404

@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify({'error': '不支持的HTTP方法'}), 405

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': '服务器内部错误'}), 500

# ============= 主程序入口 =============

if __name__ == '__main__':
    print("初始化数据库...")
    init_db()  # 初始化数据库
    print("Flask API 服务器启动在 http://localhost:5000")
    print("API文档:")
    print("  认证: /api/auth/login, /api/auth/logout, /api/auth/register")
    print("  用户: /api/user/profile, /api/user/birthday, /api/user/bio, /api/user/avatar")
    print("  文章: /api/posts, /api/my-posts")
    print("  分类: /api/categories")
    print("  搜索: /api/search, /api/search/suggestions, /api/search/autocomplete")
    print("  管理: /api/admin/posts, /api/admin/users, /api/admin/comments")
    print("  统计: /api/stats")
    print("  健康: /api/health")
    app.run(debug=True, port=5000, host = '0.0.0.0')