# Circuitpython umail

Lightweight SMTP client for Circuitpython [ported from umail for micropython](https://github.com/shawwwn/uMail).

Pass the socketpool and if needed the ssl module instance. This example is for builtin wifi, but those should work when substituting airlift or ethernet.

```py
import wifi
import socketpool
import ssl
import umail

pool = socketpool.SocketPool(wifi.radio)
smtp = umail.SMTP(pool, 'smtp.gmail.com', 465, ssl=ssl)
```

## Use port 465 for gmail

Gmail SSL access can be done using two different ports, 465 or 587, which support different versions of the TLS protocol. Circuitpython encounters an SSL error when using port 587. This needs to be investigated to find a fix either in the core or this library. Try using port 465 instead.

> Is port 465 or 587 better for Gmail?
> While both ports offer their advantages, choosing the proper mail server configuration that best suits your needs is essential. In general, most email clients and SMTP servers now support and prefer Port 587 due to its flexible approach to TLS encryption and compatibility with modern security standards.

