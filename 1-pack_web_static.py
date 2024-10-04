#!/usr/bin/python3
from fabric.api import local
from datetime import datetime
import os


def do_pack():
    """
    Generates a .tgz archive from the contents of the web_static folder.
    Returns the archive path if the archive was successfully created.
    Otherwise, returns None.
    """
    # Create the versions directory if it doesn't exist
    if not os.path.exists("versions"):
        os.makedirs("versions")

    # Get the current timestamp for the archive name
    now = datetime.now()
    archive_name = "web_static_{}.tgz".format(now.strftime("%Y%m%d%H%M%S"))

    # The full path of the archive to be created
    archive_path = "versions/{}".format(archive_name)

    # Create the archive using tar
    try:
        local("tar -czvf {} web_static".format(archive_path))
        return archive_path
    except Exception as e:
        print("Error during archiving: {}".format(e))
        return None
