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

        cellWidth = 9
        
        self.master.title("Tone Manager")

        Style().configure("TButton", padding=(0, 10, 0, 10),
            font='serif 15')

        self.columnconfigure(0, pad=3)
        self.columnconfigure(1, pad=3)
        self.columnconfigure(2, pad=3)
        self.columnconfigure(3, pad=3)
        
        self.rowconfigure(0, pad=3)
        self.rowconfigure(1, pad=3)
        self.rowconfigure(2, pad=3)

        prevSong, nextSong, toggleAT, togglePed, nextTone, set1, set2, set3, set4 = commands
        
        bps = Button(self, text="<<<", command=prevSong, width=cellWidth)
        bps.grid(row=0, column=0)
        self.songTitle = Button(self, text="Nome da Música", width=2*cellWidth, command=nextTone)
        self.songTitle.grid(row=0, column=1, columnspan=2, sticky=W+E)
        bns = Button(self, text=">>>", command=nextSong, width=cellWidth)
        bns.grid(row=0, column=3)
        
        self.bat = Button(self, text="ATC", command=toggleAT, width=cellWidth)
        self.bat.grid(row=1, column=0)
        self.toneCode = Button(self, text="Código do Timbre", command=nextTone)
        self.toneCode.grid(row=1, column=1, columnspan=2, sticky=W+E)
        self.bpe = Button(self, text="PED", command=togglePed, width=cellWidth)
        self.bpe.grid(row=1, column=3)
        
        self.bt = [None, None, None, None]

        self.bt[0] = Button(self, text="-", command=set1, width=cellWidth)
        self.bt[0].grid(row=2, column=0)
        self.bt[1] = Button(self, text="-", command=set2, width=cellWidth)
        self.bt[1].grid(row=2, column=1)
        self.bt[2] = Button(self, text="-", command=set3, width=cellWidth)
        self.bt[2].grid(row=2, column=2)
        self.bt[3] = Button(self, text="-", command=set4, width=cellWidth)
        self.bt[3].grid(row=2, column=3)
        
        self.pack()
       
    def update(self, status):

        currentSong = status[0]
        songIndex = status[3]
        totalSongs = status[4]
        tone = status[5]
        toneIndex = status[8]
        tonesList = status[9]
        totalTones = len(tonesList)
        ped = status[10]
        at = status[11]

        self.songTitle['text'] = f'{currentSong} {songIndex+1}/{totalSongs}'
        self.toneCode['text'] = f'{toneIndex+1}/{totalTones} - {tone}'

        for bt in self.bt:
            bt.configure(text='\n-\n')

        for i, code in enumerate(tonesList):
            self.bt[i].configure(text=f'{"*******" if i == toneIndex else ""}\n{code}\n{"*******" if i == toneIndex else ""}')

        self.bat.configure(text=f'AT{at}')
        self.bpe.configure(text=f'PD{ped}')

    def on_closing(self):
        for cbk in self.closing_callbacks:
            cbk()
        self.master.destroy()

