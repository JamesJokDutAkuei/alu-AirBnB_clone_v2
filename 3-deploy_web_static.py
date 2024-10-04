#!/usr/bin/python3
from fabric.api import env, local, put, run
from datetime import datetime
import os

# Define the web servers' IP addresses
env.hosts = ['54.234.59.93', '34.224.89.36']


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


def do_deploy(archive_path):
    """
    Distributes an archive to the web servers and deploys it.

    Args:
    archive_path (str): The path to the archive file.

    Returns:
    bool: True if all operations were successful, False otherwise.
    """
    if not os.path.exists(archive_path):
        return False

    try:
        # Get the archive file name (web_static_YYYYMMDDHHMMSS.tgz)
        archive_file = archive_path.split("/")[-1]

        # Extract the file name without the extension
        archive_no_ext = archive_file.split(".")[0]

        # Define the remote path where the archive will be uploaded
        remote_path = "/tmp/{}".format(archive_file)

        # Upload the archive to the /tmp/ directory of the web server
        put(archive_path, remote_path)

        # Create the directory where the archive will be uncompressed
        release_path = "/data/web_static/releases/{}".format(archive_no_ext)
        run("mkdir -p {}".format(release_path))

        # Uncompress the archive to the release folder
        run("tar -xzf /tmp/{} -C {}".format(archive_file, release_path))

        # Remove the uploaded archive from the web server
        run("rm /tmp/{}".format(archive_file))

        # Move the contents from the web_static folder to the release path
        run("mv {}/web_static/* {}/".format(release_path, release_path))

        # Remove the now-empty web_static folder
        run("rm -rf {}/web_static".format(release_path))

        # Delete the existing symbolic link
        run("rm -rf /data/web_static/current")

        # Create a new symbolic link to the new release
        run("ln -s {} /data/web_static/current".format(release_path))

        print("New version deployed successfully!")
        return True

    except Exception as e:
        print("Deployment failed: {}".format(e))
        return False


def deploy():
    """
    Creates and distributes an archive to the web servers.
    Returns the result of the deployment.
    """
    # Call do_pack() to create the archive
    archive_path = do_pack()

    # If no archive was created, return False
    if archive_path is None:
        return False

    # Call do_deploy() to deploy the archive
    return do_deploy(archive_path)
