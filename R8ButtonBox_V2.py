from GraphicsSpy_V2 import GraphicsSpy
from PhysicsSpy import PhysicsSpy
from actionFunctions import *
import serial.tools.list_ports
import asyncio
import json

# configfiles for objects to retrieve sharedMemory info.
physicsConfig = "./configFiles/physics.json"
graphicsConfig = "./configFiles/graphics.json"
keysBindingConfig = "./configFiles/buttonBoxConfig.json"

# parameters needed to retrieve (could be configured at future by Human request)
graphicsParameters = ["packetId","TCCUT","EngineMap","rainLights","lightsStage","wiperLV"]
physicsParameters = ["tcActive","absActive","ignitionOn",]

# hardconfig buttonBox name
device_name = "Arduino Micro"

def loadKeysConfig(file:str) -> dict:

    with open(file,'r') as config:
        return json.load(config)

def stablishCommunication(baudRate=115200,timeOut=1) -> serial.Serial:
    """
        Function to stablish serial comunication with available devices.
        would search for description or ask for port by console.
    """

    ports = serial.tools.list_ports.comports()

    for port in ports:
        if device_name.lower() in port.description.lower():
            selectedPort = port.device

    print(f"device {device_name} found at PORT: {port.device}")
    serialInstance = serial.Serial(port=selectedPort, baudrate=baudRate, timeout=timeOut)
    try:
        serialInstance.open()
    except Exception as e:
        print(e)
    finally:
        return serialInstance

async def retrieveGraphics() -> dict:
    # declare global variables in scope
    global graphicSpy,graphicsParameters

    # retrieve data from graphics sheet of memory
    rawData = graphicSpy.spy()
    if (rawData["packetId"] == 0): # check whether game has started
        return {"packetId":0}
    data = dict([(key,rawData[key]) for key in graphicsParameters])
    return data


async def retrievePhysics():
    # declare global variables in scope
    global physicsSpy,physicsParameters
    rawData = physicsSpy.spy()
    data = dict([(key,rawData[key]) for key in physicsParameters])
    return data

async def receivePackage() -> dict:

    global serialInstance
    serialInstance.write(" ".encode('utf-8'))
    await asyncio.sleep(0.01)
    if serialInstance.in_waiting:
        jsonPackage = serialInstance.readline()
        return json.loads(jsonPackage)
    return {}

async def resolveInputs(inputs:dict,gameData:dict):

    pass

async def main():
    """
        Main function to excecute with two goals:
            1) Retrieve live information from sharedMemory
            2) receive ButtonBox status to be processed
    """
    try:
        packageTask = asyncio.create_task(receivePackage())
        graphicsTask = asyncio.create_task(retrieveGraphics())
        physicsTask = asyncio.create_task(retrievePhysics())
    
        graphicsData = await graphicsTask
        physicsData = await physicsTask
        inputs:dict = await packageTask

        if graphicsData["packetId"] == 0:
            print("Race has not started") # increase delay if game has not started to avoid memory access collision
            asyncio.sleep(3)
        else:
            del graphicsData["packetId"]
            gameData = {**graphicsData,**physicsData}
            print("ButtonBox")
            print(inputs)
            await resolveInputs(inputs=inputs,gameData=gameData)

                        

    except Exception as e:
            print("An error has ocurred: ", e)
            emergencyShutdown()

        

if __name__ == "__main__":

    graphicSpy = GraphicsSpy(graphicsConfig)
    physicsSpy = PhysicsSpy(physicsConfig)
    keyConfig = loadKeysConfig(keysBindingConfig)
    try:
        emergencyShutdown() #cleans any remaining keys pressed in any case something went wrong
    except:
        allSelectedKeys(keyConfig)
        allSelectedKeys(keyConfig)   
    serialInstance = stablishCommunication() 
    while True:
        asyncio.run(main())