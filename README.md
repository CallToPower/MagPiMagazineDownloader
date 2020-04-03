# MagPiMagazineDownloader

Downloads issues of the MagPi magazine.

## Prerequisites

* Python 3

## Copyright

2019-2020 Denis Meyer

Magazine by "The Raspberry Pi Foundation" (https://magpi.raspberrypi.org)

## Usage

* Start shell
  * Windows
    * Start shell as administrator
    * `Set-ExecutionPolicy Unrestricted -Force`
* Create a virtual environment
  * `python -m venv venv`
* Activate the virtual environment
  * Mac/Linux
    * `source venv/bin/activate`
  * Windows
    * `.\venv\scripts\activate`
* Install the required libraries
  * `pip install -r requirements.txt`
* Run the app
  * `python MagPiMagazineDownloader.py --start <StartIssue> --end <EndIssue>`
