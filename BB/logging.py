from .bbConfig import bbConfig
import os.path
from os import path
from datetime import datetime

class logger:
    def __init__(self):
        self.logs = {"usersDB":"", "guildsDB":"", "bountiesDB":"",
                        "shop":"", "escapedBounties": "", "bountyConfig": "", "duels": "",
                        "hangar": "", "misc": "", "bountyBoards": ""}


    def save(self):
        logsSaved = ""
        files = {}
        nowStr = datetime.utcnow().strftime("(%d/%m/%H:%M)")

        for category in self.logs:
            if self.logs[category] != "":
                currentFName = bbConfig.loggingFolderPath + ("" if bbConfig.loggingFolderPath.endswith("/") else "/") + category + ".txt"
                logsSaved += category + ".txt"

                if category not in files:
                    if not path.exists(currentFName):
                        try:
                            f = open(currentFName, 'x')
                            f.write('')
                            f.close()
                            logsSaved += "[+]"
                        except IOError as e:
                            print(nowStr + "-[LOG::SAVE]>F_NEW_IOERR: ERROR CREATING LOG FILE: " + currentFName + "\n" + str(e))
                    try:
                        files[category] = open(currentFName, 'a')
                    except IOError as e:
                        print(nowStr + "-[LOG::SAVE]>F_OPN_IOERR: ERROR OPENING LOG FILE: " + currentFName + "\n" + str(e))
                        files[category] = None

                if files[category] is not None:
                    try:
                        files[category].write(self.logs[category])
                        logsSaved += ", "
                    except IOError as e:
                        print(nowStr + "-[LOG::SAVE]>F_WRT_IOERR: ERROR WRITING TO LOG FILE: " + currentFName + "\n" + str(e))
        
        for f in files.values():
            f.close()
        if logsSaved != "":
            print(nowStr + "-[LOG::SAVE]>SAVE_DONE: Logs saved: " + logsSaved[:-2])


    def log(self, classStr, funcStr, event, category="misc", eventType="MISC_ERR"):
        if category not in self.logs:
            self.log("misc", "Log", "log", "ATTEMPTED TO LOG TO AN UNKNOWN CATEGORY '" + str(category) + "' -> Redirected to misc.", eventType="UNKWN_CTGR")
        eventStr = datetime.utcnow().strftime("(%d/%m/%H:%M)") + "-[" + str(classStr).upper() + "::" + str(funcStr).upper() + "]>" + str(eventType) + ": " + str(event)
        print(eventStr)
        self.logs[category] += eventStr + "\n\n"


bbLogger = logger()