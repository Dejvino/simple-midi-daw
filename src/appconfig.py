import configparser

def load_common():
    print("Loading common app config...")
    configFiles = ['config.ini']
    config = configparser.ConfigParser()
    # TODO: find config from a priority list of locations
    result = config.read(configFiles)
    # TODO: verify the result matches what we requested
    print("Config loaded.")
    return config

def load_keyboards():
    print("Loading keyboards config...")
    configFiles = ['keyboard.ini']
    config = configparser.ConfigParser()
    # TODO: find config from a priority list of locations
    # TODO: read multiple separate config files (one per keyboard) into one config
    result = config.read(configFiles)
    # TODO: verify the result matches what we requested
    print("Configs loaded.")
    return config
