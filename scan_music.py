#!/usr/bin/env python3
import os
import glob

dir = "/media/storage/Music"

def scan_for_palylist():
    for (path, subdirs, files) in os.walk(dir):
        os.chdir(path)
        if glob.glob("*.mp3") != []:
            cur_dir = os.path.split(path)
            _m3u = open( "/home/neuro/" + os.path.split(path)[1] + ".m3u" , "w" )
            #print(os.path.split(path))
            _m3u.write("#EXTM3U\n")
            for song in glob.glob("*.mp3"):
                _m3u.write("#EXTINF:0,"+ song + "\n")
                _m3u.write(dir + "/" + cur_dir[1] + "/" + song + "\n")
            _m3u.close()
    #os.chdir(dir) # Not really needed..


def main():
   scan_for_palylist()
   print("Playlists created")

if __name__ == '__main__':
    main()


