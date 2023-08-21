
import sys, os
from pygame import mixer
import pygame
from dataclasses import dataclass
import time
import argparse
import paho.mqtt.client as mqtt
import pathlib
import json
from PyQt6.QtGui import QImage, QPixmap, QCloseEvent, QStandardItem, QStandardItemModel, QIcon, QColor
from PyQt6.QtWidgets import QApplication, QMainWindow, QTableView, QLabel, QPushButton, QMessageBox
from PyQt6.QtWidgets import QFileDialog
from PyQt6.uic import loadUi
from PyQt6.QtCore import QModelIndex, QObject, Qt, QTimer, QThread, pyqtSignal, QAbstractTableModel
from pyflame_avsim_mixer import mapi_mixer

WORKING_PATH = pathlib.Path(__file__).parent # working path
APP_UI = WORKING_PATH / "MainWindow.ui" # Qt-based UI file
RESOURCE_PATH = WORKING_PATH / pathlib.Path("sound")
APP_NAME = "avsim-mixer" # application name

# class MixerState(QTimer):
#     def __init__(self, interval_ms):
#         self.time_interval = interval_ms # default interval_ms = 100ms
#         self.setInterval(interval_ms)
#         self.timeout.connect(self.on_timeout_callback) # timer callback

#     def on_timeout_callback(self):
#         pygame.display.update()
#         print("update")
            
    
class AVSimMixer(QMainWindow):
    def __init__(self, broker_ip:str):
        super().__init__()
        loadUi(APP_UI, self)

        self._resource_files = [f for f in RESOURCE_PATH.iterdir() if f.is_file()]
        self._resource_sound = {}
        
        # mapi interface function (subscribe the mapi)
        self.message_api = {
            "flame/avsim/mixer/mapi_play" : self.mapi_play,
            "flame/avsim/mixer/mapi_stop" : self.mapi_stop,
            "flame/avsim/mixer/mapi_fadeout" : self.mapi_fadeout,
            "flame/avsim/mixer/mapi_set_volume" : self.mapi_set_volume,
            "flame/avsim/mapi_request_active" : self.mapi_request_active,
            "flame/avsim/carla/notify_alert_collision" : self._api_notify_alert_collision
        }

        self.resource_table_columns = ["Sound Resources"]
        
        # callback function connection for menu
        self.btn_play.clicked.connect(self.on_click_play)   # play selected sound file
        self.btn_stop.clicked.connect(self.on_click_stop)   # pause selected sound file
        self.btn_pause.clicked.connect(self.on_click_pause) # pause selected sound file
        self.btn_resume.clicked.connect(self.on_click_resume)  # resume selected sound file
        self.table_sound_files.doubleClicked.connect(self.on_dbclick_select) # play selected sound file
        
         # sound resournce
        self.resource_model = QStandardItemModel()
        self.resource_model.setColumnCount(len(self.resource_table_columns))
        self.resource_model.setHorizontalHeaderLabels(self.resource_table_columns)
        self.table_sound_files.setModel(self.resource_model)

        self.load_resource()
        
        # for mqtt connection
        self.mq_client = mqtt.Client(client_id="flame-avsim-mixer", transport='tcp', protocol=mqtt.MQTTv311, clean_session=True)
        self.mq_client.on_connect = self.on_mqtt_connect
        self.mq_client.on_message = self.on_mqtt_message
        self.mq_client.on_disconnect = self.on_mqtt_disconnect
        self.mq_client.connect_async(broker_ip, port=1883, keepalive=60)
        self.mq_client.loop_start()

    '''
     Message Interface Functions
    '''
    def mapi_notify_active(self):
        pass

    def mapi_notify_status(self):
        pass

    def mapi_request_active(self):
        if self.mq_client.is_connected():
            msg = {'app':APP_NAME}
            self.mq_client.publish("flame/avsim/mapi_request_active", json.dumps(msg), 0)

    # Sound Play
    def mapi_play(self, payload:dict):
        if "file" in payload.keys():
            sound_file = payload["file"]
            if "volume" in payload.keys():
                volume = float(payload["volume"])
            else:
                volume = 1.0

            if sound_file in self._resource_sound.keys():
                self.sound_play(sound_file, volume)

    # Sound Playing Stop
    def mapi_stop(self, payload):
        if "file" in payload.keys():
            sound_file = payload["file"]

            if sound_file in self._resource_sound.keys():
                self._resource_sound[sound_file].stop()

    def mapi_fadeout(self, payload):
        print("Not support yet")
        return
    
        if "file" in payload.keys():
            sound_file = payload["file"]
            if "fadeout_time" in payload.keys():
                self._resource_sound[sound_file].fadeout(int(payload["fadeout_time"]))

        

    # change sound volume
    def mapi_set_volume(self, payload):
        if "file" in payload.keys():
            sound_file = payload["file"]
            if "volume" in payload.keys():
                volume = float(payload["volume"])
                if sound_file in self._resource_sound.keys():
                    self._resource_sound[sound_file].set_volume(volume)
        

    def _api_notify_alert_collision(self, payload:dict):
        if type(payload) != dict:
            print("pyload must be type of dict")
            return
        
        alert_sound = "collision_alert_1.mp3"
        self.sound_play(alert_sound)

    def on_click_play(self):
        pass

    def on_click_stop(self):
        pass

    def on_click_pause(self):
        pass

    def on_click_resume(self):
        pass

    def sound_play(self, filename:str, volume:float=1.0):
        if filename in self._resource_sound.keys():
            print(type(self._resource_sound[filename]))
            self._resource_sound[filename].set_volume(volume)
            self._resource_sound[filename].play()
            row_index = self.resource_model.findItems(filename, Qt.MatchFlag.MatchExactly, 0)[0].row()


    def on_dbclick_select(self):
        row = self.table_sound_files.currentIndex().row()
        col = self.table_sound_files.currentIndex().column()

        if self._resource_files[row].name in self._resource_sound.keys():
            self._resource_sound[self._resource_files[row].name].play()
            self.resource_model.item(row,col).setBackground(QColor(255,0,0,100))
            self.sound_play(self._resource_files[row].name)
        
        
    def load_resource(self):
        self.resource_model.setRowCount(0)
        for resource in self._resource_files:
            self.resource_model.appendRow([QStandardItem(str(resource.name))])
            self._resource_sound[resource.name] = mixer.Sound(str(resource))
        self.table_sound_files.resizeColumnsToContents()
        
    # change row background color
    def _mark_row_color(self, row):
        for col in range(self.resource_model.columnCount()):
            self.resource_model.item(row,col).setBackground(QColor(255,0,0,100))
    
    # reset all rows background color
    def _mark_row_reset(self):
        for col in range(self.resource_model.columnCount()):
            for row in range(self.resource_model.rowCount()):
                self.resource_model.item(row,col).setBackground(QColor(0,0,0,0))
                
    def show_on_statusbar(self, text):
        self.statusBar().showMessage(text)

    # MQTT callbacks
    def on_mqtt_connect(self, mqttc, obj, flags, rc):
        # subscribe message api
        for topic in self.message_api.keys():
            self.mq_client.subscribe(topic, 0)
        
        self.show_on_statusbar("Connected to Broker({})".format(str(rc)))
        
    def on_mqtt_disconnect(self, mqttc, userdata, rc):
        self.show_on_statusbar("Disconnected to Broker({})".format(str(rc)))
        
    def on_mqtt_message(self, mqttc, userdata, msg):
        mapi = str(msg.topic)
        
        try:
            if mapi in self.message_api.keys():
                payload = json.loads(msg.payload)
                if "app" not in payload:
                    print("message payload does not contain the app")
                    return
                
                if payload["app"] != APP_NAME:
                    self.message_api[mapi](payload)
            else:
                print("Unknown MAPI was called :", mapi)

        except json.JSONDecodeError as e:
            print("MAPI Message payload cannot be converted")
        

if __name__ =="__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--broker', nargs='?', required=False, help="Broker Address")
    args = parser.parse_args()

    broker_address = "127.0.0.1"
    if args.broker is not None:
        broker_address = args.broker
        
    mixer.init()
        
    app = QApplication(sys.argv)
    window = AVSimMixer(broker_ip=broker_address)
    window.show()
    sys.exit(app.exec())
        
        