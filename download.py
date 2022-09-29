import logging

import bs4
import fake_headers
import requests

logging.basicConfig(level=logging.INFO, filename="download.log")


class Downloader:
    def __init__(
        self,
        search: str,
        search_engine: str = "google",
        sources: list = [
            "openlibrary.org",
            "gutenberg.org",
            "scholar.google.com",
            "books.google.com",
            "news.google.com",
            "guides.library.harvard.edu",
            "en.wikisource.org",
            "en.wikipedia.org",
            "iep.utm.edu",
            "plato.stanford.edu",
        ],
    ):
        self.search = search.replace(" ", "+")
        self.search_engine = search_engine
        self.sources = sources

    def get_html(self, url) -> str:
        """
        Get HTML source code from a link.

        Returns
        -------
        str
            The HTML source code of the specified URL.
        """

        headers = fake_headers.Headers(
            browser="chrome", os="macos", headers=True
        ).generate()

        html = ""

        try:
            html = requests.get(url, headers=headers).text
        except Exception as e:
            logging.error(e)

        return html

    def get_titles(self, html: str, selector: str = ".DKV0Md", num_results: int = 5):
        """
        Get the titles of links from the passed Google search HTML.

        Parameters
        ----------
        html : str
            The HTML of the Google search results.
        selector : str, optional
            The CSS selector to use to find the titles, by default ".DKV0Md" (Google)
        num_results : int, optional
            The number of results to get, by default 5 (make sure it matches the number of links)

        Returns
        -------
        list
            The titles of the links.
        """

        titles = []
        parsed_html = bs4.BeautifulSoup(html, "html.parser")

        # Get the titles of the top 5 results from each website, but make sure they aren't ads or Google internal links.
        # Also make sure they aren't already in the list.
        # All of the results are stored together, so we need to get the first 5 from the first source, then the next 5 from the second source, etc.
        for i, title in enumerate(parsed_html.select(selector)):
            if title.text in titles:
                continue
            titles.append(title.get_text())

        for i, title in enumerate(parsed_html.select(selector)):
            if i == num_results:
                break
            if title.text in titles:
                continue
            titles.append(title.text)

        return titles

    def get_links(self, html: str, selector: str = ".DKV0Md", num_results: int = 5):
        """
        Get the links from the passed Google search HTML.

        Parameters
        ----------
        html : str
            The HTML of the search results.
        selector : str, optional
            The CSS selector to use to find the links, by default ".DKV0Md" (Google)
        num_results : int, optional
            The number of results to get, by default 5 (make sure it matches the number of titles)

        Returns
        -------
        list
            The links of the search results.
        """
        # Only get the top 5 results from each source
        links = []

        parsed_html = bs4.BeautifulSoup(html, "html.parser")

        # Get the links of the top 5 results, but make sure they aren't ads or Google internal links.
        # Also make sure they aren't already in the list.
        for i, link in enumerate(parsed_html.select(selector)):
            if i == num_results:
                break
            if link.text in links:
                continue
            links.append(link.get_text())

        return links

    def create_html(self, titles: list, links: list, stylesheet: bool = True) -> str:
        """
        Creates a valid HTML file with passed titles and links.

        Parameters
        ----------
        titles : list
            The titles of the links to be displayed.
        links : list
            The urls of the links to be embedded.
        stylesheet : bool, optional
            Whether or not to include a stylesheet, by default True

        Returns
        -------
        str
            The generated HTML.
        """

        html = """
        <!DOCTYPE html>
        <html>
        <head>
        """

        if not stylesheet:
            html += '<link rel="stylesheet" href="https://cdn.simplecss.org/simple.min.css">'

        html += """
        </head>
        <body>
        <h1>Links</h1>
        <ul>
        """

        for title, link in zip(titles, links):
            html += f'\n<li><a href="{link}">{title}</a></li>'

        html += """
        </ul>
        </body>
        </html>
        """

        return html

    def get_results(self) -> str:
        """
        Get the HTML, titles, and links from the search engine and output the finished HTML.

        Returns
        -------
        str
            The finished HTML
        """

        # Get the raw HTML
        for source in tqdm(self.sources):
            html = self.get_html(
                f"https://{self.search_engine}.com/search?q={self.search}+site:{source}"
            )

            # Get the titles and links
            titles = self.get_titles(html)
            links = self.get_links(html)

            # Create the HTML
            html = self.create_html(titles, links)

        return html
