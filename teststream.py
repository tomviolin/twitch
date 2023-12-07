#!/home/tomh/venv/video/bin/python
import os,sys
import threading, signal, os, sys, time, logging
import numpy as np
import cv2
import subprocess as sp
import urllib.request
import time
import json
config=json.load(open("config.json","r"))
FPS = config["FPS"]
CBR = config["CBR"]

os.chdir(os.path.dirname(sys.argv[0]))

req = urllib.request.urlopen('http://waterbase.uwm.edu/webcam/currentlink.jpg')
arr = np.asarray(bytearray(req.read()), dtype=np.uint8)
frame = cv2.imdecode(arr, cv2.IMREAD_COLOR) # 'Load it as it is'
frame = cv2.resize(frame, (1920,1080))

frame_width=frame.shape[1]
frame_height=frame.shape[0]

print(f"frame width:  {frame_width}")
print(f"frame height: {frame_height}")
print(f"FPS: {FPS}\n")

while True:
    config=json.load(open("config.json","r"))
    FPS = config["FPS"]
    CBR = config["CBR"]
    command = [
        'ffmpeg',
        #'-loglevel','quiet',
        '-stream_loop', '-1',
        '-f', 'rawvideo',
        '-vcodec','rawvideo',
        '-s', str(frame_width)+'x'+str(frame_height),
        '-pix_fmt', 'bgr24',
        '-r', str(FPS),
        '-i', '-',
        '-i', 'blank.wav',
        '-f', 'flv',
        '-vcodec', 'libx264',
        '-profile:v', 'main',
        '-acodec' , 'copy',
        '-g', str(10//FPS),
        '-keyint_min', str(10//FPS),
        #'-b:v', CBR,
        '-minrate', CBR,
        '-maxrate', CBR,
        '-pix_fmt', 'yuv420p',
        '-preset', 'veryslow',
        #'-tune', 'zerolatency',
        '-threads', '0',
        '-bufsize', CBR,
        config['upload_stream'] ]

    proc = sp.Popen(command, stdin=sp.PIPE, stderr=sp.STDOUT, bufsize=0)

    oframe = None
    toptime = time.clock_gettime(time.CLOCK_REALTIME)
    time.sleep(0.5)
    kframe=None
    while True:
        config=json.load(open("config.json","r"))
        if FPS != config["FPS"] or CBR != config["CBR"]:
            break
        req = urllib.request.urlopen('http://waterbase.uwm.edu/webcam/currentlink.jpg')
        arr = np.asarray(bytearray(req.read()), dtype=np.uint8)
        frame = cv2.imdecode(arr, cv2.IMREAD_COLOR) # 'Load it as it is'
        frame = cv2.resize(frame, (1920,1080))
        #if oframe is None or oframe.sum() != frame.sum():
        #print(frame.shape)
        #print(frame.dtype)
        #frame = frame - np.uint8(np.random.uniform(size=frame.shape))
        if kframe is None:
            kframe=np.float32(frame)
        else:
            kframe = kframe * 0.8 + np.float32(frame) * 0.2

        frame = np.uint8(kframe)
        print("[send frame]")
        proc.stdin.write(frame.tostring())
        nexttime = toptime + 1.0/FPS
        thistime = time.clock_gettime(time.CLOCK_REALTIME)
        diff = nexttime-thistime
        time.sleep(max(0,diff))
        toptime = nexttime
        oframe = frame


    print("stopping stream...")
    proc.stdin.close()
    proc.wait()
    print("restarting...")
