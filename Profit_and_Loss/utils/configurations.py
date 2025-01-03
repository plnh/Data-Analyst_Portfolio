import configparser

def loadConfig(filename='config.ini'):
    ''' 
    Creates a dictionary per section in a given .ini file (default = 'config.ini')
    '''
    config = configparser.ConfigParser()
    config.read(filename)
    if config.read(filename) == []:
        raise ValueError(f'{filename} does not exist.')
    config_dict = {}
    for section in config.sections():
        config_dict[section] = dict(config.items(section))
    return config_dict