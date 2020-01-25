import os
import json

from Utils.OS_Find import Path_OS_Assist

def load_speech_adaption():
    delim = Path_OS_Assist()

    with open(os.getcwd() + "%sUtils%sPATH.json" % (delim, \
        delim), "r") as path_json:
        REPO_PATH = json.load(path_json)["PATH"]

    JSON_PATH = REPO_PATH + "%sData%sWakeWord%sMFCC%s" % \
            (delim, delim, delim, delim)

    with open(os.getcwd() + "%sUtils%sData%sspeech_adaption_entities.txt" % \
            (delim, delim, delim), "r") as spch_ents:
        ents = [x.replace('\n', '') for x in spch_ents.readlines()]
    
    new_name = ""
    for i in range(len(ents)):
        
        if i % 2 == 1:
            new_name += ents[i]
            ents.append(new_name)
            new_name = ""
        
        else:
            new_name += (ents[i] + " ")

    print(ents)

if __name__ == "__main__":
    load_speech_adaption()
