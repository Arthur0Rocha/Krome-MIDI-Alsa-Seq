import sys

from manager import SongManager
from GUI import Application
from CLI import KeyboardManager
from threadslib import GeneralThread

from songs import theWall_20220318 as musicas, generals

def main(cable = False):
    manager = SongManager(songs=musicas, stdToneList=generals, cable = cable)

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
    main(cable)