import tkinter as tk
from tkinter import W, E
from tkinter.ttk import Button, Style


class Application(tk.Frame):
    def __init__(self, commands, closing_callbacks):
        master = tk.Tk()
        super().__init__(master)
        self.master = master

        self.closing_callbacks = closing_callbacks
        
        self.create_widgets(commands)
        self.master.protocol("WM_DELETE_WINDOW", self.on_closing)
        
    def create_widgets(self, commands):

        centralWidth = 20
        lateralWidth = 15
        
        self.master.title("Tone Manager")

        Style().configure("TButton", padding=(0, 10, 0, 10),
            font='serif 15')

        self.columnconfigure(0, pad=3)
        self.columnconfigure(1, pad=3)
        self.columnconfigure(2, pad=3)
        
        self.rowconfigure(0, pad=3)
        self.rowconfigure(1, pad=3)
        self.rowconfigure(2, pad=3)
        
        bps = Button(self, text="Música Anterior", command=commands[0], width=lateralWidth)
        bps.grid(row=0, column=0)
        self.songTitle = Button(self, text="Nome da Música", width=centralWidth)
        self.songTitle.grid(row=0, column=1)
        bns = Button(self, text="Próxima Música", command=commands[1], width=lateralWidth)
        bns.grid(row=0, column=2)
        
        bpt = Button(self, text="Timbre Anterior", command=commands[2], width=lateralWidth)
        bpt.grid(row=1, column=0)
        self.toneCode = Button(self, text="Código do Timbre")
        self.toneCode.grid(row=1, column=1)
        bnt = Button(self, text="Próximo Timbre", command=commands[3], width=lateralWidth)
        bnt.grid(row=1, column=2)

        bat = Button(self, text="AfterTouch", command=None, width=lateralWidth)
        bat.grid(row=2, column=0)
        
        bpe = Button(self, text="Pedal", command=None, width=lateralWidth)
        bpe.grid(row=2, column=2)

        self.pack()
       
    def update(self, status):

        currentSong = status[0]
        songIndex = status[3]
        totalSongs = status[4]
        tone = status[5]
        toneIndex = status[8]
        totalTones = status[9]

        self.songTitle['text'] = f'{currentSong} {songIndex+1}/{totalSongs}'
        self.toneCode['text'] = f'{toneIndex+1}/{totalTones} - {tone}'

    def on_closing(self):
        for cbk in self.closing_callbacks:
            cbk()
        self.master.destroy()

