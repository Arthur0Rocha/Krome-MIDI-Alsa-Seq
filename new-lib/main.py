from manager import SongManager
from GUI import Application
from CLI import KeyboardManager
from threadslib import GeneralThread

from songs import ensaio

def main():
    manager = SongManager(songs=ensaio)

    commandsCLI = [manager.nextSong, manager.previousSong, manager.reset, manager.setSong]
    CLI = KeyboardManager(commands=commandsCLI)
    commandsGUI = [manager.previousSong, manager.nextSong, manager.previousTone, manager.nextTone]
    closingGUI = [CLI.on_close]
    GUI = Application(commands=commandsGUI, closing_callbacks=closingGUI)

    manager.assignCallback(GUI.update)
    manager.assignCallback(CLI.update)
    manager.runCallbacks()

    mainThread = GeneralThread(name='main-thread', run_func=manager.run)
    keyboardThread = GeneralThread(name='keyboard-thread', run_func=CLI.run)
    GUI.mainloop()
    CLI.on_close()
    manager.on_closing()
    
if __name__ == "__main__":
    main()