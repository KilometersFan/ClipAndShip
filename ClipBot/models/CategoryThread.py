import twitch
import threading
import queue
import time
import datetime
from datetime import timedelta
import models.Category as Category
class CategoryThread(threading.Thread):
    """Thread that executes clip creation code for a single category"""
    def __init__(self, category: Category.Category):
        threading.Thread.__init__(self)
        self._messageQueue = queue.Queue()
        self._category = category
        self.finished = False
        return

    # add comment to queue
    def addToQueue(self, message):
        self._messageQueue.put(message)

    # remove oldest comment from queue
    def popFromQueue(self):
        return self._messageQueue.get()
    
    # run analysis
    def run(self):
        startTime = None
        endTime = None
        prevStart = None
        prevEnd = None
        confidence = 100
        emoteCount = 0
        totalCount = 0
        prevStrippedTime = None
        while True:
            comment = self._messageQueue.get()
            # Non comment means cancel processing
            if not comment:
                self.finished = True
                break
            # parse comment creation time
            try:
                decimalIndex = comment.created_at.index(".")
            except ValueError as e:
                decimalIndex = -1
            strippedTime = comment.created_at[:decimalIndex]
            #see if emotes are present
            if any(self._category.checkIfEmoteExists(word) for word in comment.message.body.split()):
                #start the range
                if not startTime:
                    startTime = datetime.datetime.fromisoformat(strippedTime)
                    endTime = startTime
                    confidence = 100
                #continue changing the range
                else:
                    endTime = datetime.datetime.fromisoformat(strippedTime)
                    prevTime = datetime.datetime.fromisoformat(prevStrippedTime)
                    tdelta = endTime - prevTime
                    if(tdelta.seconds >= 30):
                        confidence = -1
                    else:
                        if confidence + 10 > 100:
                            confidence = 100
                        else:
                            confidence += 10
                emoteCount += 1
            else:
                #if we are working on a range, change confidence otherwise do nothing
                if startTime :
                    confidence = confidence // 2
            # if enough comments don't have any emotes in teh category AND over half of the comments read DID have an emote in this category mark timestamps
            if confidence == 0 and startTime is not None and (emoteCount/(totalCount*1.0) >= 0.50): 
                tdelta = endTime - startTime
                # subtract time from start depending on length
                if tdelta.total_seconds() > 0:
                    if(tdelta.total_seconds() < 30):
                        startTime = startTime + timedelta(seconds=-10)
                    elif(tdelta.total_seconds() < 60):
                        startTime = startTime + timedelta(seconds=-15)
                    else:
                        startTime = startTime + timedelta(seconds=-20)
                    if prevStart and prevEnd and (startTime <= prevStart or startTime <= prevEnd or endTime + timedelta(seconds=-10) <= prevEnd):
                        startTime = min(prevStart, startTime)
                        endTime = max(prevEnd, endTime)
                        if prevStart == startTime:
                            self._category._timestamps.pop()
                    self._category.addTimestamp((startTime, endTime))
                    prevStart = startTime
                    prevEnd = endTime
            prevStrippedTime = strippedTime
            totalCount += 1
            # reset confidence and other values
            if confidence <= 0:
                confidence = -1
                startTime = None
                endTime = None
                emoteCount = 0
                totalCount = 0
                prevStrippedTime = None





