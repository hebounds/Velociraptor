import yaml

try:
    with open('users.yml', 'r+') as file_object:
        data = file_object.read()
        print(data)
except:
    print('Velociraptor - Error occurred when reading User Data file')

yaml.load(data)