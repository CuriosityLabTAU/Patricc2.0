from play_block import *
from datetime import datetime
import copy
import os.path
import collections


# block_player = play_block()
# time.sleep(1)


class FlowNode:
    block_player = None

    def __init__(self):
        self.flow = None
        self.prev_block = None
        self.next_block = None

######################################################OG
        self.event_occured = False
        self.exit_step = 'start'
        self.wrong_in_air = []
        self.wrong_on_console = []

        self.activation = 'off'
        self.rule_sign = []
        self.rule = []
        self.event_goto = 'start'
######################################################

        self.base_path = '../'

    def sound_exist(self, file_name):
        full_name = self.base_path + 'sounds/' + self.flow['path'] + file_name
        return os.path.exists(full_name)

    def load(self, file_name='session_1.txt'):
        FlowNode.block_player.update_rifd()
        print(FlowNode.block_player.rfids)

        flow_sequence = open(file_name).read().split('\n')

        self.flow = {
            'robot': '',
            'path': ''
        }
        for step in flow_sequence:
            step_desc = step.split(',')
            if len(step_desc[0]) > 0:
                #print(step_desc)
                if step_desc[0].lstrip() == 'robot':
                    self.flow['robot'] = step_desc[1].lstrip() + '/'
                elif step_desc[0].lstrip() == 'path':
                    self.flow['path'] = step_desc[1].lstrip() + '/'
                elif step_desc[0].lstrip() == 'props':
                    self.flow['props'] = step_desc[1].lstrip().split(' ')
                elif step_desc[1].lstrip() == 'wait':
                    self.flow[step_desc[0]] = {'type': 'wait'}
                    for i in range(2, len(step_desc)):
                        param = step_desc[i].split(':')
                        self.flow[step_desc[0]][param[0].lstrip()] = param[1].lstrip()
                    self.flow[step_desc[0]]['props'] = self.flow[step_desc[0]]['correct'].split(' ')
                elif step_desc[1].lstrip() == 'block':
                    self.flow[step_desc[0]] = {
                        'type': 'block',
                        'block': step_desc[2].lstrip(),
                        'next': step_desc[3].lstrip().split(' ')
                    }
                    print 'we are here', step_desc[3].lstrip().split(' ')
                elif step_desc[1].lstrip() == 'composite':
                    self.flow[step_desc[0]] = {
                        'type': 'composite',
                        'block': step_desc[2].lstrip(),
                        'sound': step_desc[3].lstrip(),
                        'lip': step_desc[4].lstrip(),
                        'correct': step_desc[5].lstrip(),
                        'props': step_desc[6].lstrip().split(' '),
                        'next': step_desc[7].lstrip()
                    }
                    if self.flow[step_desc[0]]['lip'] == '*':
                        self.flow[step_desc[0]]['lip'] = self.flow[step_desc[0]]['sound'][:-3] + 'csv'
                elif step_desc[1].lstrip() == 'point':
                    self.flow[step_desc[0]] = {
                        'type': 'point',
                        'rfid': step_desc[2].lstrip(),
                        'sound': step_desc[3].lstrip(),
                        'lip': step_desc[4].lstrip(),
                        'next': step_desc[5].lstrip()
                    }
                    if self.flow[step_desc[0]]['lip'] == '*':
                        self.flow[step_desc[0]]['lip'] = self.flow[step_desc[0]]['sound'][:-3] + 'csv'
                elif step_desc[1].lstrip() == 'mixed':
                    self.flow[step_desc[0]] = {
                        'type': 'mixed',
                        'block': step_desc[2].lstrip(),
                        'inter_block': self.load_inter_block_sequence(step_desc[3].lstrip()),
                        'next': step_desc[4].lstrip()
                    }
                    self.flow[step_desc[0]]['motor_commands'] = self.convert_mixed(self.flow[step_desc[0]])
                elif step_desc[1].lstrip() == 'gaze_towards':
                    self.flow[step_desc[0]] = {
                        'type': 'gaze_towards',
                        'who': step_desc[2].lstrip(),
                        'next': step_desc[3].lstrip()
                    }
                elif step_desc[1].lstrip() == 'check_prop_state':
                    self.flow[step_desc[0]] = {
                        'type': 'check_prop_state',
                        'props_on_console': step_desc[2].lstrip().split(' '),
                        'next': step_desc[3].lstrip()
                    }
                elif step_desc[1].lstrip() == 'pick_up_something':
                    self.flow[step_desc[0]] = {
                        'type': 'pick_up_something',
                        'duration': step_desc[2].lstrip(),
                        'timeout': step_desc[3].lstrip(),
                        'repeats': step_desc[4].lstrip(),
                        'nothing_happened': step_desc[5].lstrip(),
                        'sound_name': step_desc[6].lstrip(),
                        'next': step_desc[7].lstrip(),
                    }

