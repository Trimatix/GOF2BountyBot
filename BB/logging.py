from .bbConfig import bbConfig
import os.path
from os import path
from datetime import datetime
import datetime

class logger:
    def __init__(self):
        self.clearLogs()


    def clearLogs(self):
        self.logs = {"usersDB":{}, "guildsDB":{}, "bountiesDB":{},
                        "shop":{}, "escapedBounties": {}, "bountyConfig": {}, "duels": {},
                        "hangar": {}, "misc": {}, "bountyBoards": {}}


    def isEmpty(self):
        for cat in self.logs:
            if bool(self.logs[cat]):
                return False
        return True


    def peekHeadTimeAndCategory(self):
        head, headCat = None, ""
        for cat in self.logs:
            if bool(self.logs[cat]):
                currHead = list(self.logs[cat].keys())[0]
                if head is None or currHead < head:
                    head, headCat = currHead, cat

        return head, headCat


    def popHeadLogAndCategory(self):
        head, headCat = self.peekHeadTimeAndCategory()

        if head is None:
            log = ""
        else:
            log = self.logs[headCat][head]
            del self.logs[headCat][head]

        return log, headCat


    def save(self):
        if self.isEmpty():
            return

        logsSaved = ""
        files = {}
        nowStr = datetime.utcnow().strftime("(%d/%m/%H:%M)")
        
        for category in self.logs:
            if bool(self.logs[category]):
                currentFName = bbConfig.loggingFolderPath + ("" if bbConfig.loggingFolderPath.endswith("/") else "/") + category + ".txt"
                logsSaved += category + ".txt, "

                if category not in files:
                    if not path.exists(currentFName):
                        try:
                            f = open(currentFName, 'x')
                            f.write('')
                            f.close()
                            logsSaved += "[+]"
                        except IOError as e:
                            print(nowStr + "-[LOG::SAVE]>F_NEW_IOERR: ERROR CREATING LOG FILE: " + currentFName + ":" + e.__name__, trace=traceback.format_exc())
                    try:
                        files[category] = open(currentFName, 'a')
                    except IOError as e:
                        print(nowStr + "-[LOG::SAVE]>F_OPN_IOERR: ERROR OPENING LOG FILE: " + currentFName + ":" + e.__name__, trace=traceback.format_exc())
                        files[category] = None

        while not self.isEmpty():
            log, category = self.popHeadLogAndCategory()
            if files[category] is not None:
                try:
                    files[category].write(log)
                except IOError as e:
                    print(nowStr + "-[LOG::SAVE]>F_WRT_IOERR: ERROR WRITING TO LOG FILE: " + currentFName + ":" + e.__name__, trace=traceback.format_exc())
        
        for f in files.values():
            f.close()
        if logsSaved != "":
            print(nowStr + "-[LOG::SAVE]>SAVE_DONE: Logs saved: " + logsSaved[:-2])
        
        self.clearLogs()


    def log(self, classStr, funcStr, event, category="misc", eventType="MISC_ERR", trace=""):
        if category not in self.logs:
            self.log("misc", "Log", "log", "ATTEMPTED TO LOG TO AN UNKNOWN CATEGORY '" + str(category) + "' -> Redirected to misc.", eventType="UNKWN_CTGR")

        now = datetime.utcnow()
        eventStr = now.strftime("(%d/%m/%H:%M)") + "-[" + str(classStr).upper() + "::" + str(funcStr).upper() + "]>" + str(eventType) + ": " + str(event)
        print(eventStr)
        self.logs[category][now] = eventStr + ("\n" + trace if trace != "" else "") + "\n\n"


bbLogger = logger()