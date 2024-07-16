import keyboard
import asyncio

awaitTime = 0.05

async def pressNRelease(pair:tuple,binding):

    if tuple[0] != tuple[1]:
        if type(binding) == str:
            keyboard.press(binding)
            asyncio.sleep(awaitTime)
            keyboard.release(binding)
        if type(binding) == list:
            for key in binding:
                keyboard.press(key)
            asyncio.sleep(awaitTime)
            for key in binding:
                keyboard.release(key)

def allSelectedKeys(config:dict):

    allKeys:set = {"shift"}

    for key in config.keys():
        binding = config[key]["binding"]
        if type(binding) == str:
            allKeys.add(binding)
        if type(binding) == dict:
            for dict_key in binding.keys():
                if type(binding[dict_key]) == str:
                    allKeys.add(binding[dict_key])
                if type(binding[dict_key]) == list:
                    for key_ in binding[dict_key]:
                        allKeys.add(key_)
        if type(binding) == list:
            for key_ in binding:
                allKeys.add(key_)

    with open("emergency.txt","w") as file:
        for item in allKeys:
            file.write(item + '\n')


def emergencyShutdown():

    with open('emergency.txt', 'r') as f:
        for line in f:
            key = line.strip()
            print(key)
            keyboard.release(key)

    