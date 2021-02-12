#!/usr/bin/env python

from __future__ import print_function

import thread
import socket

import argparse

import sys, time, os, glob, shutil, math, datetime

from tmuxsend import TmuxSend


def run_server(port):

    # Create a TCP/IP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    #sock.settimeout(3)
    # Bind the socket to the port
    server_address = ('', port)
    sock.bind(server_address)
    sock.listen(1)
    print("ROS navigation server started on port %d ..." %port)

    tmux = TmuxSend('bringup', ['loc','nav','laser'])

    connected = False
    dorun = True
    while dorun:

        if not connected:
            print("-- Waiting for connection ...")
        while (dorun and not connected):
            try:
                # Wait for a connection
                connection, client_address = sock.accept()
                connected = True
                print ('-- Connection from %s'  %client_address[0])
            except KeyboardInterrupt:
                print("User interrupt (quit)")
                dorun = False
            except Exception as e:
                print(e)
                pass # keep listening
    
        if not dorun:
            return

        # print("-- Waiting for data...")
        data = None
        while dorun and connected and data is None:
            # receive data
            try:
                #connection.settimeout(3) # timeout when listening (exit with CTRL+C)
                data = connection.recv(320)  # blocking
                data = data.strip()
            except KeyboardInterrupt:
                print("User interrupt (quit)")
                dorun = False
            except socket.timeout:
                data = None
                print("socket timeout")

        if data is not None:
            if len(data)==0:
                connected = False
            else:
                print(data)
                navfolder = "~/src/marrtino_apps/navigation"
                laserfolder = "~/src/marrtino_apps/laser"
                if data=='@loc':
                    tmux.cmd(0,'cd %s' %navfolder)
                    tmux.cmd(0,'python startloc.py')
                elif data=='@lockill':
                    tmux.Cc(0)
                elif data=='@movebase':
                    tmux.cmd(1,'cd %s' %navfolder)
                    tmux.cmd(1,'roslaunch move_base.launch')
                elif data=='@movebasekill':
                    tmux.Cc(1)
                elif data=='@hokuyo':
                    tmux.cmd(2,'cd %s' %laserfolder)
                    tmux.cmd(2,'roslaunch hokuyo.launch')
                elif data=='@hokuyokill':
                    tmux.Cc(2)
                elif data=='@rplidar':
                    tmux.cmd(2,'cd %s' %laserfolder)
                    tmux.cmd(2,'roslaunch rplidar.launch')
                elif data=='@rplidarkill':
                    tmux.Cc(2)
                else:
                    print('Unknown command %s')


if __name__ == '__main__':

    default_port = 9240

    parser = argparse.ArgumentParser(description='navigation bringup')
    parser.add_argument('server_port', type=int, default=default_port, help='server port')

    args = parser.parse_args()

    run_server(args.server_port)

