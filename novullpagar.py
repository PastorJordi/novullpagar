import requests
import sys
import os

from bs4 import BeautifulSoup
from JournalParser import parser_exporter

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

        self.detect_journal()
        self.get_parser()

    def detect_journal(self):
        # find journal, strip https://(www.)
        if self.url[8:].startswith('www.'):
            suburl = self.url[12:]
        else:
            suburl = self.url[8:]

        self.site, *_, self.article_name = suburl.split('/') # fancy but parhaps fragile?

    def get_parser(self):
        self.parser = parser_exporter(self.site, self.soup)

    html_header = (
    '<!DOCTYPE html>\n'
    '<html lang="en">\n'
    '<head>\n'
    '<meta charset="utf-8"/>\n'
    )

    def parse(self):
        """this will parse soup back to a simple local html
        it will prepend header and use apropiate parser.
        Parsers must return "html string" of the article (but header)
        """
        html = self.parser.parse_journal()
        # few checks to dst file
        if os.path.isdir(self.savpath):
            if not self.savpath.endswith('/'):
                self.savpath += '/'
            fpath = self.savpath + self.article_name

        with open("output1.html", "w", encoding='utf-8') as file:
            file.write(
                nvp.html_header + html 
            )

if __name__=="__main__":

    test_urls = {
        "elpais"            : "https://elpais.com/espana/2021-09-03/hacienda-solicita-a-la-casa-real-los-pagos-que-ha-hecho-juan-carlos-i-desde-su-abdicacion-hasta-2018.html",
        "ara"               : "https://www.ara.cat/politica/new-york-times-aprofundeix-presumptes-vincles-l-entorn-puigdemont-russia_1_4104228.html",
        "elmundo"           : "https://www.elmundo.es/opinion/editorial/2021/09/03/61310a88e4d4d8ce758b45d0.html",
        "elconfidencial"    : "https://www.elconfidencial.com/cultura/2021-09-03/dune-denis-villeneuve-critica_3269702/",
        "elespanol"         : "https://www.elespanol.com/opinion/tribunas/20210901/covid-19-vuelta-normalidad-todavia-lejos/608559145_12.html",
        "eldiario"          : "https://www.eldiario.es/escolar" # Not yet implemented
    }

    q = nvp(test_urls["ara"])
    q.parse()