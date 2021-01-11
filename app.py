#!/usr/bin/env python
from importlib import import_module
import os
import sys
from flask import Flask, render_template, Response, request, abort
import time

from camera import Camera, dsize
import camera

import threading
import queue

# 時間計測開始
time_sta = time.time()

def set_interval(func, sec):
    def func_wrapper():
        set_interval(func, sec)
        func()
    t = threading.Timer(sec, func_wrapper)
    t.start()
    return t
  
def set_timer(func,sec):
  t = threading.Timer(sec,func)
  t.start()
  return t

app = Flask(__name__)

fps = 30.0
delay = 0
frames = queue.Queue()

@app.after_request
def after_request(response):
  response.headers.add('Access-Control-Allow-Origin', '*')
  response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
  response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
  return response

@app.route('/')
def index():
    return "Hello World"

@app.route('/stream')
def stream():
    """Video streaming home page."""
    return render_template('stream.html')


def gen(camera):
    global frames, time_sta,delay
    """Video streaming generator function."""
    while True:

        # 時間計測
        time_end = time.time()
        # 経過時間（秒）
        tim = time_end- time_sta

        # FPS制御
        if tim > (1/fps) :
          frames.put(camera.get_frame())
          time_sta = time_end

        if frames.qsize() > delay * fps:
          yield (b'--frame\r\n'
            b'Content-Type: image/jpeg\r\n\r\n' + frames.get() + b'\r\n')

        


@app.route('/video_feed')
def video_feed():
    """Video streaming route. Put this in the src attribute of an img tag."""
    return Response(gen(Camera()),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


#パラメータ変更
@app.route('/params', methods=['POST'])
def change_params():
    global fps,delay
    print("params change requested")
    try:
        if request.method == 'POST':
            data = request.json
            print(data)
            fps = float(data['fps'])
            delay = float(data['delay'])
            print(data)
            return ""
        else:
            return abort(400)
    except Exception as e:
        return str(e)


#カメラ画像解像度変更
@app.route('/dsize', methods=['POST'])
def change_dsize():
    global dsize
    print("dsize change requested")
    print("current")
    print(dsize)
    try:
        if request.method == 'POST':
            data = request.json
            print(data)
            camera.dsize = (int(data['dsize_x']),int(data['dsize_y']))
            print(dsize)
            return ""
        else:
            return abort(400)
    except Exception as e:
        return str(e)

if __name__ == '__main__':
    port = int(sys.argv[1])
    app.run(host='0.0.0.0',port=port, threaded=True)
