import sys
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.Qt import *
import os
from aip import AipFace
import urllib.request
import RPi.GPIO as GPIO
import base64
import threading
import time
import paizhao
import sqlite3

APP_ID = '26497573'
API_KEY = 'utSefp59lTAOjKdjUq6ERWxm'
SECRET_KEY ='9iN4xgEMNaNuG6WOUbmkGfAyr76emEwN '
client = AipFace(APP_ID, API_KEY, SECRET_KEY)
IMAGE_TYPE='BASE64'
GROUP = 'wjy_test001'

cg=2
u_name=' '
if_in_out_global=1

def updt_in(name):
    global if_in_out_global
    conn = sqlite3.connect('finalsql.db')
    c = conn.cursor()
    cursor = c.execute("SELECT name, num, if_in from user")
    if_in_out='is_in'
    for row in cursor:
        if_in_out=row[2]
    if if_in_out=='is_in':
        c.execute("UPDATE user set if_in = 'is_out' where name='%s'" %name)
        if_in_out_global=0
    if if_in_out=='is_out':
        c.execute("UPDATE user set if_in = 'is_in' where name='%s'" %name)
        if_in_out_global=1
    print('if_in_out=%s'%if_in_out)
    conn.commit()
    conn.close()

def transimage():
    time.sleep(1)
    f = open('faceimage.jpg','rb')
    img = base64.b64encode(f.read())
    go_api(img)
def go_api(image):
    global cg
    global u_name
    result = client.search(str(image, 'utf-8'), IMAGE_TYPE, GROUP);
    if result['error_msg'] == 'SUCCESS':
        name = result['result']['user_list'][0]['user_id']
        score = result['result']['user_list'][0]['score']
        if score > 80:
            #GUI().label.setText('识别成功')
            print('识别成功 %s' % name)
            u_name=name
            updt_in(name)
            cg=1
            time.sleep(3)
        else:
            print('靓仔你谁？')
            cg=0
            time.sleep(3)
    if result['error_msg'] == 'pic not has face':
        cg=2
        print(' ')
        time.sleep(3)
    #QApplication.processEvents()
    #print('%d' % cg)
    transimage()


class GUI(QWidget):
    
    def __init__(self):
        super().__init__()
        self.initGUI()
        self.updt()
    def initGUI(self):
        self.resize(700,700)
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())
        #设置窗口标题和图标
        self.setWindowTitle('180400316万景源')
        self.setWindowIcon(QIcon('2.png'))
        #设置窗口提示
        self.setToolTip('窗口提示')
        #设置label信息
        self.label = QLabel(self)
        self.label.setGeometry(QRect(100, 10, 150, 60))
        self.label.setText('这是lable信息')
        self.label.setObjectName('label')
        self.label1 = QLabel(self)
        self.label1.setPixmap(QPixmap('/home/pi/Desktop/aip-python-sdk-2.2.15/faceimage.jpg'))
        self.label1.setGeometry(QRect(50, 100, 640, 480))
        self.label2 = QLabel(self)
        self.label2.setGeometry(QRect(350, 10, 150, 60))
        self.label2.setText(' ')
        self.label3 = QLabel(self)
        self.label3.setGeometry(QRect(250, 10, 100, 60))
        self.label3.setText(' ')
        
        self.textbox = QLineEdit(self)
        self.textbox.resize(100, 20)
        self.textbox.move(100, 50)
        self.textbox.setToolTip('用户名')
        
        self.textbox2 = QLineEdit(self)
        self.textbox2.resize(100, 20)
        self.textbox2.move(200, 50)
        self.textbox2.setToolTip('学号')
        
        self.btn =QPushButton('录入',self)
        self.btn.resize(100,20)
        self.btn.move(300,50)
        self.btn.setStyleSheet("background-color: rgb(164, 185, 255);"
                          "border-color: rgb(255, 255, 255);"
                          "font: 75 12pt \"Arial Narrow\";"
                          "color: rgb(0, 0, 0);")
        self.btn.clicked.connect(self.clickbtn)
        
        self.show();
    
    def clickbtn(self):
        conn = sqlite3.connect('finalsql.db')
        c = conn.cursor()
        name_now=self.textbox.text()
        num_now=self.textbox2.text()
        c.execute("INSERT INTO user (name,num,if_in) VALUES ('%s', '%s', 'is_in')"%(name_now,num_now))
        self.label2.setText('新用户录入成功')
        conn.commit()
        conn.close()
        f = open('faceimage.jpg','rb')
        img = base64.b64encode(f.read())
        result=client.addUser(str(img, 'utf-8'), IMAGE_TYPE, GROUP, name_now);
        QApplication.processEvents()
#         textboxValue = self.textbox.text()
#         QMessageBox.question(self, "信息", '你输入的输入框内容为:' + textboxValue,QtWidgets.QMessageBox.Ok, QtWidgets.QMessageBox.Ok)
#         self.textbox.setText('')
    def updt(self):
        global cg
        time.sleep(1)
        self.label1.setPixmap(QPixmap('/home/pi/Desktop/aip-python-sdk-2.2.15/faceimage.jpg'))
        self.label1.setGeometry(QRect(50, 100, 640, 480))
        if cg==1:
            self.label.setText('识别成功%s' % u_name)
            if if_in_out_global==1:
                self.label3.setText('欢迎回来')
            if if_in_out_global==0:
                self.label3.setText('一路平安')
        elif cg==0:
            self.label.setText('靓仔你谁')
            self.label3.setText('')
        elif cg==2:
            self.label.setText(' ')
            self.label3.setText('')
            print('%d' % cg)
        QApplication.processEvents()
        self.updt()

        
        
t2 = threading.Thread(target=transimage)

    
if __name__ == '__main__':
    t2.start()
    app = QApplication(sys.argv)
    gui = GUI()
    sys.exit(app.exec_())