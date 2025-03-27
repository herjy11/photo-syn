# Synology Memories

This package helps synnology users to create custom albums programmatically. 
Using psycopg2, we access the synnofoto database to directly program new albums for users, set their sharing rights 
and update their content.

The aim is that the functionality emulates google photos' `memories` feature. For instance I use the package to create 
an album for each user that contains photos of them with a loved one (requires `faces` with some labeling to be enabled)
or photos of their past year. I then use synology's task scheduler to automatically update the albums 
on a daily/weekly/... basis.

## Disclaimer

This package was designed for use with a synnology NAS that supports synology photos, however, t
his package is **not** affiliated with or endorsed by Synology.

## Recommended reading and inspiration

I don't think I could have done that without the following resources in particular:
* [postgres script to manipulate the database](https://community.synology.com/enu/forum/1/post/148949)
* [Guidelines for remote connection to the database](https://community.synology.com/enu/forum/1/post/148949)

## Usage

The code mainly consists in a class `AutoAlbum` that allows to create albums, 
set their sharing rights and update their content. 

For instance the following snippet creates a shared album named "Souvenirs" owned by user 
`user1` and shared by default with all users in the database. Keyword `sharable` can be used to restrict the sharing 
to a subset of users.

```
from memories.auto_album import AutoAlbum
from memories.connection import get_connection

conection = get_connection()
album = AutoAlbum('user1',
                  connection,
                  album_name="Souvenirs",
                  shared=True,
                  commit=True,
                  )
```

If the album already exists (based on its name, owner and sharing rights) nothing happens, otherwise it will be created.
    
The following snippet updates the album and adds between 10 and 15 photos from album number `4` 
(id needs to be checked in the database) where `user1` and `user2` are present.
The commit keyword allows to commit the changes to the database.
```
album.update_album(start=0,
                   stop=dt.datetime.now().timestamp(),
                   limit = 10 + int(np.random.rand(1) * 5),
                   in_album = 4,
                   people = ('Sedona', person),
                   commit=True)
```

## Automation

To automate the update of the albums, you can use synology's task scheduler to run a python script every day/week/month/...
In a python script (e.g. souvenirs.py) write the above script and save it. 

in `Control Panel -> Task Scheduler -> Create -> Scheduled Task -> User-defined Script`:
Use the schedule tab to define the schedule (e.g. every day at 10am). In the `Task Setting` run the script: 

```
#!/bin/sh

python /path/to/scripts/souvenirs.py 
```
Note that this solution uses the native python environment of your synology, which only supports python 3.8.15
(at least for my model). At the moment, only release [v1](https://github.com/herjy11/photo-syn/releases/tag/v1-DS224%2B)
supports python 3.8.15.

To use other versions of python, I suggest running a container by following the instructions below.

## Containerization

For generality and also to enable use of more recent python versions, I recommend using a docker container to run the 
code. To do so, I've made helper script that you can use to build and run the containers.

My currennt solution is probably not ideal, but it works: I create a docker image for each album-generating script 
I want to run. They can be found in the Dockerfile and each image simply runs the corresponding python script. 
From there, building the images is done by running:

```
bash scripts/build_images.sh souvenirs
bash scripts/build_images.sh people
bash scripts/build_images.sh hourly
```
from within the repository.

Then running the containers via tasks uses the `run_container` script:

```
#!/bin/sh

/var/services/homes/remy/git_repos/photo-syn/scripts/run_container.sh people <ip> <port>

/var/services/homes/remy/git_repos/photo-syn/scripts/run_container.sh souvenirs <ip> <port>
```
where <ip> and <port> are the ip and port of the postgres database on your synology.