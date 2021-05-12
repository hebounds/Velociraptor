import yaml
import os


def open_yamlfile(fileStr):
    try:
        with open("src/" + fileStr, 'r+') as file_object:
            data = file_object
            data = yaml.load(data, Loader=yaml.FullLoader)
            print(data)
            return data
    except:
        raise Exception('Velociraptor - Error occurred when reading YAML data file')


def add_field(dataFile, key, value):
    pass


def get_field(dataFile, key):
    for item, doc in dataFile.items():
        if item == key:
            return item
    pass


userData = open_yamlfile('users.yml')

print(get_field(userData, 'myface'))
