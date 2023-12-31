import requests
from bs4 import BeautifulSoup

def get_phil_sd_hs_links():
    """
    Creates list of Philadelphia school district high school links
    """
    req = requests.get("https://en.wikipedia.org/wiki/List_of_schools_of_the_School_District_of_Philadelphia")
    print(req.status_code)

get_phil_sd_hs_links()
