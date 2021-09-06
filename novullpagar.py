import requests
import sys
import os
import json
from bs4 import BeautifulSoup
from dataclasses import dataclass
import webbrowser
from selenium import webdriver
import time
# this is integrated in the same file now.
# from JournalParser import parser_exporter

## MINIMAL CONFIG FOR SELENIUM
# EXEC_PATH = None #

DRIVER_PATH = os.path.join(
    os.path.dirname(sys.argv[0]), # script path
    'chromedriver'
    )

class nvp():
    """just using a class to better organize the code"""
    def __init__(self, url, savpath=None):
        """instantiate class, few checks, store vars"""
        assert isinstance(url, str), 'needs a valid url'
        self.url = url
        self.site = None
        self.article_name = None
        self.htmlfile = None

        

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
        #self.parser = parser_exporter(self.site, self.soup)
        self.parser = parser_exporter(self.site, self.url)


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
        else:
            fpath = self.savpath

        if fpath.endswith('/'):
            fpath = fpath[:-1] 
        if not fpath.endswith('.html'):
            fpath += '.html'

        with open(fpath, "w", encoding='utf-8') as file:
            file.write(
                nvp.html_header + html 
            )
        self.htmlfile = fpath

@dataclass
class ParserParams:
    """ Class that keeps track of the parameters of a specific parser,
        with some sensible defaults provided. 
    """
    # TODO: @AFont What's the advantage of creating a class for it? vs e.g.
    # having default kwargs and passing a dict of kwargs which can be unpacked.?
    first_paragraph: int    = 0
    last_paragraph: int     = -1
    json_index: int         = 0
    selenium: bool          = False # whether to use selenium to load page

class JournalParser():
    """ Parses a specific journal. """

    def __init__(self, parser_params: ParserParams, url):

        self.params = parser_params
        self.url = url


        if not self.params.selenium:
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
        else:
            # load content using headless selenium
            options = webdriver.chrome.options.Options()
            options.add_argument("--headless")
            ## TODO: adapt to firefox & edge?
            browser = webdriver.Chrome(
                DRIVER_PATH,
                options=options
            )
            browser.get(url) 
            browser.implicitly_wait(4) 
            time.sleep(4)
            self.soup = BeautifulSoup(browser.page_source, "html.parser")
            browser.quit()
        

    def parse_journal(self) -> str:
        """ Generic parsing method that should work on all journals. """
        # Get the article text with the p-tags so we can reconstruct it later:
        paragraphs = self.soup.findAll('p')[self.params.first_paragraph:self.params.last_paragraph]

        # body_content = [p.get_text() for p in paragraphs]
        # switching back to old strategy to retrieve (.contents) and keep hrefs/links
        body_content = []
        for item in paragraphs: 
            c_content = item.contents
            if c_content is None:
                continue
            if len(c_content)>1:
                body_content += [
                    "".join([str(x) for x in c_content])
                ]
            elif isinstance(c_content, list):
                if len(c_content):
                    body_content += [str(c_content[0])]
            else:
                body_content += str(c_content)

        # Get the JSON data for the headline, description, images...
        scr = self.soup.findAll('script', type="application/ld+json")
        json_dict = json.loads(scr[self.params.json_index].string, strict=False)

        # In some journals, d["image"] are lists, while in some others 
        # are single instances of dict:
        images = json_dict["image"]
        if isinstance(images, list):
            image_string = '\n'.join([f'<img src="{im["url"]}" width="280">' 
                                        for im in images])
        else:
            image_string = '\n' + f'<img src="{images["url"]}" width="280">'

        out = (
            f"<h1>{json_dict['headline']}</h1>"
            + '<p>'+('</p><p>'.join(body_content))+'</p>' # using double
            + image_string
            )

        return out 

def parser_exporter(site: str, site_data) -> JournalParser:
    """ Returns the appropiate JournalParser object together with some exception
    handling.
    """
    try:
        parameters = parser_dict[site]
    except KeyError:
        raise Exception(f"Couldn't find parser for site: {site}")

    return JournalParser(parameters, site_data)

"""
The parser_dict contains the parser data for each journal. To add a new one,
add a new entry with the appropiate parameters. See JournalParser.py and the 
ParserParams dataclass to see which fields are allowed.
"""
    
parser_dict = {
    "elpais.com"            : ParserParams(json_index=1),
    "elconfidencial.com"    : ParserParams(),
    "elmundo.es"            : ParserParams(), # elMundo has different paywall messages
    "ara.cat"               : ParserParams(),
    "elespanol.com"         : ParserParams(first_paragraph=7, last_paragraph=-5),
    "eldiario.es"           : ParserParams(first_paragraph=2, last_paragraph=-11),
    "elperiodico.com"       : ParserParams(first_paragraph=8, last_paragraph=-7),
    "abc.es"                : ParserParams(last_paragraph=-7,selenium=True) 
}



# Actually run the script, as a standalone cmd (# generate a .sh to export alias)
if __name__=="__main__":

    help_msg = """
        usage: 
            python3 novullpagar.py [url] (path_to_store_html) 
        or (if using alias)
        novullpagar [url] (path_to_store_html)'
        """
    # assert sys.argv>1, help_msg # debugging with code below
    assert len(sys.argv)<4, help_msg

    if len(sys.argv)>1: # expected behavior
        q = nvp(*sys.argv[1:])
    else: # debug        
        test_urls = {
            "elpais"            : "https://elpais.com/espana/2021-09-03/hacienda-solicita-a-la-casa-real-los-pagos-que-ha-hecho-juan-carlos-i-desde-su-abdicacion-hasta-2018.html",
            "ara"               : "https://www.ara.cat/politica/new-york-times-aprofundeix-presumptes-vincles-l-entorn-puigdemont-russia_1_4104228.html",
            "elmundo"           : "https://www.elmundo.es/opinion/editorial/2021/09/03/61310a88e4d4d8ce758b45d0.html",
            "elconfidencial"    : "https://www.elconfidencial.com/cultura/2021-09-03/dune-denis-villeneuve-critica_3269702/",
            "elespanol"         : "https://www.elespanol.com/opinion/tribunas/20210901/covid-19-vuelta-normalidad-todavia-lejos/608559145_12.html",
            "eldiario"          : "https://www.eldiario.es/escolar/mil-dias-bloqueo-antidemocratico-judicial_132_8258583.html", # Not yet implemented
            "elperiodico"       : "https://www.elperiodico.com/es/opinion/20210901/autopistas-medio-siglo-despues-articulo-jordi-mercader-12033522"
        }

        q = nvp(test_urls["elespanol"])
    
    q.parse()
    webbrowser.open(q.htmlfile)