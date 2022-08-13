import alsaseq
import os

# TODO add SEQ MODE capabilities

def aplaymidi(filename, delay=0):
    os.system(f'aplaymidi -p KROME -d {delay} {filename}')

def aconnect(dev1, dev2, disconnect=False):
    os.system(f'aconnect {"-d" if disconnect else ""} {dev1} {dev2}')

def makeConnections( cable = False):
    if not cable:
        aconnect("\"Vortex Wireless 2\"", "KROME")
    else:
        aconnect("\"Vortex Wireless 2\"", "KROME", disconnect=True)
    aconnect("\"Vortex Wireless 2\"", "Arthur SEQ")
    aconnect("KROME", "Arthur SEQ")
    aconnect("\"Arthur SEQ\":1", "KROME")
    aconnect("SINCO", "SINCO-KROME-REMAP")
    aconnect("\"SINCO-KROME-REMAP\":1", "Arthur SEQ")

def midiSysEx(sysEx):
        message = [sysEx[0], len(sysEx) - 1] + sysEx[1:]
        header = [
                0x4d, 0x54, 0x68, 0x64,
                0x00, 0x00, 0x00, 0x06,
                0x00, 0x00, 
                0x00, 0x01,
                0x03, 0xc0
        ]
        content = [0x00] + message
        ending = [
                0x00, 0xff, 0x2f, 0x00
        ]
        track = [
                0x4d, 0x54, 0x72, 0x6b,
                0x00, 0x00, 0x00, len(content) + 4
        ]
        return bytes(header + track + content + ending)

def initMIDIFolder():
    if not os.path.isdir('midi-files'):
        os.mkdir('midi-files')
        print('Created midi-files folder.')
    for val, CP in [(0x00, 'COMBI'), (0x02, 'PROGRAM')]:
        filename = f'midi-files/{CP}.MID'
        if not os.path.isfile(filename):
            command = [0xF0, 0x42, 0x30, 0x00, 0x01, 0x15, 0x4E, val, 0xF7]
            f = open(filename, 'wb')
            f.write(midiSysEx(command))
            f.close()
            print(f'Created {CP} midi command.')
    for i in range(4):
        for val in [1, 127]:
            filename = f'midi-files/MIDI.{i+1}.{val}.MID'
            if not os.path.isfile(filename):
                command = [0xF0, 0x42, 0x30, 0x00, 0x01, 0x15, 0x41, 0x00, 0x00, 0x0C + i, 0x00, 0x35, 0x00, 0x00, 0x00, 0x00, val, 0xF7]
                f = open(filename, 'wb')
                f.write(midiSysEx(command))
                f.close()
                print(f'Created {filename}.')
   

def createMIDIfile(filename, bank=0, tone=0):
    strout =  b'MThd\x00\x00\x00\x06\x00\x00\x00\x01\x03\xc0MTrk\x00\x00\x00\x0f\x00\xb0\x00\x00\x00\xb0\x20'  \
            + bytes([bank]) + b'\x00\xc0' \
            + bytes([tone]) + b'\x00\xff\x2f\x00'

    f = open(filename, 'wb')
    f.write(strout)
    f.close()
    print(f'Created {filename}.')

def changeBankTone(bank, tone):
    fname = f"midi-files/{['A','B','C','D','E','F'][bank]}{tone:03d}.MID"
    if not os.path.isfile(fname):
        createMIDIfile(fname, bank, tone)
    aplaymidi(fname)

def handlePMstate(pmStr, delay=0):
    if delay > 0:
        aplaymidi('midi-files/MIDI.1.127.MID', delay)
    for i, c in enumerate(pmStr):
        if c == 'P':
            sendPM(i+1, 127)
        elif c == 'M':
            sendPM(i+1, 0)

def sendPM(channel, value):
    aplaymidi(f'midi-files/MIDI.{channel}.{127 if value > 0 else 1}.MID')

