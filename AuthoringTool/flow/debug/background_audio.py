import rospy
from std_msgs.msg import String
from pygame import mixer
import time
import numpy as np
from map_props import *
from pygame import mixer
from copy import copy
from copy import deepcopy
from datetime import datetime
import random





class BackgroundAudio():
    def __init__(self):
        self.rfids = [None for i in range(5)]
        self.activation = 'on'
        self.animal_states  = {'cow':'sleeping', 'donkey':'sleeping', 'sheep':'sleeping'}
        self.cover = ['orange', 'strawberry', 'water', 'lemon', 'banana']
        self.animals = ['cow', 'donkey', 'sheep']
        self.is_rfid_change = False
        self.rfid_change = []
        self.rfid_prev = [None for i in range(5)]
        self.food_preferences = {'cow':{'like':['lemon', 'banana'],
                                        'dislike':['orange', 'strawberry'],
                                        'state':'sleep',
                                        'state_time':datetime.now()},
                                 'donkey':{'like':['strawberry', 'lemon'],
                                           'dislike':['orange', 'banana'],
                                           'state':'sleep',
                                           'state_time':datetime.now()},
                                 'sheep':{'like':['strawberry', 'orange'],
                                           'dislike':['lemon', 'banana'],
                                          'state':'sleep',
                                          'state_time':datetime.now()}}
        self.eat_log = {'cow':{'eat':0, 'action':0},
                        'donkey':{'eat':0, 'action':0},
                        'sheep':{'eat':0, 'action':0}}
        self.max_activity = 6
        self.max_eat = 3
        self.last_action_time = datetime.now()
        self.sounds = {'cow':{'yummy':[], 'yuck':[], 'drink':[], 'yawn':[], 'bored':[], 'regular':[]},
                       'donkey':{'yummy':[], 'yuck':[], 'drink':[], 'yawn':[], 'bored':[], 'regular':[]},
                       'sheep':{'yummy':[], 'yuck':[], 'drink':[], 'yawn':[], 'bored':[], 'regular':[]}}
        self.wake_up_time = [15, 45]
        self.max_sleep = 60
        self.last_action = 'start'
        self.sleep_log = {'cow': {'sleep':'false', 'time':datetime.now()},
                          'donkey': {'sleep':'false', 'time':datetime.now()},
                          'sheep': {'sleep':'false', 'time':datetime.now()}}
        mixer.init()
        rospy.init_node('world')
        rospy.Subscriber('/rfid', String, self.callback_rfid)
        rospy.Subscriber('/game_activation', String, self.callback_activation)
        self.world_publisher = rospy.Publisher('/world_action', String, queue_size=10)

        rospy.spin()



    def start(self):
        mixer.init()
        rospy.init_node('world')
        rospy.Subscriber('/rfid', String, self.callback_rfid)
        rospy.Subscriber('/game_activator', String, self.callback_activation)
        #self.mode_publisher = rospy.Publisher('/patricc_activation_mode', String, queue_size=10)
        rospy.spin()

    def callback_rfid(self, data):
        msg = data.data
        for i in range(5):
            rfid = msg[i*8:(i+1)*8]
            if '---' in rfid:
                self.rfids[i] = None
            else:
                try:
                    self.rfids[i] = rfid_to_prop[rfid]
                except:
                    pass
        self.is_rfid_change = False
        #print ['rfids : ' , self.rfids]
        for i in range(5):
            if self.rfids[i] != self.rfid_prev[i]:
                self.rfid_change = [self.rfids[i], self.cover[i]]
                if self.rfid_prev[i]==None:
                    self.is_rfid_change = True
        self.rfid_prev = deepcopy(self.rfids)
        self.controller()

        #for prop in self.rfids:
        #    if isinstance(prop, str):
        #        print prop, type(prop)
        #       if mixer.music.get_busy() == False:
        #            file_name = '/home/gorengordon/PycharmProjects/Patricc2.0/AuthoringTool/sounds/game_1/a ' + prop +'.mp3'
        #            print file_name
        #            mixer.music.load(file_name)
        #            mixer.music.set_volume(0.7)
        #            mixer.music.play()
            #print self.rfids

    def callback_activation(self, data):
        msg = data.data
        if self.activation == 'off':
            if msg == 'game_2':
                self.reset()
                self.activation = 'on'
        elif self.activation == 'on':
            if msg != 'game_2':
                self.activation = 'off'

    def reset(self):
        self.rfids = [None for i in range(5)]
        self.activation = 'on'
        self.animal_states  = {'cow':'sleeping', 'donkey':'sleeping', 'sheep':'sleeping'}
        self.cover = ['orange', 'strawberry', 'water', 'lemon', 'banana']
        self.animals = ['cow', 'donkey', 'sheep']
        self.is_rfid_change = False
        self.rfid_change = []
        self.rfid_prev = [None for i in range(5)]
        self.food_preferences = {'cow':{'like':['lemon', 'banana'],
                                        'dislike':['orange', 'strawberry'],
                                        'state':'sleep',
                                        'state_time':datetime.now()},
                                 'donkey':{'like':['strawberry', 'lemon'],
                                           'dislike':['orange', 'banana'],
                                           'state':'sleep',
                                           'state_time':datetime.now()},
                                 'sheep':{'like':['strawberry', 'orange'],
                                           'dislike':['lemon', 'banana'],
                                          'state':'sleep',
                                          'state_time':datetime.now()}}
        self.eat_log = {'cow':{'eat':0, 'action':0},
                        'donkey':{'eat':0, 'action':0},
                        'sheep':{'eat':0, 'action':0}}
        self.max_activity = 6
        self.max_eat = 3
        self.last_action_time = datetime.now()
        self.sounds = {'cow':{'yummy':[], 'yuck':[], 'drink':[], 'yawn':[], 'bored':[], 'regular':[]},
                       'donkey':{'yummy':[], 'yuck':[], 'drink':[], 'yawn':[], 'bored':[], 'regular':[]},
                       'sheep':{'yummy':[], 'yuck':[], 'drink':[], 'yawn':[], 'bored':[], 'regular':[]}}
        self.wake_up_time = [15, 45]
        self.max_sleep = 60
        self.last_action = 'start'
        self.sleep_log = {'cow': {'sleep':'false', 'time':datetime.now()},
                          'donkey': {'sleep':'false', 'time':datetime.now()},
                          'sheep': {'sleep':'false', 'time':datetime.now()},}

    def play_sound(self, animal, action):
        #sound_file = random.choice(self.sounds[animal][action])
        sound_file = animal + '_' + action + '_' + str(random.randint(1, 3))
        sound_file_w_path = '/home/gorengordon/PycharmProjects/Patricc2.0/AuthoringTool/sounds/game_2/' + sound_file + '.mp3'
        mixer.music.load(sound_file_w_path)
        mixer.music.play()


    def controller(self):
        #print 'here'
        #self.world_publisher.publish('hello hello')
        if self.activation=='on':
            if mixer.music.get_busy()==False:
                #print 'here', self.rfids, self.is_rfid_change
                current_time = datetime.now()
                if (current_time-self.last_action_time).total_seconds() > self.wake_up_time[0] and self.last_action != 'regular':
                    #print (current_time-self.last_action_time).total_seconds()
                    self.play_sound(random.choice(self.animals), 'regular')
                    self.last_action_time = datetime.now()
                    self.last_action = 'regular'
                    self.world_publisher.publish(self.last_action)
                elif (current_time-self.last_action_time).total_seconds() > self.wake_up_time[1] and self.last_action != 'bored':
                    self.play_sound(random.choice(self.animals), 'bored')
                    self.last_action_time = datetime.now()
                    self.last_action = 'bored'
                    self.world_publisher.publish(self.last_action)
                elif self.is_rfid_change==True:
                    animal = self.rfid_change[0]
                    food = self.rfid_change[1]
                    sleep_time = self.sleep_log[animal]['time']
                    if self.sleep_log[animal]['sleep'] == 'true' and (current_time-sleep_time).total_seconds()>self.max_sleep:
                        self.sleep_log[animal]['sleep'] = 'false'
                    if self.sleep_log[animal]['sleep'] == 'false':
                        if food!=None:
                            if food in self.food_preferences[animal]['like']: # if this is something the animal likes
                                self.eat_log[animal]['eat'] += 1
                                self.eat_log[animal]['action'] += 1
                                self.play_sound(animal, 'yummy')
                                self.last_action = 'yummy'
                                self.world_publisher.publish(self.last_action)
                            elif food in self.food_preferences[animal]['dislike']:
                                self.eat_log[animal]['action'] += 1
                                self.play_sound(animal, 'yuck')
                                self.last_action = 'yuck'
                                self.world_publisher.publish(self.last_action)
                            elif food == 'water':
                                self.eat_log[animal]['action'] += 1
                                self.play_sound(animal, 'drink')
                                self.last_action = 'drink'
                                self.world_publisher.publish(self.last_action)
                            if self.eat_log[animal]['action']>self.max_activity or self.eat_log[animal]['eat']>self.max_eat:
                                while mixer.music.get_busy():
                                    time.sleep(0.1)
                                self.play_sound(animal, 'yawn')
                                self.last_action = 'yawn'
                                self.eat_log[animal]['action'] = 0
                                self.eat_log[animal]['eat'] = 0
                                self.sleep_log[animal]['sleep'] = 'true'
                                self.sleep_log[animal]['time'] = datetime.now()
                                self.world_publisher.publish(self.last_action)
                            self.is_rfid_change = False
                            self.last_action_time = datetime.now()
                #print self.last_action
            #self.world_publisher.publish(self.last_action)
            time.sleep(0.1)


ba = BackgroundAudio()
#ba.start()

