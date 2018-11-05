"""IMLS Workset Downloader.

Usage:
    workset_downloader.py <username> <password> (--ids | --file) <input>
    workset_downloader.py -h

Options:
  -h --help     Show this screen.

Description:
    This authorizes against the data api and downloads the given data.
    username: username of the DC system.
    password: your password for the DC system.
    input: set of data ID's separated by commas or file containing the workset ids in separate lines
Example:
    python workset_downloader.py admin admin "123,2232"

"""
import requests
from base64 import b64encode
from docopt import docopt
from os import mkdir
from os.path import exists, join

#DATA_API_URL = "http://localhost:5000"
DATA_API_URL = "http://156.56.176.81:5000"
TOKEN_FILE_NAME = "api.token"
DATA_FOLDER = "data"


def download_workset(username, password, id_list):
    # Create the data folder if it does not exist
    if not exists(DATA_FOLDER):
        mkdir(DATA_FOLDER)

    if not authorize_user(username, password):
        return
    else:
        for public_id in id_list:
            download_data(public_id)


def download_data(public_id):
    url = DATA_API_URL + "/download/" + public_id
    headers = {"x-access-token": read_token_from_file()}
    request = requests.get(url, allow_redirects=True, headers=headers)
    if request.status_code == 200:
        open(join(DATA_FOLDER,public_id), 'wb').write(request.content)
        print("Downloaded: " + public_id)
    else:
        print("Error occurred getting the file: " + public_id)
        print("message: " + request.json()["message"])


def authorize_user(username, password):
    auth = b64encode(bytes(username + ':' + password, "utf-8")).decode("ascii")
    headers = {'Authorization': 'Basic %s' % auth}
    login_request = requests.get(DATA_API_URL+"/login", headers=headers)
    if login_request.status_code == 200:
        response = login_request.json()
        write_token_to_file(response["token"])
        return True
    else:
        print("Error occurred authorizing. Please check the username and password")
        print("message from server: " + login_request.text)
        return False


def write_token_to_file(token):
    with open(TOKEN_FILE_NAME, 'w') as file:
        file.write(token + '\n')


def read_token_from_file():
    with open(TOKEN_FILE_NAME) as file:
        token = file.readline().rstrip()
    return token


def main():
    """
    Main function for the IMLS Workset Downloader.

    """
    arguments = docopt(__doc__, version='IMLS Workset Downloader 1.0')
    if arguments["--ids"]:
        download_workset(arguments["<username>"], arguments["<password>"], arguments["<input>"].split(","))
    elif arguments["--file"]:
        ids = []
        with open(arguments["<input>"]) as file:
            for line in file:
                ids.append(line.strip())
        download_workset(arguments["<username>"], arguments["<password>"], ids)


if __name__ == "__main__":
    main()
