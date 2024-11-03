import re
import json
from requests import Session
from bs4 import BeautifulSoup

class GoogleLens:
    def __init__(self):
        self.url = "https://lens.google.com"
        self.session = Session()
        self.session.headers.update(
            {'User-agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:103.0) Gecko/20100101 Firefox/103.0'}
        )

    def __get_prerender_script(self, page: str):
        soup = BeautifulSoup(page, 'html.parser')

        prerender_script = list(filter(
            lambda s: (
                'AF_initDataCallback(' in s.text and
                re.search(r"key: 'ds:(\d+)'", s.text).group(1) == "0"),
            soup.find_all('script')))[0].text
        prerender_script = prerender_script.replace(
            "AF_initDataCallback(", "").replace(");", "")
        hash = re.search(r"hash: '(\d+)'", prerender_script).group(1)
        prerender_script = prerender_script.replace(
            f"key: 'ds:0', hash: '{hash}', data:",
            f"\"key\": \"ds:0\", \"hash\": \"{hash}\", \"data\":").replace("sideChannel:", "\"sideChannel\":")

        prerender_script = json.loads(prerender_script)

        return prerender_script['data'][1]

    def __parse_prerender_script(self, prerender_script: dict) -> dict:
        data = {
            "match": None,
            "similar": []
        }

        try:
            data["match"] = {
                "title": prerender_script[0][1][8][12][0][0][0],
                "pageURL": prerender_script[0][1][8][12][0][2][0][4]
            }
        except IndexError:
            pass

        if data["match"] is not None:
            visual_matches = prerender_script[1][1][8][8][0][12]
        else:
            try:
                visual_matches = prerender_script[0][1][8][8][0][12]
            except IndexError:
                return data

        for match in visual_matches:
            data["similar"].append(
                {
                    "title": match[3],
                    "pageURL": match[5],
                }
            )

        return data

    def search_by_url(self, url: str) -> dict:
        with self.session.get(self.url + "/uploadbyurl", params={"url": url}, allow_redirects=True) as response:
            prerender_script = self.__get_prerender_script(response.text)

        return self.__parse_prerender_script(prerender_script)