class ManagerStatus:
    def __init__(self, songs, stdToneList, requestSystemUpdate, cable = False):
        self.songs = songs
        self.generals = stdToneList

        initMIDIFolder()

        alsaseq.client('Arthur SEQ', 1, 1, False)

        makeConnections(cable)
        
        self.requestSystemUpdate = requestSystemUpdate

        self.running = True

        self.resetState()
        
    def getCurrentSong(self):
        return self.songs[self.currentSong]['name']

    def getNextSong(self):
        index = self.currentSong + 1
        if index >= len(self.songs):
            index = 0
        return self.songs[index]['name']
    
    def getPreviousSong(self):
        index = self.currentSong - 1
        if index < 0:
            index = len(self.songs) - 1
        return self.songs[index]['name']

    def getCurrentTone(self): #TODO Test it better
        return self.getTonesList()[self.currentTone]

    def getNextTone(self):
        nextTone = self.currentTone + 1
        if nextTone >= len(self.getTonesList()):
            nextTone = 0
        return self.getTonesList()[nextTone]

    def getPreviousTone(self):
        previousTone = self.currentTone - 1
        if previousTone < 0:
            previousTone = len(self.getTonesList()) - 1
        return self.getTonesList()[previousTone]

    def getTonesList(self): #TODO Test it better
        originalTones = self.songs[self.currentSong]['tones']
        return originalTones + list(filter(lambda tone: tone not in originalTones, self.generals))[len(originalTones):]

    def getSongPD(self):
        pd = '-Y'
        if 'pd' in self.songs[self.currentSong]:
            pd = self.songs[self.currentSong]['pd']
            if type(pd) == type(list()):
                pd = pd[self.currentTone]
        return {'': -1, '+Y': 1, '-Y': 2, 'VOL': 7, 'SW': 82}[pd]

    def getSongAT(self):
        at = '+Y'
        if 'at' in self.songs[self.currentSong]:
            at = self.songs[self.currentSong]['at']
            if type(at) == type(list()):
                at = at[self.currentTone]
        return {'': -1, '+Y': 1, '-Y': 2, 'VOL': 7}[at]

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
                    self.getTonesList(),
                    self.getPedal(),
                    self.getAT()
                ]

    def resetState(self):
        self.currentSong = 0
        self.currentTone = 0
        self.clearSettings()
        self.sendUpdateCommand()

    def clearSettings(self):
        self.auxStorage = 'XXXXX'
        self.pdswTriggered = False
        self.updatePdAt()

    def updatePdAt(self):
        self.pedalCC = self.getSongPD()
        self.ATCC = self.getSongAT()

    def setSong(self, song):
        if song < len(self.songs):
            self.currentSong = song
            self.currentTone = 0
            self.clearSettings()
            self.sendUpdateCommand()

    def setNextSong(self):
        self.currentSong = self.currentSong + 1
        if self.currentSong >= len(self.songs):
            self.currentSong = 0
        self.currentTone = 0
        self.clearSettings()
        self.sendUpdateCommand()
    
    def setPreviousSong(self):
        self.currentSong = self.currentSong - 1
        if self.currentSong < 0:
            self.currentSong = len(self.songs) - 1
        self.currentTone = 0
        self.clearSettings()
        self.sendUpdateCommand()
    
    def setNextTone(self):
        ctone = self.getCurrentTone()
        ntone = self.getNextTone()
        sendCPCommand = ctone[0] != ntone[0]
        sendToneCommand = ctone[:5] != ntone[:5] and ntone[:5] != self.auxStorage[:5]
        if sendCPCommand:
            self.auxStorage = ctone
        self.currentTone = (self.currentTone + 1) % len(self.getTonesList())
        self.updatePdAt()
        self.sendUpdateCommand(sendCPCommand, sendToneCommand)
        
    def setPreviousTone(self):
        ctone = self.getCurrentTone()
        ptone = self.getPreviousTone()
        sendCPCommand = ctone[0] != ptone[0]
        sendToneCommand = ctone[:5] != ptone[:5] and ptone[:5] != self.auxStorage[:5]
        if sendCPCommand:
            self.auxStorage = ctone
        self.currentTone = self.currentTone - 1
        if self.currentTone < 0:
            self.currentTone = len(self.getTonesList()) - 1
        self.updatePdAt()
        self.sendUpdateCommand(sendCPCommand, sendToneCommand)

    def setTone(self, n): #TODO test modification
        # if n >= len(self.getTonesList()):
        if n > 3:
            return
        ctone = self.getCurrentTone()
        self.currentTone = n
        ntone = self.getCurrentTone()
        if ctone == ntone:
            sendCPCommand, sendToneCommand = [True, True]
            self.auxStorage = 'XXXXX'
        else:
            sendCPCommand = ctone[0] != ntone[0]
            sendToneCommand = ctone[:5] != ntone[:5] and ntone[:5] != self.auxStorage[:5]
            if sendCPCommand:
                self.auxStorage = ctone
        self.updatePdAt()
        self.sendUpdateCommand(sendCPCommand, sendToneCommand)

    def handleSW(self):
        self.setNextTone()
        self.requestSystemUpdate()

    def handlePedal(self, val, src, dest):
        if self.pedalCC < 0:
            return
        if self.pedalCC == 82:
            if self.pdswTriggered and val > 80:
                self.pdswTriggered = False
                self.handleSW()
            elif not self.pdswTriggered and val < 40:
                self.pdswTriggered = True
            return
        alsaseq.output( (10, 0, 0, 253, (0,0), src, dest, (0, 0, 0, 0, self.pedalCC, val)) )

    def handleAT(self, val, src, dest):
        if self.ATCC < 0:
            return
        alsaseq.output( (10, 0, 0, 253, (0,0), src, dest, (0, 0, 0, 0, self.ATCC, val)) )

    def handleCCSetTone(self, channel):
        self.setTone(channel)
        self.requestSystemUpdate()

    def togglePedal(self):
        if self.pedalCC == -1:
            self.pedalCC = 1
        elif self.pedalCC == 1:
            self.pedalCC = 2
        elif self.pedalCC == 2:
            self.pedalCC = 7
        elif self.pedalCC == 7:
            self.pedalCC = 82
        elif self.pedalCC == 82:
            self.pedalCC = -1

    def toggleAT(self):
        if self.ATCC == -1:
            self.ATCC = 1
        elif self.ATCC == 1:
            self.ATCC = 2
        elif self.ATCC == 2:
            self.ATCC = 7
        elif self.ATCC == 7:
            self.ATCC = -1

    def getPedal(self):
        if self.pedalCC == -1:
            return ''
        elif self.pedalCC == 1:
            return '+Y'
        elif self.pedalCC == 2:
            return '-Y'
        elif self.pedalCC == 7:
            return 'VOL'
        elif self.pedalCC == 82:
            return 'SW'

    def getAT(self):
        if self.ATCC == -1:
            return ''
        elif self.ATCC == 1:
            return '+Y'
        elif self.ATCC == 2:
            return '-Y'
        elif self.ATCC == 7:
            return 'VOL'

    def sendUpdateCommand(self, sendCPCommand=True, sendToneCommand=True):
        tone = self.getCurrentTone()
        toneCP = tone[0]
        toneBank = tone[1]
        toneNumber = tone[2:5]

        if sendCPCommand:
            if toneCP == 'C':
                aplaymidi('midi-files/COMBI.MID')
            elif toneCP == 'P':
                aplaymidi('midi-files/PROGRAM.MID')

        if sendToneCommand:        
            bank = {'A': 0, 'B': 1, 'C': 2, 'D': 3, 'E': 4, 'F': 5}[toneBank]
            changeBankTone(bank, int(toneNumber))
        
        if len(tone) > 5:
            modifiersPM = tone[5:]
            delay = 1 if sendCPCommand or sendToneCommand else 0
            handlePMstate(modifiersPM, delay)
            
    def on_closing(self):
        self.running = False

    def input_loop(self):
        while(self.running):
            if alsaseq.inputpending():
                ev = alsaseq.input()
                evtype = ev[0]
                evdata = ev[7]
                if evtype == 10 and evdata[4] == 82 and evdata[5] == 127:
                    self.handleSW()
                elif evtype == 10 and evdata[4] >= 26 and evdata[4] <= 29 and evdata[5] == 127:
                    self.handleCCSetTone(evdata[4]-26)
                elif evtype == 10 and evdata[4] == 4:
                    self.handlePedal(ev[7][5], ev[6], ev[5])
                elif evtype == 12:
                    self.handleAT(ev[7][5], ev[6], ev[5])

