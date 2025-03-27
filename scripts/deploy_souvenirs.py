import datetime as dt
import warnings
import sys
warnings.filterwarnings('ignore')

import numpy as np

from memories.auto_album import AutoAlbum
from memories.connection import get_connection

if __name__ == '__main__':
    connection = get_connection(ip=sys.argv[1], port=sys.argv[2])
    try:
        album = AutoAlbum('remy',
                          connection,
                          album_name="Souvenirs",
                          shared=True,
                          commit=True,
                          )

        album.update_album(start=1673826537,
                           stop=dt.datetime.now().timestamp(),
                           limit = 15 + int(np.random.rand(1) * 5),
                           in_album = 4,
                           commit = True)

    except Exception as e:
        connection.rollback()
        print(f"Album creation failed with error: {e}")