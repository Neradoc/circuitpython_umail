# SPDX-FileCopyrightText: Copyright 2018 Shawwwn <shawwwn1@gmail.com>
# SPDX-FileCopyrightText: Copyright 2025 Neradoc, https://neradoc.me
# SPDX-License-Identifier: MIT
"""
Lightweight SMTP client for Circuitpython
Ported from uMail (MicroMail) for MicroPython https://github.com/shawwwn/uMail
"""

from binascii import b2a_base64 as b64

DEFAULT_TIMEOUT = 10 # sec
LOCAL_DOMAIN = '127.0.0.1'
CMD_EHLO = 'EHLO'
CMD_STARTTLS = 'STARTTLS'
CMD_AUTH = 'AUTH'
CMD_MAIL = 'MAIL'
AUTH_PLAIN = 'PLAIN'
AUTH_LOGIN = 'LOGIN'


class SMTP:
    def __init__(self, pool, host, port, ssl=None, username=None, password=None):
        self.username = username
        self.buffer = bytearray(3)
        addr = pool.getaddrinfo(host, port)[0][-1]
        sock = pool.socket(pool.AF_INET, pool.SOCK_STREAM)
        sock.settimeout(DEFAULT_TIMEOUT)
        sock.connect(addr)
        if ssl:
            context = ssl.create_default_context()
            sock = context.wrap_socket(sock)
        sock.recv_into(self.buffer, 3)
        code = int(self.buffer[:3])
        assert code==220, 'cant connect to server %d, %s' % (code, resp)
        self._sock = sock
        self.readline()

        code, resp = self.cmd(CMD_EHLO + ' ' + LOCAL_DOMAIN)
        assert code==250, '%d' % code
        if not ssl and CMD_STARTTLS in resp:
            code, resp = self.cmd(CMD_STARTTLS)
            assert code==220, 'start tls failed %d, %s' % (code, resp)
            self._sock = ssl_wrap_socket(sock)

        if username and password:
            self.login(username, password)

    def cmd(self, cmd_str):
        self.write(cmd_str + '\r\n')
        resp = []
        next = True
        while next:
            code = self.read(3)
            next = self.read(1) == b'-'
            resp.append(self.readline().strip().decode())
        return int(code), resp

    def login(self, username, password):
        self.username = username
        code, resp = self.cmd(CMD_EHLO + ' ' + LOCAL_DOMAIN)
        assert code==250, '%d, %s' % (code, resp)

        auths = None
        for feature in resp:
            if feature[:4].upper() == CMD_AUTH:
                auths = feature[4:].strip('=').upper().split()
        assert auths!=None, "no auth method"

        if AUTH_PLAIN in auths:
            cren = b64(b"\0%s\0%s" % (username, password))[:-1].decode()
            code, resp = self.cmd('%s %s %s' % (CMD_AUTH, AUTH_PLAIN, cren))
        elif AUTH_LOGIN in auths:
            code, resp = self.cmd("%s %s %s" % (CMD_AUTH, AUTH_LOGIN, b64(username)[:-1].decode()))
            assert code==334, 'wrong username %d, %s' % (code, resp)
            code, resp = self.cmd(b64(password)[:-1].decode())
        else:
            raise Exception("auth(%s) not supported " % ', '.join(auths))

        assert code==235 or code==503, 'auth error %d, %s' % (code, resp)
        return code, resp

    def to(self, addrs, mail_from=None):
        mail_from = self.username if mail_from==None else mail_from
        code, resp = self.cmd('MAIL FROM: <%s>' % mail_from)
        assert code==250, 'sender refused %d, %s' % (code, resp)

        if isinstance(addrs, str):
            addrs = [addrs]
        count = 0
        for addr in addrs:
            code, resp = self.cmd('RCPT TO: <%s>' % addr)
            if code!=250 and code!=251:
                print('%s refused, %s' % (addr, resp))
                count += 1
        assert count!=len(addrs), 'recipient refused, %d, %s' % (code, resp)

        code, resp = self.cmd('DATA')
        assert code==354, 'data refused, %d, %s' % (code, resp)
        return code, resp

    def write(self, content):
        data = bytes(content, "utf8")
        self._sock.send(data)

    def read(self, n):
        self._sock.recv_into(self.buffer, n)
        return bytes(self.buffer[:n])

    def send(self, content=''):
        if content:
            self.write(content)
        self.write('\r\n.\r\n') # the five letter sequence marked for ending
        line = self.readline()
        return (int(line[:3]), line[4:].strip().decode())

    def quit(self):
        self.cmd("QUIT")
        self._sock.close()

    def readline(self):
        """
        Implement readline() for native wifi using recv_into
        """
        data_string = b""
        while True:
            num = self._sock.recv_into(self.buffer, 1)
            data_string += self.buffer[:num]
            if num == 0:
                return data_string
            if data_string[-2:] == b"\r\n":
                return data_string[:-2]
