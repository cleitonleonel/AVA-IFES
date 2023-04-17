import tempfile
import requests
import webbrowser
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

retry_strategy = Retry(
    connect=3,
    total=3,
    backoff_factor=1,
    status_forcelist=[429, 500, 502, 503, 504, 104],
    method_whitelist=["HEAD", "POST", "PUT", "GET", "OPTIONS"]
)
adapter = HTTPAdapter(max_retries=retry_strategy)


class Response(object):

    def __init__(self, json_data, status_code=200):
        self.json_data = json_data
        self.status_code = status_code

    def json(self):
        return self.json_data


class Browser(object):

    def __init__(self):
        self.response = None
        self.headers = None
        self.session = requests.Session()

    def set_headers(self, headers=None):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/87.0.4280.88 Safari/537.36"
        }
        if headers:
            for key, value in headers.items():
                self.headers[key] = value

    def get_headers(self):
        return self.headers

    def get_soup(self):
        return BeautifulSoup(self.response.content, "html.parser")

    def page_preview(self):
        with tempfile.NamedTemporaryFile("wb", delete=False, suffix=".html") as file:
            file.write(self.response.content)
        webbrowser.open_new_tab(f"file://{file.name}")

    def send_request(self, method, url, **kwargs):
        try:
            self.session.mount("https://", adapter)
            self.session.mount("http://", adapter)
            return self.session.request(method, url, **kwargs)
        except requests.exceptions.ConnectionError:
            return Response({"result": False,
                             "object": self.response,
                             "message": "Network Unavailable. Check your connection."
                             }, 104)
