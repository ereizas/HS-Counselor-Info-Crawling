import requests
from bs4 import BeautifulSoup

def get_phil_sd_hs_links():
    """
    Creates list of Philadelphia school district high school links
    """
    school_to_link = dict()
    req = requests.get("https://en.wikipedia.org/wiki/List_of_schools_of_the_School_District_of_Philadelphia")
    soup = BeautifulSoup(req.text,'html.parser')
    link_sections = soup.find_all('div',attrs={'class':"div-col"})[3:6]
    for sect in link_sections:
        schools_html=sect.find_all('li')
        for school in schools_html:
            school_str = str(school)
            if 'href' in school_str:
                wiki_str_ind = school_str.find('wiki/')+5
                wiki_domain_suff = school_str[wiki_str_ind:school_str.find('\"',wiki_str_ind)]
                #school_wiki_req = requests.get("https://en.wikipedia.org/wiki/")
            else:
                #google search
                pass

            

get_phil_sd_hs_links()