##################################################################################OG
                elif step_desc[1].lstrip() == 'loop_block':
                    self.flow[step_desc[0]] = {
                        'type': step_desc[1].lstrip(),
                        'block': step_desc[2].lstrip(),
                        'duration': step_desc[3].lstrip(),
                        'next': step_desc[4].lstrip(),
                    }
##################################################################################

##################################################################################OG
                elif step_desc[1].lstrip() == 'prop_event':
                    self.flow[step_desc[0]] = {
                        'type': step_desc[1].lstrip(),
                        'event_name': step_desc[2].lstrip(),
                        'activation': step_desc[3].lstrip(),
                        'rule_sign': step_desc[4].lstrip(),
                        'rule': step_desc[5].lstrip().split(' '),
                        'goto': step_desc[6].lstrip(),
                        'next': step_desc[7].lstrip(),
                    }
##################################################################################

##################################################################################OG

                elif step_desc[1].lstrip() == 'prop_block':
                    self.flow[step_desc[0]] = {
                        'type': step_desc[1].lstrip(),
                        'block': step_desc[2].lstrip(),
                        'prop' : step_desc[3].lstrip(),
                        'next': step_desc[4].lstrip()
                    }
##################################################################################

                else:
                    self.flow[step_desc[0]] = {
                        'type': 'block',
                        'block': step_desc[1].lstrip(),
                        'next': step_desc[2].lstrip()
                    }

    def load_inter_block_sequence(self, file_name=''):
        interupt = {}
        inter_sequence = open(self.base_path + 'blocks/' + self.flow['path'] + file_name).read().split('\n')
        for step in inter_sequence:
            step_desc = step.split(',')
            if len(step_desc) > 2:
                interupt[float(step_desc[0])] = [step_desc[1], step_desc[2]]
        return interupt

    def run(self):
        time.sleep(2)
        FlowNode.block_player.update_rifd()

        current_step = 'start'
        a_prop_is_missing = False
        current_prop = []
        self.exit_step = {}
        while current_step != 'end':
            # check if all the props are there
            # say (put_down) for those who aren't
########################################################OG
            if current_step == 'exit_step':
                current_step = self.exit_step
########################################################OG
            if self.activation=='on':
                self.check_event()
                if self.event_occured == True:
                    self.exit_step = current_step
                    current_step = self.event_goto

#########################################################################OG
            if self.flow[current_step]['type'] == 'loop_block':
                block_name = self.get_block_name(current_step)
                FlowNode.block_player.sound_filename = None
                FlowNode.block_player.lip_filename = None

                stopwatch_start = datetime.now()
                resolution = 'timeout'
                interupt_sequence = False
                while (datetime.now() - stopwatch_start).total_seconds() < float(self.flow[current_step]['duration']):
                    # ===============
                    self.play_complex_block(block_name)
                    # ================
                    if self.event_occured == True:
                        break
                    time.sleep(0.1)
                current_step = self.flow[current_step]['next']
##########################################################################OG temp
             #else:
             #   block_name = self.get_block_name(current_step)
             #   FlowNode.block_player.sound_filename = None
             #   self.next_block = self.get_block_name(self.flow[current_step]['next'])
             #   stop_on_sound = False #self.flow[current_step]['type'] == 'point' #TODO
             #   self.play_complex_block(block_name, stop_on_sound=stop_on_sound)
             #   current_step = self.flow[current_step]['next']
##########################################################################
            elif self.flow[current_step]['type'] == 'prop_event':
                self.activation = self.flow[current_step]['activation']
                self.event_name = self.flow[current_step]['event_name']
                self.rule_sign = self.flow[current_step]['rule_sign']
                self.rule = self.flow[current_step]['rule']
                if self.rule == 'wrong_in_air':
                    self.rule = self.wrong_in_air[0]
                elif self.rule == 'wrong_on_console':
                    self.rule = self.wrong_on_console[0]
                self.event_goto = self.flow[current_step]['goto']
                current_step = self.flow[current_step]['next']
############################################################################

############################################################################OG
            #elif self.flow[current_step]['type'] == 'prop_block':
            #    block_name = self.get_block_name(current_step)
            #    self.next_block = self.get_block_name(self.flow[current_step]['next'])
            #    stop_on_sound = False # TODO: OG - check with Goren what stop_on_sound is
            #    block_name = block_name.format(self.flow[current_step]['prop'])
            #    self.play_complex_block(block_name, stop_on_sound=stop_on_sound)
            #    current_step = self.flow[current_step]['next']
