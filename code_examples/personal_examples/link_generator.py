"""
File description.

Dreamsub.stream is an anime website
that collects series from various fansub organizations
and make them available for download.

Their download system is based on a cdn and they generate their links
based on a simple pattern, quite naive imho.

Therefor a scraper is not needed
and the download links for the series
can be automatically generated from the inital url
"""

import argparse
import re
import sys


class Dreamsub:
    """Class definition."""

    SPLIT_PATTERN = "https://dreamsub.stream/anime/"
    CDN_URI = "https://cdn.dreamsub.stream/fl/"

    def __init__(self, link, episode_number, quality):
        """Class init."""
        self.quality = quality
        self.link = link
        self.ep_number = int(episode_number)

    def link_generator(self):
        """Generate links for given series link."""
        anime_name = self.link.split(self.SPLIT_PATTERN)[1]  # take last part of the uri (the slug) #noqa
        for episode in range(1, self.ep_number + 1):
            full_name = "{cdn}{name}/{ep_number}/SUB_ITA/{quality}p".format(
                cdn=self.CDN_URI,
                name=anime_name,
                ep_number=f'{episode:03d}' if self.ep_number > 99 else f'{episode:02d}', #noqa
                quality=self.quality
            )
            yield full_name

    def list_links(self):
        """Returns a list of downloadable links for given series."""
        return self.link_generator()


parser = argparse.ArgumentParser(description='Dreamsub links generator.')
parser.add_argument(
    'link', metavar='https://dreamsub.stream/anime/angel-beats',
    type=str, help='Link of the series to be generated'
)
parser.add_argument(
    '-e', '--episodes',
    required=True, dest="episodes",
    metavar='episodes_number', type=int,
    help='Number of episodes'
)
parser.add_argument(
    '-q', '--quality', nargs="?", default="720",
    dest="quality", required=True,
    metavar='720', type=int,
    help='An integer for quality selection'
)

args = parser.parse_args()

if __name__ == "__main__":
    series_link = args.link
    episode_number = args.episodes
    quality = args.quality
    dreamsub = Dreamsub(
        link=series_link,
        episode_number=episode_number,
        quality=quality)

    print(*dreamsub.list_links(), sep="\n")
