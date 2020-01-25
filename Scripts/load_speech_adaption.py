def load_speech_adaption():
    with open("speech_adaption_entities.txt", "r") as spch_ents:
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
