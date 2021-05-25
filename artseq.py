import alsaseq
import os

import threading

running = True

class KeyboardThread(threading.Thread):

    def __init__(self, input_cbk = None, name='keyboard-input-thread'):
        self.input_cbk = input_cbk
        super(KeyboardThread, self).__init__(name=name)
        self.start()

    def run(self):
        global running
        while running:
            self.input_cbk(input()) #waits to get input + Return

def my_callback(inp):
    global currentSong
    global running
    global forcing
    if inp == 'n':
        toNextSong()
    elif inp == 'p':
        toPreviousSong()
    elif inp == 'r':
        toResetSong()
    elif inp.isdigit():
        setSong(int(inp) - 1)
    elif inp == 'force':
        forcing = not forcing
    elif inp == 'exit':
        running = False
         


def changeBankTone(bank, tone):
    
    banks = ['A','B','C','D','E','F']
    bankname = banks[bank]
    
    fname = f'midi-files/{bankname}{tone:03d}.MID'

    if not os.path.isfile(fname):

        strout =  b'MThd\x00\x00\x00\x06\x00\x00\x00\x01\x03\xc0MTrk\x00\x00\x00\x0f\x00\xb0\x00\x00\x00\xb0\x20'  \
                + bytes([bank]) + b'\x00\xc0' \
                + bytes([tone]) + b'\x00\xff\x2f\x00'

        f = open(fname, 'wb')
        f.write(strout)

    os.system(f'aplaymidi -p KROME -d 0 {fname}')

# FOOT SWITCH -> CC 82

# Note on 6
# Note off 7
# CC 10
# Aftertouch 12
# Program change: 10 -> 10 -> 11

songs = [
    (['CD001PM', 'PF001'], 'Bring me to life'), # 1
    (['CD021'], 'Going Under'), # 2
    (['PF001', 'CD029'], 'Tourniquet'), # 3
    (['PF001', 'CD001'], 'Imaginary'), # 4
    (['CD001PM'], 'My immortal'), # 5
    (['CD001PM', 'PF001'], 'Lithium'), # 6
    (['PF000', 'PF001'], 'Broken'), # 7 
    (['CD001', 'PF001'], 'Taking over me'), # 8 
    (['PF001', 'PF012'], 'What you want'), # 9
    # (['PF002', 'PF001', 'PF002', 'PF001', 'PF002', 'PF003', 'PF001'], 'Call me'), # 10
    (['CD002PMM', 'CD002MPM', 'CD002PMM', 'CD002MPM', 'CD002PMM', 'CD002MMP', 'CD002MPM'], 'Call me'), # 10
    (['CD029'], 'Everybody\'s fool'), # 11
    (['CD018'], 'Final Countdown'), # 12
    (['CD027'], 'Dont wanna miss'), # 13
    (['PF001', 'CD000'], 'Nothing else matters'), # 14
    (['PF007'], 'Separate ways'), # 15
    (['PD057', 'PF000'], 'Love aint no stranger'), # 16
    (['CD020', 'PD084'], 'its my life'), # 17
    (['CD025'], 'Maniac'), # 18
    (['CD031'], 'Everybody want to rule'), # 19
    (['CD019'], 'Enjoy the silence'), # 20
    (['PF012'], 'Radio gaga'), # 21
    (['CD028', 'PA020'], 'Numb'), # 22
    (['PD057', 'PF000'], 'The evil that men do'), # 23
    (['PB011', 'CD016', 'CD017'], 'Mr Crowley') # 24
]

currentSong = 0
currentTone = -1

lastCOMBI = 'XXXX'
lastPROGR = 'XXXX'
currentCP = 'X'

forcing = False # TODO implement that