###########################################################################
            elif self.flow[current_step]['type'] == 'gaze_towards':
                print 'here', self.flow[current_step]['who']
                FlowNode.block_player.mode_publisher.publish(self.flow[current_step]['who'])
                current_step = self.flow[current_step]['next']
            elif self.flow[current_step]['type'] == 'check_prop_state':
                print "detected", FlowNode.block_player.rfids, "desired", self.flow[current_step]['props_on_console']
                if collections.Counter(FlowNode.block_player.rfids) == collections.Counter(self.flow[current_step]['props_on_console']):
                    print "all good"
                else:
                    print "prop correction"
                current_step = self.flow[current_step]['next']
            else:
                block_name = self.get_block_name(current_step)
                FlowNode.block_player.sound_filename = None
                if self.flow[current_step]['type'] == 'composite':
                    FlowNode.block_player.sound_filename = self.base_path + 'sounds/' + self.flow['path'] + self.flow[current_step]['sound']
                    FlowNode.block_player.lip_filename = self.base_path + 'sounds/' + self.flow['path'] + self.flow[current_step]['lip']
                elif self.flow[current_step]['type'] == 'point':
                    FlowNode.block_player.sound_filename = self.base_path + 'sounds/' + self.flow['path'] + self.flow[current_step]['sound']
                    FlowNode.block_player.lip_filename = self.base_path + 'sounds/' + self.flow['path'] + self.flow[current_step]['lip']

                print('block: ', block_name, FlowNode.block_player.sound_filename)
                self.next_block = self.get_block_name(self.flow[current_step]['next'])
                FlowNode.block_player.update_rifd()
                print('next block:', self.next_block)
                stop_on_sound = False #self.flow[current_step]['type'] == 'point' #TODO
                if self.flow[current_step]['type'] == 'mixed':
                    self.flow[current_step]['motor_commands'] = self.convert_mixed(self.flow[current_step])
                    self.play_complex_block(block_name, stop_on_sound=stop_on_sound,
                                            motor_commands=self.flow[current_step]['motor_commands'])
                elif self.flow[current_step]['type'] == 'composite':
                    required_prop_is_in_proper_position = True
                    for p in self.flow[current_step]['props']:
                        if p[0] == '-':    # pick up
                            if p[1:] not in FlowNode.block_player.rfids:
                                required_prop_is_in_proper_position = False
                        elif p[0] == '+':    # put down
                            if p[1:] in FlowNode.block_player.rfids:
                                required_prop_is_in_proper_position = False
                    if required_prop_is_in_proper_position:
                        self.play_complex_block(block_name, stop_on_sound=stop_on_sound)
                    else:
                        current_step = self.flow[current_step]['next']
                        current_step = self.flow[current_step]['true']
                        current_step = self.flow[current_step]['next']
                        continue
                else:
                    self.play_complex_block(block_name, stop_on_sound=stop_on_sound)
                current_step = self.flow[current_step]['next'][0]

    def get_block_name(self, current_step):
        block_name = None
        if current_step != 'end':
            if self.flow[current_step]['type'] == 'block':
                block_name = self.base_path + 'blocks/' + self.flow['path'] + self.flow[current_step]['block']
##################################################################OG
            elif self.flow[current_step]['type'] == 'loop_block':
                block_name = self.base_path + 'blocks/' + self.flow['path'] + self.flow[current_step]['block']
