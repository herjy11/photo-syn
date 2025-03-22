import datetime as dt
import warnings
warnings.filterwarnings('ignore')

import numpy as np

from memories.auto_album import AutoAlbum
from memories.connection import get_connection

if __name__ == '__main__':
    connection = get_connection()
    try:
        album = AutoAlbum('remy',
                          connection,
                          album_name="Sedona aujourd`hui",
                          shared=True,
                          commit=True,
                          )

        album.update_album(start=dt.datetime.now().timestamp() - 24 * 3600,
                           stop=dt.datetime.now().timestamp(),
                           limit = 100,
                           in_album = 4,
                           commit = True)

    except Exception as e:
        connection.rollback()
        print(f"Album creation failed with error: {e}")