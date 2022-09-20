# Copyright (c) Acconeer AB, 2022
# All rights reserved

import acconeer.exptool as et
from acconeer.exptool import a121
from multiprocessing import Process, Queue
import argparse
from json import dumps, loads
import numpy as np
import time
import socket
import os

# from tqdm import tqdm

def put_nCube(clientSocket, data, ctname = 'radar_sensor'):

    # clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    HOST = '203.250.148.120'
    PORT = 20521
    NAME = (HOST,PORT)
    # # time.sleep(1)
    clientSocket.connect(NAME)
    triggerData = '{"ctname": '+"\""+ctname+"\""+',' '"con":' '"hello"}' + '<EOF>'

    clientSocket.send(triggerData.encode('utf-8'))
    while True:
        try:
            clientSocket.recv(100) #ack
            break
        except:
            pass
    print("cnt connect")


    value_dec = data
    # data = '{"ctname":'+"\"" + ctname +"\""+','+ '"con": '+'\"'+ str(value_dec) +'\"'+'}' + '<EOF>'
    data_dict = {
        'ctname' : ctname,
        'con' : np.array2string(value_dec)
    }
    data = dumps(data_dict)
    # data = '{"ctname": target' +'"con": '+'\"'+ str(value_dec) +'\"'+'}' + '<EOF>'
    # data = '{"ctname": "target", "con": '+'\"'+str(value_dec)+'\"'+'}' + '<EOF>'
    clientSocket.send(data.encode('utf-8'))
    # time.sleep(0.5)
    # clientSocket.recv(100)
    clientSocket.close()

# def streamer():
#     os.system('/home/pi/rpi_xe121/out/acc_exploration_server_a121')

def sender(q):    
    # HOST = '203.250.148.120'
    # PORT = 20521
    HOST = 'localhost'
    PORT = 3106
    NAME = (HOST,PORT)
    # time.sleep(1)
    clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # clientSocket.connect(NAME)
    while True:
        data = q.get()
        data = np.mean(data, axis = 0)
        send_data = np.concatenate((np.abs(data), np.angle(data)), axis = 0)
        put_nCube(clientSocket, send_data)

    # print('kafka time : ', time.time() - start)
    # clientSocket.close()

def saver(label, q):
    pass

def main(q):
    args = a121.ExampleArgumentParser().parse_args()
    et.utils.config_logging(args)

    # client = a121.Client(**a121.get_client_args(args))
    client = a121.Client(ip_address = '127.0.0.1')
    # client.ip_address = '127.0.0.1'
    client.connect()
    #start_distance = start_point * 2.5mm
    start_distance = 100
    start_point = start_distance / 2.5
    #end_distance = start_point * 2.5mm + num_points * 2.5mm
    end_distance = 150
    num_points = (end_distance - start_point * 2.5) / 2.5

    sensor_config = a121.SensorConfig(
        subsweeps=[
            a121.SubsweepConfig(
                start_point = start_point,
                step_length = 1,
                num_points = num_points,
                profile = a121.Profile.PROFILE_1,
                hwaas = 10,
            ),
        ],
        sweeps_per_frame = 20,
        frame_rate = 1,
    )
    # session_config = a121.SessionConfig(
    #     [
    #         {
    #             2: sensor_config,
    #         },
    #     ],
    # )

    client.setup_session(sensor_config)
    # client.setup_session(session_config)
    client.start_session()
    
    # start = time.time()
    # for i in tqdm(range(data_len)):
    try:
        while True:
            data = client.get_next()
            q.put(data.frame)
    except KeyboardInterrupt:
        pass
    finally :
    # print('time : ', time.time() - start)
        client.stop_session()
        client.disconnect()

if __name__ == '__main__':

    data_len = 10

    # parent_conn, child_conn = Pipe()
    queue = Queue()

    p_receiver = Process(target = main, args = (queue,))
    p_receiver.start()
    # p_sender = Process(target = sender, args = (label, producer, parent_conn))
    p_sender = Process(target = sender, args = (queue,))
    p_sender.start()
    # p_streamer.join()
    p_receiver.join()
    p_sender.join()
    queue.close()
