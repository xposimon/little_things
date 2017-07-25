#!/usr/bin/python
# coding = utf-8
# reverse_proxy

import socket, re, time, requests
from threading import Thread

def r_and_s(fromClientSock, MAXBUF = 4096):
# Dealing with received raw data
    try:
        data = fromClientSock.recv(MAXBUF)

    except:
        fromClientSock.close()
    if not data:
        return

    print(data[:60])

    request_pattern = "(GET)|(POST) /(.*) HTTP/1.[01]"
    host_pattern = ".*Host: ([0-9a-zA-Z\\.]*)(:\d+)?.*"
    req_re = re.compile(request_pattern)
    result = req_re.match(data.decode("utf-8"))

    if result:
        host_result = re.search(re.compile(host_pattern), data.decode("utf-8"))

        # 确认访问的域名存在
        if host_result:
            host = host_result.group(1) # get host
        else :
            host = "127.0.0.1"

        # 端口不为80
        #print(host_result.groups())

        if host_result and len(host_result.groups()) == 3:
            to_port = int(host_result.group(2)[1:])
        else:
            to_port = 80

        with open("parse_domain.inc", "r") as f:
            domain_names = eval(f.read())
            #print(f.read())
        #print(domain_names)
        if host not in domain_names.keys():
            ip = "127.0.0.1"
        else :
            ip = domain_names[host]

        # 记录通过的http包
        filename = time.strftime("%Y%m%d", time.localtime(time.time()))
        with open("./secret_log/" + filename + ".log", "a") as f:
            f.write(data.decode("utf-8"))
            f.write("\n\n")

        print(ip, to_port)
        toSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        toSock.connect((ip, to_port))
        data = (data.decode().replace(host, ip)).encode()
        print(data[:60])
        toSock.sendall(data)


        back_data = toSock.recv(MAXBUF)
        response = b""
        while len(back_data):
            print(back_data[:60])
            response += back_data
            back_data = toSock.recv(MAXBUF)

        fromClientSock.sendall(response)
        toSock.close()
    #fromClientSock.send("<html>it's on testing</html>".encode("utf-8"))
    fromClientSock.close()
    print("finish\n\n")

class server:
    ''' The server to listen http requests. '''
    def __init__(self, host = '', port = 80, maxbuf = 4096):
        self.port = port
        self.MAXBUF = maxbuf
        self.host = host

    def run(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind(('', self.port))
        sock.listen(5)
        stop_flag = False

        while not stop_flag:
            print("Waiting for new connection:\n")
            tcpClientSock, addr = sock.accept()
            print("Receive from: " + str(addr))
            th = Thread(args=(tcpClientSock, ), target = r_and_s)
            th.start()
            th.join()

        sock.close()


if __name__ == "__main__":
    MyServer = server('0.0.0.0', 80)
    MyServer.run()