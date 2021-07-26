
# ------------------------------------ Back-end ---------------------------------------


import alsaseq
import os


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

def managePM(channel, value):
    os.system(f'aplaymidi -p KROME -d 0 midi-files/MIDI.{channel}.{127 if value > 0 else 1}.MID')


class SongManager:
    def __init__(self):

        alsaseq.client('Arthur SEQ', 1, 1, False)

        os.system('aconnect \"Vortex Wireless 2\" KROME')
        os.system('aconnect \"Vortex Wireless 2\" \"Arthur SEQ\"')
        os.system('aconnect KROME \"Arthur SEQ\"')
        os.system('aconnect \"Arthur SEQ\":1 KROME')

        self.songs = [
            (['PF000', 'CD029'], 'Memórias - Pitty'),
            (['PF000', 'PF003'], 'Déjà Vu - Pitty'),
            (['CD029'], 'Semana que vem - Pitty'),
            (['PF000'], 'Pulsos - Pitty'),
            (['PF000'], 'Anacrônico - Pitty'),
            (['CD001PM'], 'Na sua estante - Pitty'),
            (['PF000'], 'Me adora - Pitty'),
            (['PF004', 'PF003'], 'Eu quero sempre mais - Ira ft. Pitty'),
            (['PF000'], 'I Wanna Be - Pitty'),
            (['PF001', 'CD029'], 'Heaven and Hell - Black Sabbath'),
            (['PF001'], 'Toxicity - SOAD'),
            (['CD001PM'], 'Zombie - The Cranberries'),
            (['CD024', 'PA092'], 'Mama, I\'m Coming Home - Ozzy Osbourne'),
            (['CD022'], 'Perfect Strangers - Deep Purple')
        ]

        self.currentSong = 0
        self.currentTone = -1

        self.lastCOMBI = 'XXXX'
        self.lastPROGR = 'XXXX'
        self.currentCP = 'X'

        self.callback = None
        self.running = True
        self.thread = MidiReaderThread(songManager=self)
        print ('Running...\n')

    def setTone(self):
        
        tone = self.songs[self.currentSong][0][self.currentTone]
        if tone[0] == 'C' and self.currentCP[0] != 'C':
            os.system('aplaymidi -p KROME -d 0 midi-files/COMBI.MID')
        elif tone[0] == 'P' and self.currentCP[0] != 'P':
            os.system('aplaymidi -p KROME -d 0 midi-files/PROGRAM.MID')
        
        self.currentCP = tone[0]
        
        if tone[0] == 'C' and self.lastCOMBI == tone[1:5]:
            pass
        elif tone[0] == 'P' and self.lastPROGR == tone[1:5]:
            pass
        else:
            bank = {'A': 0, 'B': 1, 'C': 2, 'D': 3, 'E': 4, 'F': 5}[tone[1]]
            changeBankTone(bank, int(tone[2:5]))
            if tone[0] == 'C':
                self.lastCOMBI = tone[1:5]
            elif tone[0] == 'P':
                self.lastPROGR = tone[1:5]
            

        if len(tone) > 5:
            modifiers = tone[5:]
            for i, char in enumerate(modifiers):
                if char == 'P':
                    managePM(i+1, 127)
                elif char == 'M':
                    managePM(i+1, 0)

        print(f'\t{(self.currentSong + 1):02d} - {tone} | {self.songs[self.currentSong][1]} ({self.currentTone+1} / {len(self.songs[self.currentSong][0])})')

        if self.callback is not None:
            self.callback()

    def setSong(self, song):

        if song < 0:
            self.currentSong = len(self.songs) - 1
        elif song >= len(self.songs):
            self.currentSong = 0
        else:
            self.currentSong = song
        self.currentTone = 0
        self.lastPROGR = 'XXXX'
        self.lastCOMBI = 'XXXX'
        self.currentCP = 'X'
        self.setTone()

    def toNextProgram(self):
        self.currentTone += 1
        if self.currentTone >= len(self.songs[self.currentSong][0]):
            self.currentTone = 0
        self.setTone()

    def toPreviousProgram(self):
        self.currentTone -= 1
        if self.currentTone < 0:
            self.currentTone = len(self.songs[self.currentSong][0]) - 1
        self.setTone()

    def toNextSong(self):
        self.setSong(self.currentSong + 1)

    def toPreviousSong(self):
        self.setSong(self.currentSong - 1)

    def toResetSong(self):
        self.setSong(0)

    def get_current_song(self):
        return self.songs[self.currentSong]


                
