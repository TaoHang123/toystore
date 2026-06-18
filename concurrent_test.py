import threading
import requests

# 需要先登录获取 session（或手动登录后复制 cookie）
# 这里以简单方式：先用浏览器登录，复制 sessionid 和 csrftoken 到代码中
# 或者用 requests 模拟登录。

url = "http://127.0.0.1:8000/shop/create-order/"
data = {
    # 你需要知道该 POST 请求需要哪些参数
    # 例如 address_id, csrfmiddlewaretoken 等
}

# 登录获取 cookie（如果下单需要登录）
session = requests.Session()
login_data = {
    'username': 'testuser',
    'password': 'testpass',
}
session.post('http://127.0.0.1:8000/login/', data=login_data)

def place_order():
    # 注意：每个请求需要带上 CSRF token，可以从第一次 GET 获取或从 cookie 自动处理
    # 这里简化，假设你的视图没有 CSRF 验证（或已设置 @csrf_exempt 测试）
    response = session.post(url, data=data)
    print(response.status_code)

# 创建 10 个线程同时下单
threads = []
for i in range(10):
    t = threading.Thread(target=place_order)
    t.start()
    threads.append(t)

for t in threads:
    t.join()