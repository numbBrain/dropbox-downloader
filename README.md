# dropbox-downloader
python script to download publicly shared dropbox folders into zip files 

**supports only publicly shared links**
```
optional arguments:

  -h, --help                show this help message and exit
  --links link1, link2...   read links from STDI
  --read file.txt           read links from file
  --dest DEST               specify download directory
  --unzip                   unzip downloaded zipfiles into folders and delete zipfiles
  --retain_zip              don't delete zipfiles after unzipping, when --unzip is used
  ```

**NOTE:** I created this repo to teach myself some python & git

## requirements

this requires only requests package, so:

`pip install requests`