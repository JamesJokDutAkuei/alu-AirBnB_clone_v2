#!/usr/bin/python3
from fabric.api import env, put, run
import os

# Define the web servers' IP addresses
env.hosts = ['54.234.59.93', '34.224.89.36']


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
