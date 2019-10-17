import atexit
import logging

from crawler import Crawler
from frontier import Frontier
from iindexbuilder import IIndexBuilder

if __name__ == "__main__":
    # Configures basic logging
    logging.basicConfig(format='%(asctime)s (%(name)s) %(levelname)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p',
                        level=logging.INFO)

    # Instantiates frontier and loads the last state if exists
    frontier = Frontier()
    frontier.load_frontier()
    # Registers a shutdown hook to save frontier state upon unexpected shutdown
    atexit.register(frontier.save_frontier)

    # Instantiates a crawler object and starts crawling
    crawler = Crawler(frontier)
    crawler.start_crawling()

    # Builds the inverted index and stores it in a json file
    iib = IIndexBuilder(crawler.get_data_of_docs())
    iib.build_iindex()
    iib.normalize()
    iib.create_iindex_file()
    iib.create_totaldocs_file()
    iib.create_df_file()
