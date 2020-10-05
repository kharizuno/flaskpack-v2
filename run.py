## Author : Kharizuno
## Github : https://github.com/kharizuno

from systems.config import NeoConfig
from systems.config.http import server, __setup_logging

#: setup logging
__setup_logging()

if __name__ == '__main__':
    server.run(port=NeoConfig.PORT)