import time

class Tracker:
    """
    ## Tracker
    The Tracker class is used to help visualize and track the progress of the
    application while it's running.
    """
    def __init__(self, total: int):
        """
        @type total: int
        @param total: Total number of items to process.
        """
        self.start = time.time()
        self.end = None
        self.total = total
        if self.total == 0:
            self.total = 1
        self.current = 0
        self.complete = False

    def progressBar(self, current: int, data: bool = False) -> None:
        """
        Print a dynamic progress bar to the terminal given the current completed
        value (out of the total).

        @type current: int
        @param current: The current completed position out of the total (5 out of 10 done).
        @type data: bool
        @param data: Whether `current` is a byte measurement or not. 
            (default is False)
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

    def setCurrent(self, current: int) -> None:
        """
        Update (set) the current position of tracking (out of the total).

        @type current: int
        @param current: Current position in total (5 out of 10 done).
        """
        self.current = current

    def setComplete(self) -> None:
        """
        Set the Tracker object as complete.
        """
        self.end = time.time()
        self.complete = True

    def getAppropriateUnit(self, current: int, total: int) -> str:
        """
        Returns a printable string of denoting the completed data status (with
        an appropriate unit measurement).

        @type current: int
        @param current: Number of bytes completed so far.
        @type total: int
        @param total: Total number of bytes to be completed.
        """
        if (total > 1000000000):
            return f"{round(current/1000000000,1)}/{round(total/1000000000,1)} GB"
        elif (total > 1000000):
            return f"{round(current/1000000,1)}/{round(total/1000000,1)} MB"
        elif (total > 1000):
            return f"{round(current/1000,1)}/{round(total/1000,1)} KB"
        else:
            return f"{current}/{total} Bytes"