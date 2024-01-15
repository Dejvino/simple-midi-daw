import configparser
import threading


local = threading.local()

def load_common():
    if getattr(local, "common_cache", None) != None:
        return local.common_cache
    #print("Loading common app config...")
    configFiles = ['config.ini']
    config = configparser.ConfigParser()
    # TODO: find config from a priority list of locations
    result = config.read(configFiles)
    # TODO: verify the result matches what we requested
    #print("Config loaded.")
    local.common_cache = config
    return config

def load_keyboards():
    if getattr(local, "kbd_cache", None) != None:
        return local.kbd_cache
    #print("Loading keyboards config...")
    configFiles = ['keyboard.ini']
    config = configparser.ConfigParser()
    # TODO: find config from a priority list of locations
    # TODO: read multiple separate config files (one per keyboard) into one config
    result = config.read(configFiles)
    # TODO: verify the result matches what we requested
    #print("Configs loaded.")
    local.kbd_cache = config
    return config


# TODO: cleanup, remove from here:
import mido
from .midi import MidiClient

def find_every_keyboard_port(port_type='midi'):
    keyboardCfg = load_keyboards()
    keyboardClientName = keyboardCfg['description']['client_name']
    keyboardPortName = keyboardCfg['description']['client_port_' + port_type + '_name']
    client = MidiClient("keyboard")
    inPorts = mido.get_input_names()
    for port in inPorts:
        if port.find(keyboardClientName) != -1 and port.find(keyboardPortName) != -1:
            yield port

def find_keyboard_port(port_type='midi'):
    keyboards = list(find_every_keyboard_port(port_type))
    assert len(keyboards) > 0
    return keyboards[0]

def for_every_keyboard(fn, port_type='midi'):
    for port in find_every_keyboard_port(port_type):
        fn(port)
