import configparser


config = configparser.ConfigParser()
config.read("../fastapi_websocket/development.ini")

# print(config.get("db","port"))