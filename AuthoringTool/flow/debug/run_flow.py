from play_block import *
from datetime import datetime
import copy
import os.path


# block_player = play_block()
# time.sleep(1)


class FlowNode:
    block_player = None

    def __init__(self):
        self.flow = None
        self.prev_block = None
        self.next_block = None

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
                        'next': step_desc[3].lstrip()
                    }
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
                elif step_desc[1].lstrip() == 'interaction':
                    interaction_step = step_desc[0]
                    step_desc[2] = step_desc[2].lstrip()
                    self.flow[interaction_step] = {
                        'type': 'composite',
                        'block': 'pick_up_2_a',
                        'next': step_desc[0] + '.1'
                    }
                    the_props = step_desc[2].lstrip().split(' ')
                    self.flow[interaction_step]['sound'] = "%s_pick up the %s" % (self.flow['robot'][:-1], the_props[0])
                    if len(the_props) == 2:
                        self.flow[interaction_step]['sound'] += " and the %s" % the_props[1]
                    self.flow[interaction_step]['lip'] = self.flow[interaction_step]['sound'] + '.csv'
                    self.flow[interaction_step]['sound'] = self.flow[interaction_step]['sound'] + '.mp3'
                    self.flow[interaction_step]['correct'] = ''
                    for p in the_props:
                        self.flow[interaction_step]['correct'] += ' -' + p
                    self.flow[interaction_step]['props'] = self.flow[interaction_step]['correct'].lstrip().split(' ')

                    interaction_step = step_desc[0] + '.1'

                    self.flow[interaction_step] = {
                        'type': 'wait',
                        'duration': '10',
                        'false': step_desc[0] + '.2',
                        'timeout': step_desc[0] + '.3',
                        'true': step_desc[0] + '.4',
                    }
                    self.flow[interaction_step]['correct'] = ''
                    for p in the_props:
                        self.flow[interaction_step]['correct'] += ' -' + p
                    self.flow[interaction_step]['props'] = self.flow[interaction_step]['correct'].lstrip().split(' ')

                    interaction_step = step_desc[0] + '.2'
                    self.flow[interaction_step] = {
                        'type': 'block',
                        'block': "%s_try again 1" % self.flow['robot'][:-1],
                        'next': step_desc[0]
                    }

                    interaction_step = step_desc[0] + '.3'
                    self.flow[interaction_step] = {
                        'type': 'block',
                        'block': "%s_try again 2" % self.flow['robot'][:-1],
                        'next': step_desc[0]
                    }

                    interaction_step = step_desc[0] + '.4'
                    self.flow[interaction_step] = {
                        'type': 'block',
                        'block': "%s_very good well done 1" % self.flow['robot'][:-1],
                        'next': step_desc[0] + '.5'
                    }

                    interaction_step = step_desc[0] + '.5'
                    self.flow[interaction_step] = {
                        'type': 'composite',
                        'block': 'put_down_2_a',
                        'next': step_desc[0] + '.6'
                    }
                    the_props = step_desc[2].lstrip().split(' ')
                    self.flow[interaction_step]['sound'] = "%s_put down the %s" % (self.flow['robot'][:-1], the_props[0])
                    if len(the_props) == 2:
                        self.flow[interaction_step]['sound'] += " and the %s" % the_props[1]
                    self.flow[interaction_step]['lip'] = self.flow[interaction_step]['sound'] + '.csv'
                    self.flow[interaction_step]['sound'] = self.flow[interaction_step]['sound'] + '.mp3'
                    self.flow[interaction_step]['correct'] = ''
                    for p in the_props:
                        self.flow[interaction_step]['correct'] += ' +' + p
                    self.flow[interaction_step]['props'] = self.flow[interaction_step]['correct'].lstrip().split(' ')

                    interaction_step = step_desc[0] + '.6'

                    self.flow[interaction_step] = {
                        'type': 'wait',
                        'duration': '10',
                        'false': step_desc[0] + '.7',
                        'timeout': step_desc[0] + '.8',
                        'true': step_desc[0] + '.9',
                    }
                    self.flow[interaction_step]['correct'] = ''
                    for p in the_props:
                        self.flow[interaction_step]['correct'] += ' +' + p

                    self.flow[interaction_step]['props'] = self.flow[interaction_step]['correct'].lstrip().split(' ')

                    interaction_step = step_desc[0] + '.7'
                    self.flow[interaction_step] = {
                        'type': 'block',
                        'block': "%s_try again 1" % self.flow['robot'][:-1],
                        'next': step_desc[0] + '.5'
                    }

                    interaction_step = step_desc[0] + '.8'
                    self.flow[interaction_step] = {
                        'type': 'block',
                        'block': "%s_try again 2" % self.flow['robot'][:-1],
                        'next': step_desc[0] + '.5'
                    }

                    interaction_step = step_desc[0] + '.9'
                    self.flow[interaction_step] = {
                        'type': 'block',
                        'block': "%s_very good well done 2" % self.flow['robot'][:-1],
                        'next': step_desc[3].lstrip()
                    }
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
        while current_step != 'end':
            # check if all the props are there
            # say (put_down) for those who aren't
            if not current_step == 'correction_block' and '*' not in current_step:
                a_prop_is_missing = False
                # FlowNode.block_player.update_rifd()
                for p in self.flow['props']:
                    if p not in FlowNode.block_player.rfids and p not in current_prop:
                        # check if there is a proper file name
                        sound_file_name = "%s_put down the %s.mp3" % (self.flow['robot'][:-1], p)
                        if self.sound_exist(sound_file_name):
                            if 'next' in self.flow[current_step]: # wierd bug correction
                                self.flow['correction_block'] = {
                                    'type': 'composite',
                                    'block': self.base_path + 'blocks/'+ self.flow['robot'] + self.flow['robot'][:-1] + '_idle_1.new',
                                    'next': self.flow[current_step]['next'],
                                    'sound': "%s_put down the %s.mp3" % (self.flow['robot'][:-1], p),
                                    'lip': "%s_put down the %s.csv" % (self.flow['robot'][:-1], p),
                                    'props': []
                                }
                                current_step = 'correction_block'
                                a_prop_is_missing = True
                                FlowNode.block_player.sound_offset = 0.0
                if a_prop_is_missing:
                    time.sleep(1.0)
                    continue
            if self.flow[current_step]['type'] == 'wait':
                current_prop = []
                block_name = self.base_path + 'blocks/'+ self.flow['robot'] + self.flow['robot'][:-1] + '_idle_1.new'
                FlowNode.block_player.sound_filename = None
                FlowNode.block_player.lip_filename = None

                stopwatch_start = datetime.now()
                resolution = 'timeout'
                interupt_sequence = False
                while (datetime.now() - stopwatch_start).total_seconds() < float(self.flow[current_step]['duration']):
                    # ===============
                    self.play_complex_block(block_name)
                    # ================
                    if FlowNode.block_player.update_rifd(): # Removed because there is only a need to change current status and not change # FlowNode.block_player.update_rifd():
                        print('a change')
                        correct_resolution = 0
                        for p in self.flow[current_step]['props']:
                            if p[0] == '-':    # pick up
                                if p[1:] not in FlowNode.block_player.rfids:
                                    correct_resolution += 1
                                    current_prop.append(p[1:])
                            elif p[0] == '+':    # put down
                                if p[1:] in FlowNode.block_player.rfids:
                                    correct_resolution += 1
                                    current_prop.append(p[1:])
                        if correct_resolution  == 0:
                            resolution = 'false'
                            wrong_props = [p for p in FlowNode.block_player.rfid_change if p is not None]
                            # first check if there are any wrong props
                            if len(wrong_props) > 0:
                                self.flow['correction_block'] = {
                                    'type': 'composite',
                                    'block': self.base_path + 'blocks/'+ self.flow['robot'] + self.flow['robot'][:-1] + '_idle_1.new',
                                    'next': self.flow[current_step][resolution],
                                    'sound': "%s_this is a %s.mp3" % (self.flow['robot'][:-1], wrong_props[0]),
                                    'lip': "%s_this is a %s.csv" % (self.flow['robot'][:-1], wrong_props[0]),
                                    'props': []
                                }
                                current_step = 'correction_block'
                                interupt_sequence = True
                                FlowNode.block_player.sound_offset = 0.0
                                break
                        elif correct_resolution == len(self.flow[current_step]['props']):
                            resolution = 'true'
                            break
                        break
                    time.sleep(0.1)

                print('resolution:', resolution)
                if not interupt_sequence:
                    current_step = self.flow[current_step][resolution]
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
                current_step = self.flow[current_step]['next']

    def get_block_name(self, current_step):
        block_name = None
        if current_step != 'end':
            if self.flow[current_step]['type'] == 'block':
                block_name = self.base_path + 'blocks/' + self.flow['path'] + self.flow[current_step]['block']
            elif self.flow[current_step]['type'] == 'composite':
                if 'blocks' not in self.flow[current_step]['block']:
                    block_name = self.base_path + 'blocks/' + self.flow['path'] + self.flow[current_step]['block']
                else:
                    block_name = self.flow[current_step]['block']
            elif self.flow[current_step]['type'] == 'point':
                block_name = self.get_point_block(self.flow[current_step]['rfid'])
            elif self.flow[current_step]['type'] == 'mixed':
                block_name = self.base_path + 'blocks/' + self.flow['path'] + self.flow[current_step]['block']
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