from alsainterface import ManagerStatus

class SongManager:
    def __init__(self, songs):

        self.status = ManagerStatus(songs, self.runCallbacks)

        self.callbacks = []

        self.running = True
        print ('Running...\n')

    def assignCallback(self, callback):
        self.callbacks.append(callback)

    def runCallbacks(self):
        status = self.status.getFullStatus()
        for cbk in self.callbacks:
            cbk(status)

    def nextSong(self):
        self.status.setNextSong()
        self.runCallbacks()

    def previousSong(self):
        self.status.setPreviousSong()
        self.runCallbacks()

    def nextTone(self):
        self.status.setNextTone()
        self.runCallbacks()

    def previousTone(self):
        self.status.setPreviousTone()
        self.runCallbacks()

    def reset(self):
        self.status.resetState()
        self.runCallbacks()
    
    def setSong(self, song):
        self.status.setSong(song)
        self.runCallbacks()

    def on_closing(self):
        self.status.on_closing()
        self.running = False

    def run(self):
        self.status.input_loop()

