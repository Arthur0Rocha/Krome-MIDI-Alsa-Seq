class KeyboardManager:

    def __init__(self, commands):
        self.running = True

        self.nextSong = commands[0]
        self.previousSong = commands[1]
        self.resetSong = commands[2]
        self.setSong = commands[3]

    def on_close(self):
        self.running = False

    def run(self):
        while self.running:
            inp = input() #waits to get input + Return
   
            if inp == 'n':
                self.nextSong()
            elif inp == 'p':
                self.previousSong()
            elif inp == 'r':
                self.resetSong()
            elif inp.isdigit():
                self.setSong(int(inp) - 1)
            elif inp == 'exit':
                self.on_close()

    def update(self, status):
        currentSong = status[0]
        songIndex = status[3]
        totalSongs = status[4]
        tone = status[5]
        toneIndex = status[8]
        print(f'\t{(toneIndex + 1):02d} - {tone} | {currentSong} ({songIndex+1} / {totalSongs})')