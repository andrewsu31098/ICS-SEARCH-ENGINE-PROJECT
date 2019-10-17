import logging
import re
import os
from collections import defaultdict
from urllib.parse import urlparse, urljoin, parse_qs
from corpus import Corpus
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

class Crawler:
    """
    This class is responsible for scraping urls from the next available link in frontier and adding the scraped links to
    the frontier
    """

    def __init__(self, frontier):
        self.frontier = frontier
        self.corpus = Corpus()
        self.url_paths = defaultdict(lambda: defaultdict(int))
        self.data_of_docs = []

    def get_data_of_docs(self):
        return self.data_of_docs

    def start_crawling(self):
        """
        This method starts the crawling process which is scraping urls from the next available link in frontier and adding
        the scraped links to the frontier
        """
        while self.frontier.has_next_url():
            url = self.frontier.get_next_url()
            logger.info("Fetching URL %s ... Fetched: %s, Queue size: %s", url, self.frontier.fetched, len(self.frontier))
            url_data = self.fetch_url(url)

            data_for_index = {
                'id': self.corpus.get_file_identifier(url),
                'content': url_data['content']
            }

            self.data_of_docs.append(data_for_index)

            for next_link in self.extract_next_links(url_data):
                if self.corpus.get_file_name(next_link) is not None:
                    if self.is_valid(next_link):
                        parsed = urlparse(next_link)
                        self.url_paths[parsed.scheme + "://" + parsed.netloc + parsed.path][tuple(parse_qs(parsed.query, keep_blank_values = True).keys())] += 1
                        self.frontier.add_url(next_link)

    def fetch_url(self, url):
        """
        This method, using the given url, should find the corresponding file in the corpus and return a dictionary
        containing the url, content of the file in binary format and the content size in bytes
        :param url: the url to be fetched
        :return: a dictionary containing the url, content and the size of the content. If the url does not
        exist in the corpus, a dictionary with content set to None and size set to 0 can be returned.
        """

        the_file = self.corpus.get_file_name(url)

        url_data = {
            "url": url,
            "content": None,
            "size": 0
        }

        if the_file == None:
            return url_data

        with open(the_file, mode = "rb") as open_file:
            url_data["content"] = open_file.read()
            url_data["size"] = os.path.getsize(the_file)

        return url_data

    def extract_next_links(self, url_data):
        """
        The url_data coming from the fetch_url method will be given as a parameter to this method. url_data contains the
        fetched url, the url content in binary format, and the size of the content in bytes. This method should return a
        list of urls in their absolute form (some links in the content are relative and needs to be converted to the
        absolute form). Validation of links is done later via is_valid method. It is not required to remove duplicates
        that have already been fetched. The frontier takes care of that.

        Suggested library: lxml
        """

        if url_data["content"] == None:
            return []

        bs = BeautifulSoup(url_data["content"], features = "lxml")

        return [urljoin(url_data["url"], link.get("href")) for link in bs.find_all("a") if link.get("href") != None]

    def is_valid(self, url):
        """
        Function returns True or False based on whether the url has to be fetched or not. This is a great place to
        filter out crawler traps. Duplicated urls will be taken care of by frontier. You don't need to check for duplication
        in this method
        """
        parsed = urlparse(url)
        if parsed.scheme not in set(["http", "https"]):
            return False
        try:
            if not ".ics.uci.edu" in parsed.hostname \
                    or re.match(".*\.(css|js|bmp|gif|jpe?g|ico" + "|png|tiff?|mid|mp2|mp3|mp4" \
                                    + "|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf" \
                                    + "|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso|epub|dll|cnf|tgz|sha1" \
                                    + "|thmx|mso|arff|rtf|jar|csv" \
                                    + "|rm|smil|wmv|swf|wma|zip|rar|gz|pdf)$", parsed.path.lower()):
                return False

            if re.search(r"(([a-zA-Z0-9-]+/)\2{6,})", parsed.scheme + "://" + parsed.netloc + parsed.path) \
                or (True if (self.url_paths[parsed.scheme + "://" + parsed.netloc + parsed.path][tuple(parse_qs(parsed.query, keep_blank_values = True).keys())] > 100 and parsed.query != "") else False):
                return False

            return True

        except TypeError:
            print("TypeError for ", parsed)
            return False