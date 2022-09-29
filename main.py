#!python3
import argparse

from tqdm import tqdm

from download import Downloader


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("query", help="The query to search for.")
    parser.add_argument(
        "-n", "--num-results", help="The number of results to get.", default=5, type=int
    )
    parser.add_argument(
        "-o", "--output", help="The output file to write to.", default="output.html"
    )
    parser.add_argument(
        "-d",
        "--disable-stylesheet",
        help="Disable the stylesheet.",
        action="store_true",
    )
    parser.add_argument(
        "-e", "--search-engine", help="The search engine to use.", default="google"
    )
    parser.add_argument(
        "-s",
        "--selector",
        help="The CSS selector to use to find the titles.",
        default=".DKV0Md",
    )
    args = parser.parse_args()

    titles = []
    links = []

    downloader = Downloader(args.query)

    for source in tqdm(downloader.sources):
        url = f"https://{downloader.search_engine}.com/search?q={downloader.search}+site:{source}"
        html = downloader.get_html(url)
        titles += downloader.get_titles(html, args.selector, args.num_results)
        links = downloader.get_links(html, args.selector, args.num_results)

    html_output = downloader.create_html(titles, links, args.disable_stylesheet)

    if args.output:
        with open(args.output, "w") as f:
            f.write(html_output)
    else:
        print(html_output)


if __name__ == "__main__":
    main()
