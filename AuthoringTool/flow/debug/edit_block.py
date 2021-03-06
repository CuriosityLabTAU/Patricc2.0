import pickle

block_filename = '../../blocks/Fuzzy_contest/Fuzzy contest 01'
# print 'block filename ', self.filename
with open(block_filename, 'rb') as input:
    play_block = pickle.load(input, encoding='latin1')
    print(play_block)