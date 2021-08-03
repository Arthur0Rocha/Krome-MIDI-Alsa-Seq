import alsaseq
import os

def aplaymidi(filename):
    os.system(f'aplaymidi -p KROME -d 0 {filename}')

def aconnect(dev1, dev2):
    os.system(f'aconnect {dev1} {dev2}')

def createMIDIfile(filename, bank=0, tone=0):
    strout =  b'MThd\x00\x00\x00\x06\x00\x00\x00\x01\x03\xc0MTrk\x00\x00\x00\x0f\x00\xb0\x00\x00\x00\xb0\x20'  \
            + bytes([bank]) + b'\x00\xc0' \
            + bytes([tone]) + b'\x00\xff\x2f\x00'

    f = open(filename, 'wb')
    f.write(strout)
    f.close()

def changeBankTone(bank, tone):
    fname = f"midi-files/{['A','B','C','D','E','F'][bank]}{tone:03d}.MID"
    if not os.path.isfile(fname):
        createMIDIfile(fname, bank, tone)
    aplaymidi(fname)

def managePM(channel, value):
    aplaymidi(f'midi-files/MIDI.{channel}.{127 if value > 0 else 1}.MID')

class ManagerStatus:
    def __init__(self, songs, requestSystemUpdate):
        self.songs = songs

        alsaseq.client('Arthur SEQ', 1, 1, False)

        aconnect("\"Vortex Wireless 2\"", "KROME")
        aconnect("\"Vortex Wireless 2\"", "Arthur SEQ")
        aconnect("KROME", "Arthur SEQ")
        aconnect("\"Arthur SEQ\":1", "KROME")
        
        self.requestSystemUpdate = requestSystemUpdate

        self.running = True

        self.resetState()
        
    def getCurrentSong(self):
        return self.songs[self.currentSong][1]

    def getNextSong(self):
        index = self.currentSong + 1
        if index >= len(self.songs):
            index = 0
        return self.songs[index][1]
    
    def getPreviousSong(self):
        index = self.currentSong - 1
        if index < 0:
            index = len(self.songs) - 1
        return self.songs[index][1]

    def getCurrentTone(self):
        return self.songs[self.currentSong][0][self.currentTone]

    def getNextTone(self):
        nextTone = self.currentTone + 1
        if nextTone >= len(self.songs[self.currentSong][0]):
            nextTone = 0
        return self.songs[self.currentSong][0][nextTone]

    def getPreviousTone(self):
        previousTone = self.currentTone - 1
        if previousTone < 0:
            previousTone = len(self.songs[self.currentSong][0]) - 1
        return self.songs[self.currentSong][0][previousTone]

    def getFullStatus(self):
        return [self.getCurrentSong(), 
                    self.getNextSong(), 
                    self.getPreviousSong(),
                    self.currentSong,
                    len(self.songs), 
                    self.getCurrentTone(),
                    self.getNextTone(),
                    self.getPreviousTone(),
                    self.currentTone,
                    len(self.songs[self.currentSong][0])
                ]

    def setNextSong(self):
        self.forceCommandChange = [True, True]
        self.currentSong = self.currentSong + 1
        if self.currentSong >= len(self.songs):
            self.currentSong = 0
        self.currentTone = 0
        self.sendUpdateCommand()
    
    def setPreviousSong(self):
        self.forceCommandChange = [True, True]
        self.currentSong = self.currentSong - 1
        if self.currentSong < 0:
            self.currentSong = len(self.songs) - 1
        self.currentTone = 0
        self.sendUpdateCommand()
    
    def setNextTone(self):
        ctone = self.getCurrentTone()
        ntone = self.getNextTone()
        self.forceCommandChange = [ctone[0] != ntone[0], ctone[:5] != ntone[:5]]
        self.currentTone = (self.currentTone + 1) % len(self.songs[self.currentSong][0])
        self.sendUpdateCommand()
        
    def setPreviousTone(self):
        ctone = self.getCurrentTone()
        ptone = self.getPreviousTone()
        self.forceCommandChange = [ctone[0] != ptone[0], ctone[:5] != ptone[:5]]
        self.currentTone = self.currentTone - 1
        if self.currentTone < 0:
            self.currentTone = len(self.songs[self.currentSong][0]) - 1
        self.sendUpdateCommand()

    def resetState(self):
        self.currentSong = 0
        self.currentTone = 0
        self.forceCommandChange = [True, True]
        self.sendUpdateCommand()

    def setSong(self, song):
        if song < len(self.songs):
            self.currentSong = song
            self.currentTone = 0
            self.forceCommandChange = [True, True]
            self.sendUpdateCommand()

    def sendUpdateCommand(self):
        tone = self.getCurrentTone()
        CP = tone[0]

        if self.forceCommandChange[0]:
            if CP == 'C':
                aplaymidi('midi-files/COMBI.MID')
            elif CP == 'P':
                aplaymidi('midi-files/PROGRAM.MID')

        if self.forceCommandChange[1]:        
            bank = {'A': 0, 'B': 1, 'C': 2, 'D': 3, 'E': 4, 'F': 5}[tone[1]]
            changeBankTone(bank, int(tone[2:5]))
        
        if len(tone) > 5:
            modifiers = tone[5:]
            for i, char in enumerate(modifiers):
                if char == 'P':
                    managePM(i+1, 127)
                elif char == 'M':
                    managePM(i+1, 0)

    def on_closing(self):
        self.running = False

    def input_loop(self):
        while(self.running):
            if alsaseq.inputpending():
                ev = alsaseq.input()
                evtype = ev[0]
                evdata = ev[7]
                if evtype == 10 and evdata[4] == 82 and evdata[5] == 127:
                    self.getNextTone()
                    self.requestSystemUpdate()
                elif evtype == 10 and evdata[4] >= 26 and evdata[4] <= 29:
                    managePM(evdata[4]-25, evdata[5])
                # elif evtype == 12:
                #     print(ev)

