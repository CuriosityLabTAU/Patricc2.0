class Animal:
    def __init__(self, type, like, dislike):
        self.type = type
        self.state = 'sleaping'
        self.like = like
        self.dislike = dislike

    def controller(self, fruit):
        pass

    def reset(self):
        #resets the world
        pass


def is_change(rfids):
    pass


cover = ['orange', 'strawberry', 'water', 'lemon', 'banana']



# start pygame
#subscribe to - game controller
### if game activate is on  - continue, elif activation is off - reset and stop
#at callback check if change - is_change returns that anima that there was a change
#get from cover what the animal is on
#if there is change - send the fruit to the animal that has changed


