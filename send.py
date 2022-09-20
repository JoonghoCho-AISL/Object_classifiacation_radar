import socket
import time

def put_mobius(ctname,data):

    HOST= '203.250.148.120'
    PORT =  20520
    NAME = (HOST,PORT)

    clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    clientSocket.connect(NAME)

    triggerData = '{"ctname": '+"\""+str(ctname)+"\""+',' '"con":' '"hello"}' + '<EOF>'

    clientSocket.send(triggerData.encode('utf-8'))
    clientSocket.recv(100) #ack
    print("cnt connect")


    value_dec = data
    data = '{"ctname":'+"\""+str(ctname)+"\""+','+ '"con": '+'\"'+value_dec+'\"'+'}' + '<EOF>'
    clientSocket.send(data.encode('utf-8'))
    time.sleep(0.5)
    clientSocket.close()