def setTone():
    global currentSong
    global currentTone
    global songs
    global lastPROGR
    global lastCOMBI
    global currentCP

    tone = songs[currentSong][0][currentTone]
    if tone[0] == 'C' and currentCP[0] != 'C':
        os.system('aplaymidi -p KROME -d 0 midi-files/COMBI.MID')
    elif tone[0] == 'P' and currentCP[0] != 'P':
        os.system('aplaymidi -p KROME -d 0 midi-files/PROGRAM.MID')
    
    currentCP = tone[0]
    
    if tone[0] == 'C' and lastCOMBI == tone[1:5]:
        pass
    elif tone[0] == 'P' and lastPROGR == tone[1:5]:
        pass
    else:
        bank = {'A': 0, 'B': 1, 'C': 2, 'D': 3, 'E': 4, 'F': 5}[tone[1]]
        changeBankTone(bank, int(tone[2:5]))
        if tone[0] == 'C':
            lastCOMBI = tone[1:5]
        elif tone[0] == 'P':
            lastPROGR = tone[1:5]
        

    if len(tone) > 5:
        modifiers = tone[5:]
        for i, char in enumerate(modifiers):
            if char == 'P':
                managePM(i+1, 127)
            elif char == 'M':
                managePM(i+1, 0)

    print(f'\t{(currentSong + 1):02d} - {tone} | {songs[currentSong][1]} ({currentTone+1} / {len(songs[currentSong][0])})')

def setSong(song):
    global currentTone
    global currentSong
    global songs
    global lastCOMBI
    global lastPROGR
    global currentCP

    if song < 0:
        currentSong = len(songs) - 1
    elif song >= len(songs):
        currentSong = 0
    else:
        currentSong = song
    currentTone = 0
    lastPROGR = 'XXXX'
    lastCOMBI = 'XXXX'
    currentCP = 'X'
    setTone()

def toNextProgram():
    global currentSong
    global currentTone
    currentTone += 1
    if currentTone >= len(songs[currentSong][0]):
        currentTone = 0
    setTone()

def toNextSong():
    global currentSong
    setSong(currentSong + 1)

def toPreviousSong():
    global currentSong
    setSong(currentSong - 1)

def toResetSong():
    setSong(0)

def managePM(channel, value):
    os.system(f'aplaymidi -p KROME -d 0 midi-files/MIDI.{channel}.{127 if value > 0 else 1}.MID')

def init():
    kthread = KeyboardThread(my_callback)

    alsaseq.client('Arthur SEQ', 1, 1, False)

    os.system('aconnect \"Vortex Wireless 2\" KROME')
    os.system('aconnect \"Vortex Wireless 2\" \"Arthur SEQ\"')
    os.system('aconnect KROME \"Arthur SEQ\"')
    os.system('aconnect \"Arthur SEQ\":1 KROME')

    print ('Running...\n')
    

def loop():
    global running
    while(running):
        if alsaseq.inputpending():
            ev = alsaseq.input()
            evtype = ev[0]
            evdata = ev[7]
            if evtype == 10 and evdata[4] == 82 and evdata[5] == 127:
                toNextProgram()
            elif evtype == 10 and evdata[4] >= 26 and evdata[4] <= 29:
                managePM(evdata[4]-25, evdata[5])
            # elif evtype == 12:
            #     print(ev)
                
if __name__ == '__main__':
    init()
    loop()







# set to PROG ->    F0 42 30 00 01 15 4E 02 F7
# set to COMBI ->   F0 42 30 00 01 15 4E 00 F7
# MIDI 0C 7F ->     F0 42 30 00 01 15 41 00 00 0C 00 35 00 00 00 00 7F F7
# Mute 1 ->         F0 42 30 00 01 15 41 00 00 0C 00 28 00 00 00 00 01 F7
# Play 1 ->         F0 42 30 00 01 15 41 00 00 0C 00 28 00 00 00 00 00 F7
# Volume 1 127 ->   F0 42 30 00 01 15 41 00 00 0C 00 02 00 00 00 00 7F F7


# MIDI File STD:    4D54 6864
#                   0000 0006
#                   0000
#                   0001
#                   03C0 (ppqn)
# 
#                   4d54 726b
#                   XXXX XXXX (length)
# 
#                   NNZZ ZZZZ (N = time, Z = command)
#                   if sysex: NNF0 ZZ XX...XX F7 (N = time, Z = # of bytes, X = command)
# 
#                   00FF 2F00