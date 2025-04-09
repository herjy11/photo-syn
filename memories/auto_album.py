import psycopg2
import datetime as dt

import numpy as np
import pandas.io.sql as sqlio

from memories.utils import get_users

class AutoAlbum:
    def __init__(self,
                 user:str,
                 connection: psycopg2.extensions.connection,
                 album_name: str,
                 shared: bool=False,
                 sharables: list[str] | None=None,
                 commit=False,
                 ):
        """
        Creates new albums for a user in a database connected with psycopg2

        Parameters
        ----------
        user: str
            SYnology username
        connection: psycopg2
            Postgres connection
        album_name: str
            Name of the album
        shared: str
            "'true'" for shared albums
        sharables: list
            List of people to share the album with
        """
        self.people = []
        self.user_name = user
        self.album_name = album_name
        self.shared = shared
        self.shared_str = str(shared).lower()
        if shared:
            self.sharables = sharables
            if sharables is None:
               self.sharables = get_users(connection)
        # Postgres connection with psycopg2
        self.connection = connection
        self.cursor = connection.cursor()
        # Matching user_id to name
        self.user_id = int(sqlio.read_sql_query(f"SELECT id FROM public.user_info WHERE name = '{self.user_name}'",
                                         self.connection).values[0][0])
        assert isinstance(self.user_id, int), f"user_id should be int instead found {type(self.user_id)}"

        # Check if album already exists
        possible_id = sqlio.read_sql_query(f"SELECT album_id FROM public.auto_album "
                                                 f"WHERE album_name = '{self.album_name}'"
                                                 f" AND user_id = {str(self.user_id)}"
                                                 f" AND shared = '{self.shared_str}';",
                                                 self.connection)['album_id'].values
        try:
            if len(possible_id) > 0:

                # Getting id of  already existing album
                self.album_id = possible_id

                # There cannot be more than one auto album with the same name.
                if self.album_id.size > 1:
                    raise AssertionError(f"Multiple albums found ({self.album_id.size})"
                                     f"please make sure only one album exists with name {self.album_name}")
                self.album_id = self.album_id[0]

                # Album already exists
                print(f"Album {self.album_name} already exists. Not creating new album.")
            else:

                # Album does not exist and needs to be created
                self._create_empty_album()

                if commit:
                    self.connection.commit()

        except Exception as e:
            self.connection.rollback()
            print(f"Album creation failed with error: {e}")


    def _create_empty_album(self,
                            commit: bool=False):
        """
        Creates an empty album.

        Parameters
        ----------
        album_name: str
            Name of the album
        shared: str
            "'true'" for shared albums
        """

        normal_album_fields = ['id_user',
                               'name',
                               'normalized_name',
                               'passphrase_share',
                               'type',
                               'shared',
                               'create_time',
                               'cover',
                               'sort_by',
                               'sort_direction']

        fields = ''.join(field + ', ' for field in normal_album_fields)[:-2]


        try:
            if self.shared:
                pass_phrase = f"'{self.album_name.upper()}_{self.user_name}_pass'"
                self.cursor.execute(f"INSERT INTO public.share (passphrase, privacy_type, modified_time,"
                                    f" id_user, expired_time, hashed_password, enable, type)"
                                    f" VALUES ({pass_phrase}, 0, {int(dt.datetime.now().timestamp())},"
                                    f" '{self.user_id}', 0, '', 'true', 0) ;")
            else:
                pass_phrase = 'NULL'

            values = (self.user_id,
                      f"'{self.album_name}'",
                      f"'{self.album_name.upper()}'",
                      f"{pass_phrase}",
                      '0',  # type
                      self.shared_str,  # shared
                      str(int(dt.datetime.now().timestamp())),  # create_time
                      '0',
                      '0',
                      '0')
            values = ''.join(str(value) + ', ' for value in values)[:-2]

            # Creates a new album
            self.cursor.execute(f"INSERT INTO public.normal_album ({fields}) VALUES ({values});")
            self.album_id = sqlio.read_sql_query(f"SELECT id FROM public.normal_album"
                                                 f" WHERE name = '{self.album_name}'"
                                                 f" AND id_user = {str(self.user_id)}"
                                                 f" AND shared = '{self.shared_str}';",
                                            self.connection).values[0][0]
            # Adds the album to the table of automatically created albums
            self.cursor.execute(f"INSERT INTO public.auto_album "
                                 f"(album_id, user_id, album_name, epoch_created, epoch_last_modified ,shared)"
                                 f"VALUES ({self.album_id}, {self.user_id}, '{self.album_name}', "
                                 f"{int(dt.datetime.now().timestamp())}, {int(dt.datetime.now().timestamp())}, {self.shared_str});")

            if self.shared:
                self._share_album(pass_phrase)

            if commit:
                self.connection.commit()
        except Exception as e:
            self.connection.rollback()
            print(f"Album creation failed with error: {e}")



    def update_album(self,
                     start: str,
                     stop: str,
                     limit=15,
                     people: list[str] | None=None,
                     in_album: int | None=None,
                     commit: bool=False):
        """
        Updates an album with new photos

        Parameters
        ----------
        start: datetime
            Start time of the album
        stop: datetime
            Stop time of the album
        people: list
            List of people in the photos to pick
        in_album: int
            Draw from a specific album
        commit: bool
            Commit the changes
        """
        album_condition = ''
        if in_album is not None:

            album_condition = f"AND id IN (SELECT id_item FROM public.many_item_has_many_normal_album "\
                              f" WHERE id_normal_album = {in_album}) "

        people_condition = ''
        if people is not None:

            id_units = [f"(SELECT id_unit FROM public.many_unit_has_many_person "
                        f"WHERE id_person IN "
                        f"(SELECT id FROM public.person WHERE name = '{p}')) " for p in people]
            ids = f"{''.join(idd + ' INTERSECT ' for idd in id_units)}"[:-12]

            people_condition = f"AND id IN ({ids})"

        sql = f"INSERT INTO public.many_item_has_many_normal_album "\
               f"(sequence, item_provider_id_user, id_item, id_normal_album, album_id_user) "\
               f"SELECT 0, {str(self.user_id)}, id_item, {str(self.album_id)}, {str(self.user_id)} FROM unit "\
               f"WHERE takentime BETWEEN {start} AND {stop} {album_condition} {people_condition} ORDER BY RANDOM() LIMIT {limit};"

        try:
            # Delete existing photos from the album
            self.cursor.execute(
                f"DELETE FROM public.many_item_has_many_normal_album WHERE id_normal_album = {self.album_id};")
            self.cursor.execute(sql)


            self.cursor.execute(f"UPDATE public.auto_album "\
                                f"SET epoch_last_modified = {int(dt.datetime.now().timestamp())} "\
                                f"WHERE album_id = {self.album_id} AND user_id = {self.user_id} "
                                f"AND album_name = '{self.album_name}';")

            self._update_album_stats()

            if commit:
                self.connection.commit()

        except Exception as e:
            self.connection.rollback()
            print(f"Album creation failed with error: {e}")

    def _share_album(self,
                    pass_phrase: str):
        """
        Shares an album with multiple users
        """
        try:


            for user in self.sharables:
                user_id = sqlio.read_sql_query(f"SELECT id FROM public.user_info WHERE name = '{user}'",
                                         self.connection).values[0][0]

                self.cursor.execute(f"INSERT INTO public.share_permission "
                                    f" (id_user, permission, target_type, target_id, passphrase_share) "
                                    f" VALUES ('{self.user_id}', 1, 1, {user_id}, {pass_phrase});")
        except Exception as e:
            self.connection.rollback()
            print(f"Album sharing failed with error: {e}")

        pass

    def _update_album_stats(self):
        """
        Updates the album stats to enable display of thumbnails.
        """
        cover_id = sqlio.read_sql_query(f"SELECT a.id_item FROM public.many_item_has_many_normal_album a "
                                        f"INNER JOIN unit u ON u.id_item = a.id_item "
                                        f"WHERE a.id_normal_album = {self.album_id} "                                            
                                        f"ORDER BY u.takentime DESC LIMIT 1;",
                                        self.connection).values[0][0]

        self.cursor.execute(f"DO $$ BEGIN "
                            f" PERFORM public.update_normal_album_cover_func('public', {self.album_id}, {cover_id});"
                            f" END $$;")
        self.cursor.execute(f"DO $$ BEGIN "
                            f"PERFORM public.insert_item_to_update_normal_album_func({self.album_id});" 
                            f"END $$;")

        pass

