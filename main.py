from manager import SongManager
from GUI import Application
from CLI import KeyboardManager
from threadslib import GeneralThread

from songs import refugio

def main():
    manager = SongManager(songs=refugio)

    CLI = KeyboardManager(commands=manager.getCLICommands())
    GUI = Application(commands=manager.getGUICommands(), closing_callbacks=[CLI.on_close])

    manager.initializeCallbacks([GUI.update, CLI.update])
    
    GeneralThread(name='main-thread', run_func=manager.run) # mainThread
    GeneralThread(name='keyboard-thread', run_func=CLI.run) # keyboardThread
    GUI.mainloop()

    CLI.on_close()
    manager.on_closing()
    
if __name__ == "__main__":
    main()