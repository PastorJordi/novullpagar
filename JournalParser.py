import json

from Parsers import parser_dict
from dataclasses import dataclass

@dataclass
class ParserParams:
    """ Class that keeps track of the parameters of a specific parser,
        with some sensible defaults provided. 
    """
    first_paragraph: int    = 0
    last_paragraph: int     = -1
    json_index: int         = 0

class JournalParser():
    """ Parses a specific journal. """

    def __init__(self, parser_params: ParserParams, data):

        self.params = parser_params
        self.soup = data

    def parse_journal(self) -> str:
        """ Generic parsing method that should work on all journals. """
        # Get the article text with the p-tags so we can reconstruct it later:
        paragraphs = self.soup.findAll('p')[self.params.first_paragraph:self.params.last_paragraph]
        body_content = [p.get_text() for p in paragraphs]

        # Get the JSON data for the headline, description, images...
        scr = self.soup.findAll('script', type="application/ld+json")
        json_dict = json.loads(scr[self.params.json_index].string, strict=False)

        # In some journals, d["image"] are lists, while in some others 
        # are single instances of dict:
        images = json_dict["image"]
        if isinstance(json_dict["image"], list):
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
    "elespanol.com"         : ParserParams(first_paragraph=7, last_paragraph=-5)
}

