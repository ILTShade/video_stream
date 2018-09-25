#-*-coding:utf-8-*-
import hashlib
from flask import Flask, Response, request, redirect, render_template
import time, cv2

# 设置和检查cookie
legal_valid = hashlib.md5(('sunaizhou' + '1314').encode()).hexdigest()
def set_cookie(username, password):
  this_valid = hashlib.md5((username + password).encode()).hexdigest()
  response = redirect('/')
  response.set_cookie('valid', this_valid, max_age = 3600)
  return response

def check_cookie():
  this_valid = request.cookies.get('valid')
  return this_valid == legal_valid

# 图片响应
frequency = 20.
class Camera(object):
  def __init__(self):
    self.cap = cv2.VideoCapture(0)
    print('init a new camera')
  def get_frame(self):
    ret, frame = self.cap.read()
    frame = cv2.imencode('.jpg', frame)[1].tobytes()
    time.sleep(1 / frequency)
    return frame

# app是Flask的一个实例，一般传递__name__作为输入
app = Flask(__name__)

# 绑定'/'，根据cookie决定是允许登陆还是重定向到登陆界面
@app.route('/')
def homepage():
  if check_cookie():
    return redirect('/secret')
  else:
    return redirect('/login')

# 登陆界面
@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/login', methods = ['POST'])
def do_login():
  username = request.form['username']
  password = request.form['password']
  response = set_cookie(username, password)
  return response

# secret界面
@app.route('/secret')
def secret():
    if check_cookie():
        return render_template('secret.html')
    else:
        return redirect('/')

# 一个用来产生图片的生成器
def gen():
    camera = Camera()
    while True:
        frame = camera.get_frame()
        yield (b'--frame\nContent-Type: image/jpeg\n\n' + frame + b'\n')

# 根据生成的图片，用来产生对应的地址
@app.route('/secret_feed')
def secret_feed():
    if check_cookie():
        return Response(gen(), mimetype = 'multipart/x-mixed-replace; boundary=frame')
    else:
        return redirect('/')

# host
app.run(host = '0.0.0.0', port = '5200', threaded = True, debug = False)
