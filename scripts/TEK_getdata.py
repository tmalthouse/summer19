import visa
import numpy as np
from matplotlib import pyplot as plt
import datetime
from settings import *
import array

# visa.log_to_screen()

plt.style.use('seaborn-dark')


def printquery(scope,q):
    print("{}: {}".format(q,scope.query(q)))

def convert_data(rawdata):
    return np.array([x if x <= 127 else x-256 for x in map(ord,rawdata)])

def sample_channel(scope,channel):
    scope.write("DAT:SOU CH{}".format(channel))
    ymult = scope.query('WFMP:YMU?')
    return convert_data(scope.query_binary_values("CURV?", datatype='c')), ymult

def save_data(scope,data, name=None):
    param = scope.query("WFMP?")
    if name == None:
        name = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    print("Saved as 'data/{}.npy".format(name))
    np.save(DATA_DIR / "mach_zehnder" / "{}.npy".format(name), data)
    

def take_measurement(scope,name = None):
    data = np.array([sample_channel(scope,1),sample_channel(scope,2)])
    save_data(data, name)

def capturedata():
    rm = visa.ResourceManager()

    print("Connecting to scope...")
    resources = rm.list_resources()
    scope = None
    for res in resources:
        if SCOPE_ID in res:
            scope = rm.open_resource(res)
    if scope is None:
        print("Could not find scope---is it on and plugged in?")
        raise FileNotFoundError
        
    print("Connected!")
    scope.timeout = 10000

    print("Setting transfer params...")
    scope.write('DAT:WID 1')
    scope.write("DAT:ENC RIB")

    scope.write("DAT:SOU CH1")
    print("Set!")


    print("Taking data...")
    ch1,ch1mult = sample_channel(scope,1)
    ch2,ch2mult = sample_channel(scope,2)
    print("Data collected!")
    scope.close()

    return (ch1,ch2),{
        'Ch1Mult': ch1mult,
        'Ch2Mult': ch2mult
    }