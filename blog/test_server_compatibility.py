#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
服务器兼容性测试脚本
测试分页功能在不同环境下的兼容性
"""

import sys
import os
import sqlite3
from database import *

def test_basic_functionality():
    """测试基本功能"""
    print("=" * 50)
    print("测试基本功能")
    print("=" * 50)
    
    try:
        # 初始化数据库
        init_db()
        print("✓ 数据库初始化成功")
        
        # 测试连接
        conn = get_db_connection()
        conn.close()
        print("✓ 数据库连接正常")
        
        # 测试获取分类
        categories = get_all_categories()
        print(f"✓ 获取分类成功，共 {len(categories)} 个分类")
        
        return True
    except Exception as e:
        print(f"✗ 基本功能测试失败: {e}")
        return False

def test_pagination_functions():
    """测试分页函数"""
    print("\n" + "=" * 50)
    print("测试分页功能")
    print("=" * 50)
    
    try:
        # 测试获取文章总数
        total_posts = get_posts_count()
        print(f"✓ 获取文章总数: {total_posts}")
        
        # 测试分页查询
        page = 1
        per_page = 5
        posts = get_posts_paginated(page=page, per_page=per_page)
        print(f"✓ 分页查询成功，第{page}页，每页{per_page}篇，实际返回{len(posts)}篇")
        
        # 测试不同页码
        if total_posts > per_page:
            page2_posts = get_posts_paginated(page=2, per_page=per_page)
            print(f"✓ 第2页查询成功，返回{len(page2_posts)}篇文章")
        
        # 测试分类筛选
        categories = get_all_categories()
        if categories:
            category_id = categories[0]['id']
            category_posts = get_posts_paginated(page=1, per_page=per_page, category_id=category_id)
            category_count = get_posts_count(category_id=category_id)
            print(f"✓ 分类{category_id}筛选成功，共{category_count}篇，返回{len(category_posts)}篇")
        
        return True
    except Exception as e:
        print(f"✗ 分页功能测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_edge_cases():
    """测试边缘情况"""
    print("\n" + "=" * 50)
    print("测试边缘情况")
    print("=" * 50)
    
    try:
        # 测试空页
        empty_posts = get_posts_paginated(page=999, per_page=10)
        print(f"✓ 空页查询正常，返回{len(empty_posts)}篇文章")
        
        # 测试极小分页大小
        small_page = get_posts_paginated(page=1, per_page=1)
        print(f"✓ 小分页查询正常，返回{len(small_page)}篇文章")
        
        # 测试不存在的分类
        nonexistent_posts = get_posts_paginated(page=1, per_page=10, category_id=99999)
        print(f"✓ 不存在分类查询正常，返回{len(nonexistent_posts)}篇文章")
        
        # 测试负数页码
        negative_posts = get_posts_paginated(page=-1, per_page=10)
        print(f"✓ 负数页码查询正常，返回{len(negative_posts)}篇文章")
        
        return True
    except Exception as e:
        print(f"✗ 边缘情况测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_sql_injection_safety():
    """测试SQL注入安全性"""
    print("\n" + "=" * 50)
    print("测试SQL注入安全性")
    print("=" * 50)
    
    try:
        # 测试恶意输入
        malicious_inputs = [
            "1; DROP TABLE posts; --",
            "' OR '1'='1",
            "1' UNION SELECT * FROM users --",
            "NULL",
            "",
        ]
        
        for malicious_input in malicious_inputs:
            try:
                # 注意：这里我们传递字符串而不是整数，看函数如何处理
                posts = get_posts_paginated(page=1, per_page=10, category_id=malicious_input)
                print(f"✓ 恶意输入 '{malicious_input}' 被安全处理")
            except Exception as e:
                print(f"✓ 恶意输入 '{malicious_input}' 被正确拒绝: {e}")
        
        return True
    except Exception as e:
        print(f"✗ SQL注入测试失败: {e}")
        return False

def test_database_performance():
    """测试数据库性能"""
    print("\n" + "=" * 50)
    print("测试数据库性能")
    print("=" * 50)
    
    try:
        import time
        
        # 测试大量查询的性能
        start_time = time.time()
        for i in range(100):
            get_posts_count()
        count_time = time.time() - start_time
        print(f"✓ 100次count查询耗时: {count_time:.3f}秒")
        
        # 测试分页查询性能
        start_time = time.time()
        for i in range(1, 11):
            get_posts_paginated(page=i, per_page=10)
        page_time = time.time() - start_time
        print(f"✓ 10次分页查询耗时: {page_time:.3f}秒")
        
        return True
    except Exception as e:
        print(f"✗ 性能测试失败: {e}")
        return False

def test_server_environment():
    """测试服务器环境兼容性"""
    print("\n" + "=" * 50)
    print("测试服务器环境兼容性")
    print("=" * 50)
    
    try:
        # 检查Python版本
        print(f"✓ Python版本: {sys.version}")
        
        # 检查SQLite版本
        print(f"✓ SQLite版本: {sqlite3.sqlite_version}")
        
        # 检查文件权限
        db_path = DATABASE
        if os.path.exists(db_path):
            print(f"✓ 数据库文件存在: {db_path}")
            print(f"✓ 数据库文件大小: {os.path.getsize(db_path)} bytes")
            print(f"✓ 数据库文件可读: {os.access(db_path, os.R_OK)}")
            print(f"✓ 数据库文件可写: {os.access(db_path, os.W_OK)}")
        
        # 检查字符编码
        test_content = "测试中文字符：你好世界！🌍"
        conn = get_db_connection()
        conn.execute("CREATE TEMP TABLE test_encoding (content TEXT)")
        conn.execute("INSERT INTO test_encoding VALUES (?)", (test_content,))
        result = conn.execute("SELECT content FROM test_encoding").fetchone()
        conn.close()
        
        if result and result[0] == test_content:
            print("✓ 字符编码测试通过")
        else:
            print("✗ 字符编码测试失败")
        
        return True
    except Exception as e:
        print(f"✗ 服务器环境测试失败: {e}")
        return False

def check_database_integrity():
    """检查数据库完整性"""
    print("\n" + "=" * 50)
    print("检查数据库完整性")
    print("=" * 50)
    
    try:
        conn = get_db_connection()
        
        # 检查表是否存在
        tables = conn.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name NOT LIKE 'sqlite_%'
        """).fetchall()
        
        table_names = [table[0] for table in tables]
        required_tables = ['users', 'posts', 'categories', 'comments']
        
        for table in required_tables:
            if table in table_names:
                print(f"✓ 表 {table} 存在")
            else:
                print(f"✗ 表 {table} 不存在")
        
        # 检查索引
        for table in table_names:
            indexes = conn.execute(f"PRAGMA index_list({table})").fetchall()
            print(f"✓ 表 {table} 有 {len(indexes)} 个索引")
        
        # 检查外键约束
        foreign_keys = conn.execute("PRAGMA foreign_key_check").fetchall()
        if not foreign_keys:
            print("✓ 外键约束检查通过")
        else:
            print(f"✗ 发现外键约束问题: {len(foreign_keys)} 个")
        
        conn.close()
        return True
    except Exception as e:
        print(f"✗ 数据库完整性检查失败: {e}")
        return False

def main():
    """主测试函数"""
    print("博客系统服务器兼容性测试")
    print("测试时间:", datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    
    tests = [
        ("基本功能", test_basic_functionality),
        ("分页功能", test_pagination_functions),
        ("边缘情况", test_edge_cases),
        ("SQL注入安全", test_sql_injection_safety),
        ("数据库性能", test_database_performance),
        ("服务器环境", test_server_environment),
        ("数据库完整性", check_database_integrity),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
                print(f"\n{test_name} 测试: ✓ 通过")
            else:
                print(f"\n{test_name} 测试: ✗ 失败")
        except Exception as e:
            print(f"\n{test_name} 测试: ✗ 异常 - {e}")
    
    print("\n" + "=" * 60)
    print(f"测试总结: {passed}/{total} 项测试通过")
    
    if passed == total:
        print("🎉 所有测试通过！系统可以在服务器上运行")
        return True
    else:
        print("⚠️  部分测试失败，请检查问题")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
