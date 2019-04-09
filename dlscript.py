from urllib.request import Request, urlopen
import json

with open("download.json", "rb") as infile:
    toDownload = json.load(infile)

for filename in toDownload.keys():
    print("downloading {0} ...".format(filename))

    url = toDownload[filename]
    req = Request(url)
    req.add_header('User-Agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36')
    print("get {0}".format(url))
    result = urlopen(req).read()
    with open(filename, "wb") as outfile:
        outfile.write(result)
