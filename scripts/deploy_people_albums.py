import datetime as dt
import warnings
import sys
warnings.filterwarnings('ignore')

import numpy as np

from memories.utils import get_users, get_people
from memories.auto_album import AutoAlbum
from memories.connection import get_connection

if __name__ == '__main__':

    connection = get_connection(ip=sys.argv[1], port=sys.argv[2])
    users = get_users(connection)
    people = get_people(connection)

    connection.close()
    for user in users:
        connection = get_connection(ip=sys.argv[1], port=sys.argv[2])
        try:
            person = people[[p.lower() == user.lower() for p in people]][0]
            album = AutoAlbum(user,
                              connection,
                              album_name="Sedona et Moi",
                              shared=False,
                              commit=True,
                              )

            album.update_album(start=0,
                               stop=dt.datetime.now().timestamp(),
                               limit = 10 + int(np.random.rand(1) * 5),
                               in_album = 4,
                               people = ('Sedona', person),
                               commit=True)
        except Exception as e:
            print(e)
        connection.close()