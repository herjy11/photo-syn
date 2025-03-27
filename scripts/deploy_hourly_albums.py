import datetime as dt
import warnings
import sys
warnings.filterwarnings('ignore')

from memories.auto_album import AutoAlbum
from memories.connection import get_connection

if __name__ == '__main__':
    connection = get_connection(ip=sys.argv[1], port=sys.argv[2])
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