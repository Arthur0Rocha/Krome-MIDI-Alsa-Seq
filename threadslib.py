import threading

class GeneralThread(threading.Thread):

    def __init__(self, name='general-thread', run_func=None):
        super(GeneralThread, self).__init__(name=name)
        self.run_func = run_func
        self.start()

    def run(self):
        self.run_func()
