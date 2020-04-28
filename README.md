# dropbox-downloader
python script to download publicly shared Dropbox folders into zip files

### This script can:

* **download public Dropbox folders as zip files**
* **read links from a file**
* **unzip zip files into folders after download**

### Usage:

`$ python dropbox.py --help`
```
optional arguments:

  -h, --help                show this help message and exit
  --links link1, link2...   read links from STDI
  --read file.txt           read links from file
  --dest DEST               specify download directory
  --unzip                   unzip downloaded zipfiles into folders and delete zipfiles
  --retain_zip              don't delete zipfiles after unzipping, when --unzip is used
  ```
### Example
  `$ python dropbox.py --read links.txt --dest Downloads --unzip --retain_zip`

  this command reads links from the file links.txt, downloads files into the Downloads folder, unzips downloaded zip files, but also keeps the downloaded zip files

**NOTE:** I created this repo to teach myself some python & git. Feedbacks are appreciated.

## requirements

this requires only requests package, so:

`pip install requests`