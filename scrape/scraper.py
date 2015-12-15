class Scraper(object):
    """The base class for all Scrapers.

    Should output data in CSV format.

    A scraper outputs it's data in environ.SCRAPER_DATA/data_dir
    """

    data_dir = None

    def __init__(self):
        """Initialize the Scraper."""
        pass


    def scrape(self):
        """Run the scraper."""
        raise NotImplementedError()
