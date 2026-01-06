'''
fiddler代理配置
'''
import ssl
import certifi
# 1. 找到 Python 的证书存储路径
print("默认证书路径:", certifi.where())  # 例如: C:\Python39\lib\site-packages\certifi\cacert.pem




# 1. 获取 Fiddler 证书内容
fiddler_cert_path = r"d:\Fiddler_Root_Certificate.pem"  # 替换为你的实际路径
with open(fiddler_cert_path, 'r') as f:
    fiddler_cert = f.read().strip()  # 去除首尾空白字符

# 2. 读取现有证书内容
cacert_path = certifi.where()
with open(cacert_path, 'r') as f:
    existing_certs = f.read()

# 3. 如果 Fiddler 证书不存在，则追加
if fiddler_cert not in existing_certs:
    with open(cacert_path, 'a') as f:  # 追加模式
        f.write('\n' + fiddler_cert + '\n')
    print("✅ Fiddler 证书已添加到:", cacert_path)
else:
    print("⏩ Fiddler 证书已存在，无需重复添加")

# 4. 验证
print("SSL 默认验证路径:", ssl.get_default_verify_paths())
import os
os.environ["REQUESTS_CA_BUNDLE"] = certifi.where()  # 强制使用更新后的证书
os.environ["SSL_CERT_FILE"] = certifi.where()

# 设置代理（根据你的代理服务器地址修改）
os.environ["HTTP_PROXY"] = "http://127.0.0.1:8866"  # 例如："http://127.0.0.1:7890"
os.environ["HTTPS_PROXY"] = "http://127.0.0.1:8866"  # HTTPS通常也用HTTP代理地址
os.environ["ALL_PROXY"] = "http://127.0.0.1:8866"
os.environ["REQUESTS_CA_BUNDLE"] = ""  # 禁用证书验证
