import json
import requests
from bs4 import BeautifulSoup
import sys
import os

class nvp():
    """just using a class to better organize the code"""
    def __init__(self, url, savpath=None):
        """instantiate class, few checks, store vars"""
        assert isinstance(url, str), 'needs a valid url'
        self.url = url
        self.site = None
        self.article_name = None
        try:
            self.page = requests.get(url)
        except Exception as e:
            print(f'failed when requesting url {url}')
            raise e
        try:
            self.soup = BeautifulSoup(self.page.content, 'html.parser')
        except Exception as e:
            print(f'failed when parsing page content')
            raise e

        if savpath is None:
            self.savpath = os.getcwd()
        else:
            self.savpath = savpath


    def detect_journal(self):
        # find journal, strip https://(www.)
        if self.url[8:].startswith('www.'):
            suburl = self.url[12:]
        else:
            suburl =self.url[8:]

        self.site, *_, self.article_name = suburl.split('/') # fancy but parhaps fragile?

    html_header = (
    '<!DOCTYPE html>\n'
    '<html lang="en">\n'
    '<head>\n'
    '<meta charset="utf-8"/>\n'
    )

    parsers = { # dictionary to pair site with method_name, used by "parse"
        'elpais.com':'elpais',
        'elconfidencial.com': 'elconfidencial'
    }

    def parse(self):
        """this will parse soup back to a simple local html
        it will prepend header and use apropiate parser.
        Parsers must return "html string" of the article (but header)
        """
        method = getattr(self, nvp.parsers[self.site])
        html = method()
        # few checks to dst file
        if os.path.isdir(self.savpath):
            if not self.savpath.endswith('/'):
                self.savpath += '/'
            fpath = self.savpath + self.article_name

        with open("output1.html", "w", encoding='utf-8') as file:
        file.write(
            nvp.html_header + html 
        )

    # individual parsers below.

    def elpais(self):
        body_content = []
        for item in self.soup.findAll('p', attrs={'class' : ""})[1:-3]: # concat paragraph content
            c_content = item.contents
            if c_content is None:
                continue
            if len(c_content)>1:
                body_content += [
                    "".join([str(x) for x in c_content])
                ]
            else:
                body_content += [str(c_content[0])]
        
        scr = self.soup.findAll('script', type="application/ld+json")
        d = json.loads(scr[1].string)
        out = (
            f"<h1>{d['headline']}</h1><h2>{d['description']}</h2>"+
            '<p>'+('</p><p>'.join(body_content))+'</p>'+ # using double
            '\n  '.join([
                f'<img src="{d["image"][i]["url"]}" width="280">' for i in range(len(d['image']))
            ])
        )
        return out # this is actually returned rather than stored in self

    def elconfidencial(self):
        body_content = []
        for item in self.soup.findAll('p')[:-1]: # concat paragraph content
            c_content = item.contents
            if c_content is None:
                continue
            if len(c_content)>1:
                body_content += [
                    "".join([str(x) for x in c_content])
                ]
            else:
                body_content += [str(c_content[0])]
        scr = soup.findAll('script', type="application/ld+json")
        d = json.loads(scr[0].string)
        out = (
            f"<h1>{d['headline']}</h1><h2>{d['description']}</h2>"+
            '<p>'+('</p><p>'.join(body_content))+'</p>'+ # using double
            '\n  '.join([
                f'<img src="{d["image"][i]["url"]}" width="280">' for i in range(len(d['image']))
            ])
        )
        return out


if __name__=="__main__":
    url = 'https://elpais.com/opinion/2021-09-01/vacunarse-es-una-obligacion-civica-y-solidaria.html'
    q = nvp(url)
    q.detect_journal()
    print(q.html_header)
    #print(q.parse())