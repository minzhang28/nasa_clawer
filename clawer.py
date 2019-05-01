
import urllib
import urllib2
import json
import re
import sys
import os
from urllib2 import urlopen, URLError, HTTPError


nasa_domain = "https://www.nasa.gov"
nasa_api_endpoint = "https://www.nasa.gov/api/2"

pdf_links = []
pages_to_check = []

# this may change due to all nasa page are dynamically generated
contents = urllib2.urlopen("https://www.nasa.gov/api/1/record/node/349697.json").read()
result_html = json.loads(contents)['landingPage']['body'].encode('utf-8')

# to find all the sub_pages from home page which links to a real content (url starts with /audience)
sub_page_url_surfixes = re.findall(r'href="(/audience/.+?)"', result_html, re.I)
sub_page_urls = list(map(lambda x: '{}{}'.format(nasa_domain, x), sub_page_url_surfixes))

dir_to_save = "{}/{}".format(os.getcwd(), "nasa_pdf")

try:
    os.mkdir(dir_to_save)
except OSError:
    print ("Creation of the directory %s failed" % dir_to_save)
else:
    print ("Successfully created the directory %s " % dir_to_save)

print("---------- Downloading Starts ----------")
for url in sub_page_urls:
    try:
        sub_page = urllib2.urlopen(url).read()
        content_page_links = list(map(lambda x: '{}{}'.format(nasa_api_endpoint, x), re.findall(r'"(/education-item/\d+?)"', sub_page, re.I)))
        for link in content_page_links:
            try:
                pdf_page = json.loads(urllib2.urlopen(link).read())['_source']['body'].encode('utf-8')
                pdf_links = re.findall(r'href="(http[s]?://.+?.pdf)"', pdf_page, re.I)
                for p_link in pdf_links:
                    pdf_name = p_link.split("/")[-1]
                    try:
                        print("downloading: {}".format(p_link))
                        urllib.urlretrieve(p_link, "{}/{}".format(dir_to_save, pdf_name))
                    except IOError as e:
                        print("failed to save file {} for reason: {}".format(pdf_name, str(e)))
                        pass
                if len(pdf_links) == 0 :
                    pages_to_check += [url]
            except HTTPError as e :
                print("can't open pdf page: {}, error message: {}, skip".format(link, str(e)))
                # keep it running as some URL are empty from Nasa
                pass
    except HTTPError as e:
        print("can't open url: {}, error message: {}, skip".format(url, str(e)))
        # keep it running as some URL are empty from Nasa
        pass

print("------------ ALL DONE ! ------------")

print("please double check the following URLS, there might be more sub pages for them or using different languages")
for p in pages_to_check:
    print(p)
