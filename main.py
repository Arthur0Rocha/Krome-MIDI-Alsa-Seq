import sys

from manager import SongManager
from GUI import Application
from CLI import KeyboardManager
from threadslib import GeneralThread

from songs import casamento_20220409 as musicas1, theWall_minimal as musicas2, generals

def main(cable = False, set2=False):
    manager = SongManager(songs=musicas2 if set2 else musicas1, stdToneList=generals['tones'], cable = cable)

    CLI = KeyboardManager(commands=manager.getCLICommands())
    GUI = Application(commands=manager.getGUICommands(), closing_callbacks=[CLI.on_close])

    manager.initializeCallbacks([GUI.update, CLI.update])
    
    GeneralThread(name='main-thread', run_func=manager.run) # mainThread
    GeneralThread(name='keyboard-thread', run_func=CLI.run) # keyboardThread
    GUI.mainloop()

    CLI.on_close()
    manager.on_closing()
    
if __name__ == "__main__":
    cable = 'cable' in sys.argv
    set2 = '2' in sys.argv
    main(cable, set2)