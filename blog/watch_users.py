from database import get_all_users

def view_database():
    users = get_all_users()
    print("=== 数据库中的所有用户 ===")
    for user in users:
        print(f"ID: {user['id']}, 用户名: {user['username']}, 密码: {user['password']}")
    print(f"总计 {len(users)} 个用户")

if __name__ == '__main__':
    view_database()