import backend
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QLabel, \
    QLineEdit, QGridLayout, QMessageBox
from PyQt5.QtGui import QIcon, QPixmap
import sys
import json
import os
import vlc
import tempfile
import threading
import time

# TODO: Жанры, кнопка назад, ИИ, андроид версия, минимизировать окно, переделать кнопки, сделать обложку на бекграунле

class Login(QWidget):
    login = ''
    passwd = ''
    grid = QGridLayout()
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('RandomVK')
        self.setWindowIcon(QIcon('web.png'))
        self.Login_Label = QLabel("Login:")
        self.Login_Input = QLineEdit('')
        self.Passwd_Label = QLabel("Passwd:")
        self.Passwd_Input = QLineEdit('')
        self.Passwd_Input.setEchoMode(QLineEdit.Password)
        self.Login_Button = QPushButton('Login')
        self.Login_Button.clicked.connect(self.onClick_login)
        self.grid.setSpacing(9)
        self.grid.addWidget(self.Login_Label, 0, 0)
        self.grid.addWidget(self.Login_Input, 0, 1)
        self.grid.addWidget(self.Passwd_Label, 1, 0)
        self.grid.addWidget(self.Passwd_Input, 1, 1)
        self.grid.addWidget(self.Login_Button, 1, 2)
        self.setLayout(self.grid)
        self.show()
    def onClick_login(self):
        try:
            login = self.Login_Input.text()
            passwd = self.Passwd_Input.text()
            global vk
            vk = backend.vk_audio(login=login, passwd=passwd)
            #raise backend.vk.exceptions.VkAuthError
            pass
        except backend.vk.exceptions.VkAuthError as VkAuthError:
            text = VkAuthError.args[0]
            err = QMessageBox()
            err.setText(text)
            err.setDefaultButton(QMessageBox.Ok)
            err.setText(text)
            err.buttonClicked.connect(self.msgbtn)
            retval = err.exec_()
        else:
            if os.name == "nt":
                Setting_File = open(os.getcwd() + '\\setting.json', 'w')
            else:
                Setting_File = open(os.getcwd() + '/setting.json', 'w')
            acc = {'access_token': vk.get_access_token()}
            Setting_Text = json.dumps(acc)
            print(Setting_Text, file=Setting_File, end='')
            Setting_File.close()
            self.hide()
            Player_UI.show()
            Player_UI.Next_Button.click()
            self.close()

class Player(QWidget):
    grid = QGridLayout()
    def __init__(self):
        super().__init__()
        self.instance = vlc.Instance()
        self.mediaplayer = self.instance.media_player_new()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('RandomVK')
        self.setWindowIcon(QIcon('web.png'))
        self.Author_Label = QLabel()
        self.Name_Label = QLabel()
        self.Add_Button = QPushButton('Add')
        self.Add_Button.clicked.connect(self.Click_Add)
        self.PP_Button = QPushButton('Play')
        self.PP_Button.clicked.connect(self.Click_PP)
        self.Next_Button = QPushButton('Next')
        self.Next_Button.clicked.connect(self.Click_Next)
        self.Song_Image_Label = QLabel(self)
        self.Song_Image = QPixmap('blank.png')
        self.Song_Image_Label.setPixmap(self.Song_Image)
        self.Cost_Label = QLabel('-')
        self.grid.setSpacing(9)
        self.grid.addWidget(self.Song_Image_Label, 0, 1)
        self.grid.addWidget(self.Author_Label, 1, 0)
        self.grid.addWidget(self.Cost_Label, 1, 1)
        self.grid.addWidget(self.Name_Label, 1, 2)
        self.grid.addWidget(self.Add_Button, 2, 0)
        self.grid.addWidget(self.Next_Button, 2, 2)
        self.grid.addWidget(self.PP_Button, 2, 1)
        self.setLayout(self.grid)

    def Click_Next(self):
        self.audio = vk.get_audio()
        temp = tempfile.gettempdir()
        if os.name == 'nt':
            temp += '\\RandomVK'
        else:
            temp += '/RandomVK'
        if not os.path.exists(temp):
            os.mkdir(temp)
        resp = backend.requests.get(self.audio['url'])
        if 'image' in self.audio:
            img = backend.requests.get(self.audio['image'])
        else:
            self.Song_Image.load('blank.png')
        if os.name == 'nt':
            tempfile_rand = open(temp + '\\temp.mp3', 'wb')
            tempfile_rand.write(resp.content)
            tempfile_rand.close()
            self.media = self.instance.media_new(temp + '\\temp.mp3')
            if 'image' in self.audio:
                tmp_image = open(temp + '\\temp.png', 'wb')
                tmp_image.write(img.content)
                tmp_image.close()
                self.Song_Image.load(temp + '\\temp.png')
        else:
            tempfile_rand = open(temp + '/temp.mp3', 'wb')
            tempfile_rand.write(resp.content)
            tempfile_rand.close()
            self.media = self.instance.media_new(temp + '/temp.mp3')
            if 'image' in self.audio:
                tmp_image = open(temp + '/temp.png', 'wb')
                tmp_image.write(img.content)
                tmp_image.close()
                self.Song_Image.load(temp + '/temp.png')
        try:
            self.mediaplayer.stop()
        except:
            pass
        self.Song_Image_Label.setPixmap(self.Song_Image)
        self.mediaplayer.set_media(self.media)
        self.mediaplayer.play()
        self.time_last = time.time()
        self.PP_Button.setText('Pause')
        self.Author_Label.setText(self.audio['artist'])
        self.Name_Label.setText(self.audio['title'])
        self.thread = threading.Thread(target=self.th)
        self.thread.daemon = True
        self.thread.start()
    def Click_Add(self):
        global vk
        vk.add(self.audio['id'], self.audio['aid'])
    def Click_PP(self):
        if self.mediaplayer.is_playing():
            self.mediaplayer.pause()
            self.PP_Button.setText("Play")
            self.time_last = time.time()
            del self.thread
        else:
            self.mediaplayer.play()
            self.time_last -= time.time()
            self.audio['duration'] -= int(self.time_last)
            self.audio['duration'] *= -1
            self.audio['duration'] += 15
            self.PP_Button.setText('Pause')
            self.thread = threading.Thread(target=self.th)
            self.thread.daemon = True
            self.thread.start()

    def th(self):
        time.sleep(int(self.audio['duration']))
        self.Next_Button.click()




if __name__ == '__main__':
    vk = 0
    app = QApplication(sys.argv)
    Player_UI = Player()
    try:
        Setting_file = open("setting.json", 'r')
    except FileNotFoundError:
        Login_UI = Login()
    else:
        Setting_json = ''
        Setting_dict = Setting_file.readlines()
        Setting_file.close()
        for s in Setting_dict:
            Setting_json += s
        if '{' in Setting_json:
            setting = json.loads(Setting_json)
            if 'access_token' in setting:
                try:
                    vk = backend.vk_audio(acc=setting['access_token'])
                except vk.exceptions.VkAuthError as VkAuthError:
                    Login_UI = Login()
                else:
                    Player_UI.show()
                    Player_UI.Next_Button.click()
            else:
                Login_UI = Login()
        else:
            Login_UI = Login()
        print()
    sys.exit(app.exec_())