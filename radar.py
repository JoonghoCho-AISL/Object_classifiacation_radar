# Copyright (c) Acconeer AB, 2022
# All rights reserved

import acconeer.exptool as et
from acconeer.exptool import a121
from json import dumps, loads
import numpy as np
import time
import socket
import os
import argparse
from tqdm import tqdm

# from tqdm import tqdm
import socket
import time

DATALENGTH = 30



# def put_mobius(data, clientSocket, ctname = 'radar'):
def put_mobius(data, ctname = 'target'):
    HOST = '127.0.0.1'
    PORT = 3105
    NAME = (HOST,int(PORT))
    clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    clientSocket.connect(NAME)

    triggerData = '{"ctname": '+"\""+str(ctname)+"\""+',' '"con":' '"hello"}' + '<EOF>'

    clientSocket.send(triggerData.encode('utf-8'))
    clientSocket.recv(100) #ack
    print("cnt connect")


    value_dec = data
    # send_data = {
    #     'ctname' : ctname,
    #     # 'con' : str(value_dec)
    #     # 'con' : value_dec.tobytes()
    #     'con' : value_dec.tolist()
    # }
    # send_data = dumps(send_data)
    send_data = '{"ctname":'+"\""+ctname+"\""+','+ '"con": '+'\"'+ str(value_dec.tolist()) +'\"'+'}' + '<EOF>'
    clientSocket.send(send_data.encode('utf-8'))
    # time.sleep(0.5)
    clientSocket.close()
    # time.sleep(0.5)

def preprocess(data):
    mean_data = np.mean(data,axis = 0)
    re_data = np.concatenate((np.abs(mean_data), np.angle(mean_data)), axis = 0)
    re_data = np.reshape(re_data, (1, re_data.shape[0]))
    return re_data

# def sender(data, clientSocket): 
def sender(data):
    # data = np.mean(data, axis = 0)
    # send_data = np.concatenate((np.abs(data), np.angle(data)), axis = 0)
    # send_data = np.reshape(send_data, (1, send_data.shape[0]))
    send_data = preprocess(data)
    # print(send_data.shape)
    # put_mobius(send_data, clientSocket)
    put_mobius(send_data)

def saver(label, q):
    pass

def main(save, send, name = None):
    # args = a121.ExampleArgumentParser().parse_args()
    # et.utils.config_logging(args)

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


    client.setup_session(sensor_config)
    # client.setup_session(session_config)
    client.start_session()
    try:
        if send == True:
            while True:
                data = client.get_next()
                data = data.frame
                sender(data)
        elif save == True:
            save_data = list()
            for j in tqdm(range(DATALENGTH)):
                data = client.get_next()
                data = data.frame
                save_data.append(preprocess(data))
            numpy_data = np.array(save_data)
            # print(numpy_data.shape)
            numpy_data = np.reshape(numpy_data, (numpy_data.shape[0], numpy_data.shape[2]))
            np.savetxt('./data/%s.csv'%(name), numpy_data, delimiter = ',')

    except KeyboardInterrupt:
        pass
    finally :
        client.stop_session()
        client.disconnect()
        
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description = 'Select save or send')
    parser.add_argument('-s','--save', action = 'store_true')
    parser.add_argument('-n','--name', action = 'store')
    parser.add_argument('-t', '--send', action = 'store_true')
    args = parser.parse_args()
    
    save = args.save
    name = args.name
    send = args.send

    main(save, send, name)

