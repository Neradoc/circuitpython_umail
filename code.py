import wifi
import socketpool
import ssl
import umail

pool = socketpool.SocketPool(wifi.radio)

smtp = umail.SMTP(pool, 'smtp.gmail.com', 465, ssl=ssl) # Gmail's SSL port
smtp.login('bob@gmail.com', 'bobspassword')
smtp.to('alice@gmail.com')
smtp.write("From: Bob <bob@gmail.com>\n")
smtp.write("To: Alice <alice@gmail.com>\n")
smtp.write("Subject: Poem\n\n")
smtp.write("Roses are red.\n")
smtp.write("Violets are blue.\n")
smtp.write("...\n")
smtp.send()
smtp.quit()
