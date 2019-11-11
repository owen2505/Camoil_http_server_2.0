# coding = utf-8
"""
HTTP Server v2.0
* 多线程并发
* 基本的request解析
* 能够反馈基本数据
* 使用类封装
"""
from socket import *
from threading import Thread
import sys


# 封装具体的类作为HTTP Sever功能模块
class HttpServer(object):
    def __init__(self, server_addr, static_dir):
        # 添加对象属性
        self.static_dir = static_dir
        self.server_addr = server_addr
        self.create_socket()  # 初始化时自动创建套接字
        self.bind()  # 初始化时自动绑定地址

    # 创建套接字并设置端口可重用
    def create_socket(self):
        self.sockfd = socket()
        self.sockfd.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)

    # 绑定地址
    def bind(self):
        self.sockfd.bind(self.server_addr)
        self.ip = self.server_addr[0]
        self.port = self.server_addr[1]

    # 具体处理http请求
    def handle(self, connfd):
        request = connfd.recv(4096)
        # 防止浏览器异常断开
        if not request:
            connfd.close()
            return
        request_headers = request.splitlines()
        print(connfd.getpeername(), ":", request_headers[0])
        # 获取请求内容
        get_request = str(request_headers[0]).split(" ")[1]
        if get_request == "/" or get_request[-5:] == ".html":
            print("想获取网页")
            self.get_html(connfd, get_request)
        else:
            print("想获取其他内容")
            self.get_data(connfd, get_request)
        connfd.close()

    # 监听、连接、创建多线程并启动线程
    def serve_forever(self):  # 负责启动服务
        self.sockfd.listen(5)
        print("监听端口：", self.port)
        while True:
            try:
                connfd, addr = self.sockfd.accept()
            except KeyboardInterrupt:
                self.sockfd.close()
                sys.exit("服务器退出")
            except Exception as e:
                print("Error:", e)
                continue
            # 创建多线程处理请求
            client_thread = Thread(target=self.handle, args=(connfd,))
            client_thread.setDaemon(True)  # 设置主线程与分支线程退出关系
            client_thread.start()

    # 获取网页响应
    def get_html(self, connfd, get_request):
        if get_request == "/":
            filename = self.static_dir + "/index.html"  # 请求主页
        else:
            filename = self.static_dir + get_request
        try:
            f = open(filename)
        except IOError:
            # 没有找到网页
            response_headers = "HTTP/1.1 404 Not Found\r\n"
            response_headers += "\r\n"
            response_body = "很抱歉，页面不存在！"
        else:
            # 返回网页内容
            response_headers = "HTTP/1.1 200 OK\r\n"
            response_headers += "\r\n"
            response_body = f.read()
        finally:
            response = response_headers + response_body
            connfd.send(response.encode())
            f.close()

    # 处理非网页请求
    def get_data(self, connfd, get_request):
        response_headers = "HTTP/1.1 200 OK\r\n"
        response_headers += "\r\n"
        response_body = "<p>waiting for httpserver v3.0</p>"
        response = response_headers + response_body
        connfd.send(response.encode())


if __name__ == '__main__':
    # 使用者自己设定address
    server_addr = ("0.0.0.0", 8000)
    # 用户提供存放网页的目录
    static_dir = "./static"
    # 创建服务器对象
    httpd = HttpServer(server_addr, static_dir)
    # 启动服务
    httpd.serve_forever()
    print(httpd.ip)
    print(httpd.port)
