# Circuitpython umail

Lightweight SMTP client for Circuitpython ported from umail for micropython.

Pass the socketpool and if needed the ssl module instance. This example is for builtin wifi, but those should work when substituting airlift or ethernet.

```py
import wifi
import socketpool
import ssl
import umail

pool = socketpool.SocketPool(wifi.radio)
smtp = umail.SMTP(pool, 'smtp.gmail.com', 465, ssl=ssl)
```
