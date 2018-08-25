#!/usr/bin/python3

#This is free and unencumbered software released into the public domain.
#
#Anyone is free to copy, modify, publish, use, compile, sell, or
#distribute this software, either in source code form or as a compiled
#binary, for any purpose, commercial or non-commercial, and by any
#means.
#
#In jurisdictions that recognize copyright laws, the author or authors
#of this software dedicate any and all copyright interest in the
#software to the public domain. We make this dedication for the benefit
#of the public at large and to the detriment of our heirs and
#successors. We intend this dedication to be an overt act of
#relinquishment in perpetuity of all present and future rights to this
#software under copyright law.
#
#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
#EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
#MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
#IN NO EVENT SHALL THE AUTHORS BE LIABLE FOR ANY CLAIM, DAMAGES OR
#OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
#ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
#OTHER DEALINGS IN THE SOFTWARE.
#
#For more information, please refer to <http://unlicense.org/>

import sys
import re
import argparse
import operator
import math

from xml.etree.ElementTree import iterparse
from itertools import groupby

# These regions are not exhaustive, and may need to be modified
sixty_hz_regions = ["Brazil","Canada","Japan","Korea","Mexico","USA","World"]
fifty_hz_regions = ["World","Europe","France","Germany","Sweden","Hong Kong","Australia","Italy","Portugal"]


# Parses a no-intro filename to map regions to speeds, either '60Hz' or '50Hz'
def get_speeds(name):
    tokens = re.findall("\((.*?)\)", name)
    regions = []
    if not tokens:
        regions.append("Unknown")
    for token in tokens:
        regions.extend([r.strip(" ") for r in token.split(",")])
    speeds = []
    speeds.append("60Hz" if len(set(regions) & set(sixty_hz_regions)) > 0 else "50Hz")
    if len(set(regions) & set(fifty_hz_regions)) > 0:
        speeds.append("50Hz")


    return set(speeds)

# Parses a logiqx data file for roms.  This file is assumed to come from
# no-intro's datomatic service.  Other dat files with non-conforming names
# have undefined behavior
def parse_no_intro_dat(filename):
    no_intro_roms = []

    for _, elem in iterparse(filename):
        if elem.tag == 'rom':
            for speed in get_speeds(elem.attrib['name']):
                rom = Rom(elem.attrib)
                rom.speed = speed
                no_intro_roms.append(rom)
        elem.clear()
    return no_intro_roms


# Represents a single rom using metadata
class Rom:
    def __init__(self, attribs):
        self.sha1 = attribs['sha1'].lower()
        self.md5 = attribs['md5'].lower()
        self.crc = attribs['crc'].lower()
        self.name = attribs['name']
        self.size = attribs['size'].lower()


    def __repr__(self):
        return str(self.__dict__)


# Gets the sha256 digests from a SmokeMonsterPacks everdrive pack list file.
def get_data_for_sha1(smdbfile):
    sums = {}
    with open(smdbfile) as smdb:
        for line in smdb:
            (sha256, filename, sha1, md5, crc32) = line.split('\t')
            sums[sha1] = sha256
    return sums


if __name__ == '__main__':

    parser = argparse.ArgumentParser(prog="rom_speed_packlist")

    required = parser.add_argument_group('required arguments')
    required.add_argument("-d","--dat", help="No-intro dat file", type=str, nargs=1, required=True)
    required.add_argument("-s","--smdb", help="Smokemonster pack db file", type=str, nargs=1, required=True)

    parser.add_argument("-p","--prefix", help="Prefix for filenames", type=str, nargs=1, default=[""])
    parser.add_argument("-m","--max-per-dir", help="Max roms per directory", type=int, nargs=1, default=[10000])
    parser.add_argument("-6","--region-60hz", help="Add additional 60Hz region", type=str, nargs='*')
    parser.add_argument("-5","--region-50hz", help="Add additional 50Hz region", type=str, nargs='*')
    parser.add_argument("-o","--out", help="Output file.  If not specified, output will be written to stdout", type=str)
    parser.add_argument("-x","--exclude", help="Exclude keywords in rom names", type=str,nargs="*")


    
    args = parser.parse_args()

    if args.region_60hz is not None:
        sixty_hz_regions.extend(args.region_60hz)

    if args.region_50hz is not None:
        fifty_hz_regions.extend(args.region_50hz)


    print("60 Hz Regions: {}".format(",".join(sixty_hz_regions)), file=sys.stderr)
    print("50 Hz Regions: {}".format(",".join(fifty_hz_regions)), file=sys.stderr)

    roms = parse_no_intro_dat(args.dat[0])
    sha1_to_sha256 = get_data_for_sha1(args.smdb[0])
    max_per = args.max_per_dir[0]

    fifty_hertz_roms = [r for r in roms if r.speed == '50Hz']
    sixty_hertz_roms = [r for r in roms if r.speed == '60Hz']
    speed_groups = [fifty_hertz_roms, sixty_hertz_roms]

    supergroups = []
    for speed_group in speed_groups:
        groups = [list(g) for k, g in groupby(speed_group, lambda s: s.name[0])]

        supergroup = []

        for group in groups:
            if len(supergroup) + len(group) < max_per:
                supergroup.extend(group)
            else:
                supergroups.append(supergroup)
                supergroup = []
                supergroup.extend(group)

        supergroups.append(supergroup)

    out = sys.stdout
    if args.out:
        out = open(args.out,"w")
    for group in supergroups:
        if len(group) < 1:
            continue
        first_char = group[0].name[0]
        if first_char > 'Z' or first_char < '0':
            first_char = "#"
        last_char = group[len(group)-1].name[0]
        segment = "{}-{}".format(first_char, last_char)

        if last_char == first_char:
            segment = ""

        for rom in group:

            # Skip roms based on keywords
            skip = False
            if args.exclude:
                for kw in args.exclude:
                    if rom.name.find(kw) >= 0:
                        skip = True
            if skip:
                continue

            name = "{} {}/{}/{}".format(args.prefix[0], rom.speed, segment,rom.name)
            try:
                sha256 = sha1_to_sha256[rom.sha1] 
            except:
                sha256 = "MISSING"
            print("{}\t{}\t{}\t{}\t{}".format(sha256, name, rom.sha1, rom.md5, rom.crc), file=out)

    out.close()

