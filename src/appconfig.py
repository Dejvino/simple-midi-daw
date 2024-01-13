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