# ------------------------------------ Thread ---------------------------------------

import threading

class MidiReaderThread(threading.Thread):

    def __init__(self, input_cbk = None, name='input-thread', songManager=None):
        self.input_cbk = input_cbk
        super(MidiReaderThread, self).__init__(name=name)
        self.manager = songManager
        self.start()

    def run(self):
        while(self.manager.running):
            if alsaseq.inputpending():
                ev = alsaseq.input()
                evtype = ev[0]
                evdata = ev[7]
                if evtype == 10 and evdata[4] == 82 and evdata[5] == 127:
                    self.manager.toNextProgram()
                elif evtype == 10 and evdata[4] >= 26 and evdata[4] <= 29:
                    managePM(evdata[4]-25, evdata[5])
                # elif evtype == 12:
                #     print(ev)



# ------------------------------------ View ---------------------------------------

import tkinter as tk
from tkinter import W, E
from tkinter.ttk import Button, Style

class Application(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        
        self.manager = SongManager()
        self.manager.callback = self.update
        
        self.create_widgets()
        self.update()

    def create_widgets(self):

        self.master.title("Tone Manager")

        Style().configure("TButton", padding=(0, 10, 0, 10),
            font='serif 10')

        self.columnconfigure(0, pad=3)
        self.columnconfigure(1, pad=3)
        self.columnconfigure(2, pad=3)
        
        self.rowconfigure(0, pad=3)
        self.rowconfigure(1, pad=3)
        
        bps = Button(self, text="Música Anterior", command=self.manager.toPreviousSong)
        bps.grid(row=0, column=0)
        self.songTitle = Button(self, text="Nome da Música")
        self.songTitle.grid(row=0, column=1)
        bns = Button(self, text="Próxima Música", command=self.manager.toNextSong)
        bns.grid(row=0, column=2)
        
        bpt = Button(self, text="Timbre Anterior", command=self.manager.toPreviousProgram)
        bpt.grid(row=1, column=0)
        self.toneCode = Button(self, text="Código do Timbre")
        self.toneCode.grid(row=1, column=1)
        bnt = Button(self, text="Próximo Timbre", command=self.manager.toNextProgram)
        bnt.grid(row=1, column=2)

        self.pack()

        # self.f1 = tk.Frame(self)
        # self.butt_ant = self.create_button(text = 'Música Anterior', command = self.manager.toPreviousSong, side = 'top')
        # self.butt_ptone = self.create_button(text = 'Timbre Anterior', command = self.manager.toPreviousProgram, side = 'bottom')
        # self.f1.pack(side='left')
        
        # self.f2 = tk.Frame(self)
        # self.butt_mus = self.create_button(text = '', command = None, side = 'top')
        # self.butt_tone = self.create_button(text = '', command = None, side = 'bottom')
        # self.f2.pack('right')
        
        # self.f3 = tk.Frame(self)
        # self.butt_pro = self.create_button(text = 'Próxima Música', command = self.manager.toNextSong, side = 'top')
        # self.butt_ntone = self.create_button(text = 'Próximo Timbre', command = self.manager.toNextProgram, side = 'bottom')
        # self.f3.pack('right')
        
    def update(self):
        song = self.manager.get_current_song()
        cind = max(self.manager.currentTone, 0)
        self.songTitle['text'] = song[1]
        self.toneCode['text'] = f'{cind+1}/{len(song[0])} - {song[0][cind]}'
        # self.butt_mus['text'] = song[1]
        # self.butt_tone['text'] = f'{cind+1}/{len(song[0])} - {song[0][cind]}'


    # def create_button(self, text='', command=None, side='right'):
    #     butt = tk.Button(self)
    #     butt["text"] = text
    #     if command is not None:
    #         butt["command"] = command
    #     butt.pack(side=side)
        
    #     return butt

        
root = tk.Tk()
app = Application(master=root)
app.mainloop()
