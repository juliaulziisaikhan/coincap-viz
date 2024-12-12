import yaml

def load_config(config_file='config.yaml'):
    return yaml.safe_load(config_file)