# rom-utils
Utilities for dealing with file metadata

## rom_speed_packlist 

  A utility to parse no-intro dat files ( https://datomatic.no-intro.org/ )and Smokemonster DB files ( https://github.com/SmokeMonsterPacks/EverDrive-Packs-Lists-Database )
  with the sole goal of creating a new SMDB file to organize roms by console speed: 60Hz and 50Hz.
  
  Requires: Python 3 (tested on Python 3.6, 3.7)
  

```
# Just use "python" on windows instead of python 3
python3 rom_speed_packlist.py -d Sega\ -\ Master\ System\ -\ Mark\ III\ \(20180824-082512\).dat \
                              -s ../EverDrive-Packs-Lists-Database/smsroms.txt \
                              -p "Master Everdrive/0" -m 128 -o "Master EverDrive Speed Addon SMDB.txt"
```


```
usage: rom_speed_packlist [-h] -d DAT -s SMDB [-p PREFIX] [-m MAX_PER_DIR]
                          [-6 [REGION_60HZ [REGION_60HZ ...]]]
                          [-5 [REGION_50HZ [REGION_50HZ ...]]] [-o OUT]
                          [-x [EXCLUDE [EXCLUDE ...]]]

optional arguments:
  -h, --help            show this help message and exit
  -p PREFIX, --prefix PREFIX
                        Prefix for filenames
  -m MAX_PER_DIR, --max-per-dir MAX_PER_DIR
                        Max roms per directory
  -6 [REGION_60HZ [REGION_60HZ ...]], --region-60hz [REGION_60HZ [REGION_60HZ ...]]
                        Add additional 60Hz region
  -5 [REGION_50HZ [REGION_50HZ ...]], --region-50hz [REGION_50HZ [REGION_50HZ ...]]
                        Add additional 50Hz region
  -o OUT, --out OUT     Output file. If not specified, output will be written
                        to stdout
  -x [EXCLUDE [EXCLUDE ...]], --exclude [EXCLUDE [EXCLUDE ...]]
                        Exclude keywords in rom names

required arguments:
  -d DAT, --dat DAT     No-intro dat file
  -s SMDB, --smdb SMDB  Smokemonster pack db file
```
