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

    def setTone(self, n):
        self.status.setTone(n)
        self.runCallbacks()

    def reset(self):
        self.status.resetState()
        self.runCallbacks()
    
    def setSong(self, song):
        self.status.setSong(song)
        self.runCallbacks()

    def toggleAT(self):
        self.status.toggleAT()
        self.runCallbacks()

    def togglePedal(self):
        self.status.togglePedal()
        self.runCallbacks()

    def getCLICommands(self):
        return [self.nextSong, self.previousSong, self.reset, self.setSong]

    def getGUICommands(self):
        return [self.previousSong, 
                self.nextSong, 
                self.toggleAT, 
                self.togglePedal, 
                self.nextTone, 
                lambda: self.setTone(0),
                lambda: self.setTone(1),
                lambda: self.setTone(2),
                lambda: self.setTone(3)
                ]

    def initializeCallbacks(self, cbks):
        for cbk in cbks:
            self.assignCallback(cbk)
        self.runCallbacks()


    def on_closing(self):
        self.status.on_closing()
        self.running = False

    def run(self):
        self.status.input_loop()

