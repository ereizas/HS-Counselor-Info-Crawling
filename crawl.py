import requests
from bs4 import BeautifulSoup

def get_phil_sd_hs_links():
    """
    Creates list of Philadelphia school district high school links
    """
    req = requests.get("https://en.wikipedia.org/wiki/List_of_schools_of_the_School_District_of_Philadelphia")
    soup = BeautifulSoup(req.text,'html.parser')
    link_sections = soup.find_all('div',attrs={'class':"div-col"})[3:6]

get_phil_sd_hs_links()