##################################################################
            elif self.flow[current_step]['type'] == 'composite':
                if 'blocks' not in self.flow[current_step]['block']:
                    block_name = self.base_path + 'blocks/' + self.flow['path'] + self.flow[current_step]['block']
                else:
                    block_name = self.flow[current_step]['block']
            elif self.flow[current_step]['type'] == 'point':
                block_name = self.get_point_block(self.flow[current_step]['rfid'])
            elif self.flow[current_step]['type'] == 'mixed':
                block_name = self.base_path + 'blocks/' + self.flow['path'] + self.flow[current_step]['block']
            elif self.flow[current_step]['type'] == 'prop_block':
                block_name = self.base_path + 'blocks/' + self.flow['path'] + self.flow[current_step]['block'].format(self.flow[current_step]['prop'])
                print "testing", block_name
        return block_name

    def get_point_block(self, rfid):
        print('rfid: ', rfid)
        try:
            # rfid_pos = 1 + FlowNode.block_player.rfids.index(rfid)
            rfid_pos = 5 - FlowNode.block_player.rfids.index(rfid)
        except:
            print('ERROR: rfid %s not in list! Chaning to 1' % rfid)
            rfid_pos = 1
        block_name = self.base_path + 'blocks/' + self.flow['robot'] + 'point_%d' % rfid_pos
        print block_name
        return block_name

    def play_complex_block(self, block_name, stop_on_sound=False, motor_commands=None):
        print block_name
        FlowNode.block_player.load_block(block_name)
        new_motor_commands = FlowNode.block_player.stitch_blocks(block_before=self.prev_block,
                                                        block_after=self.next_block,
                                                        motor_commands=motor_commands)
        FlowNode.block_player.play_editted(motor_commands=new_motor_commands, stop_on_sound=stop_on_sound)
        self.prev_block = block_name

    def convert_mixed(self, the_block=None):
        if the_block:
            # get other blocks
            for k, v in the_block['inter_block'].items():
                if v[0] == 'point':
                    point_block_name = self.get_point_block(v[1])
                    point_block = play_block()
                    point_block.base_path = self.base_path
                    point_block.load_block(point_block_name)
                    v.append(point_block)

            # get inter block sequence
            main_block = play_block()
            main_block.base_path = self.base_path
            current_block_filename = self.base_path + 'blocks/' + self.flow['path'] + the_block['block']
            main_block.load_block(current_block_filename)

            # get the lips, for future reference
            temp_motor_commands = main_block.convert_to_motor_commands()
            lip_motor_commands = np.zeros([temp_motor_commands.shape[0], 2])
            lip_motor_commands[:, 0] = temp_motor_commands[:, 0]
            lip_motor_commands[:, 1] = temp_motor_commands[:, 4]


            inter_times = sorted(the_block['inter_block'].keys())
            inter_times.append(main_block.duration)

            sequence_blocks = []
            current_block_times = [0.0, float(inter_times[0])]
            if inter_times[0] > 0.0:
                sequence_blocks.append(main_block.cut_sub_block(start=current_block_times[0],
                                                                end=current_block_times[1]))
                current_block_times[0] += sequence_blocks[-1].duration

            for i in range(len(inter_times)-1):
                sequence_blocks.append(the_block['inter_block'][inter_times[i]][-1])

                current_block_times[0] += sequence_blocks[-1].duration
                current_block_times[1] = inter_times[i+1]

                if current_block_times[1] < current_block_times[0]:
                    break
                sequence_blocks.append(main_block.cut_sub_block(start=current_block_times[0],
                                                                end=current_block_times[1]))
                current_block_times[0] += sequence_blocks[-1].duration


            # stitch all blocks
            new_block_commands = sequence_blocks[0].stitch_blocks(block_after=sequence_blocks[1])

            for i_seq in range(1, len(sequence_blocks) - 1):
                # add_motor_commands = np.copy(sequence_blocks[i_seq].stitch_blocks(block_before=sequence_blocks[i_seq-1],
                #                                                                   block_after=sequence_blocks[i_seq+1]))
                add_motor_commands = np.copy(sequence_blocks[i_seq].convert_to_motor_commands())
                new_block_commands = self.append_motor_commands(new_block_commands, add_motor_commands)
            add_motor_commands = np.copy(sequence_blocks[-1].stitch_blocks(block_before=sequence_blocks[-2]))
            new_block_commands = self.append_motor_commands(new_block_commands, add_motor_commands)

            # assume lips is longer ...
            final_motor_commands = np.zeros([lip_motor_commands.shape[0], new_block_commands.shape[1]])
            final_motor_commands[:, 0] = lip_motor_commands[:, 0]
            final_motor_commands[:, 4] = lip_motor_commands[:, 1]
            for i in [1, 2, 3, 5, 6, 7, 8]:
                final_motor_commands[:, i] = np.interp(final_motor_commands[:, 0],
                                                       new_block_commands[:, 0],
                                                       new_block_commands[:, i])

            return final_motor_commands

    def append_motor_commands(self, motor_commands_1, motor_commands_2):
        new_motor_commands = np.copy(np.concatenate((motor_commands_1, motor_commands_2), axis=0))
        new_motor_commands[motor_commands_1.shape[0]:, 0] += motor_commands_1[-1, 0]
        return new_motor_commands

##################################################OG
    def check_event(self):
        self.wrong_in_air = []
        self.wrong_on_console = []
        detected_props = [x for x in FlowNode.block_player.rfids if x != None]
        print 'detected: ', detected_props, ' rule: ', self.rule
        if set(detected_props)==set(self.rule):
            if self.rule_sign == 'positive':
                self.event_occured = True
            elif self.rule_sign == 'negative':
                self.event_occured = False
        else:
            if self.rule_sign == 'negative':
                self.event_occured = True
            elif self.rule_sign == 'positive':
                self.event_occured = False
        print self.event_occured
        self.wrong_in_air = np.setdiff1d(self.rule,detected_props)
        self.wrong_on_console = np.setdiff1d(detected_props, self.rule)
        time.sleep(0.5)
#################################################


#flow = FlowNode()
# === demo ====
# flow.load('session_fuzzy_interaction.txt')
#flow.load('session_jay_interaction.txt')

# === development =====
# flow.load('session_point_test.txt')
# flow.load('session_fuzzy_interaction_onesong.txt')
# flow.load('session_jay_interaction_onesong.txt')

# ========= lessons =========
# flow.load('flow_lesson_2.txt')
# flow.run()