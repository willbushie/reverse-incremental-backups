import time

class Tracker:
    def __init__(self, total):
       self.start = time.time()
       self.end = None
       self.total = total
       self.current = 0
       self.complete = False

    def progressBar(self, current, data=False):
        """
        Print dynamic progress bar.
        @param current - Current completed value.
        @param data - Whether the current param passed is a byte measurement or not.
        """
        self.setCurrent(current)
        elapsedTime = time.time() - self.start
        if (self.current == 0):
            self.setCurrent(1)
        progress = self.current / self.total
        estTotalTime = elapsedTime / progress
        estTimeLeft = estTotalTime - elapsedTime
        if (estTimeLeft > 60):
            timeRemaining = f"Est Remaining: {max(round(estTimeLeft / 60, 1),0)} min"
        else:
            timeRemaining = f"Est Remaining: {max(round(estTimeLeft, 1),0)} sec"
        
        barLength = 30
        filledLength = int(barLength * self.current / self.total)
        bar = ('=' * filledLength) + ' ' * (barLength - filledLength)
        if (self.complete and data == False):
            print(f"[{'=' * 30}] {self.total}/{self.total} (100.0%) {' ' * 25}")
        elif (self.complete and data == True):
            correctUnit = self.getAppropriateUnit(self.total, self.total)
            print(f"[{'=' * 30}] {correctUnit} (100.0%) {' ' * 25}")
        elif (not self.complete and data == False):
            print(f"[{bar}] {self.current}/{self.total} ({round((self.current/self.total) * 100,1)}%) {timeRemaining} {' ' * 25}", end='\r')
        elif (not self.complete and data == True):
            correctUnit = self.getAppropriateUnit(self.current, self.total)
            print(f"[{bar}] {correctUnit} ({round((self.current/self.total) * 100,1)}%) {timeRemaining} {' ' * 25}", end='\r')

    def setCurrent(self, current):
        self.current = current

    def setComplete(self):
        """
        Set Tracker as complete.
        """
        self.end = time.time()
        self.complete = True

    def getAppropriateUnit(self, current, total):
        """
        Using a total, determine the appropriate data unit to use.
        @param current - Current number of bytes.
        @param total - Total number of bytes.
        @return str
        """
        if (total > 1000000000):
            return f"{round(current/1000000000,1)}/{round(total/1000000000,1)} GB"
        elif (total > 1000000):
            return f"{round(current/1000000,1)}/{round(total/1000000,1)} MB"
        elif (total > 1000):
            return f"{round(current/1000,1)}/{round(total/1000,1)} KB"
        else:
            return f"{current}/{total} Bytes"
