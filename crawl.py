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
        schools_html=sect.find_all('a')
        for school in schools_html:
            school_wiki__domain_suff = school.get('href')
            if school_wiki__domain_suff:
                school_wiki_req = requests.get("https://en.wikipedia.org"+school_wiki__domain_suff)
                soup=BeautifulSoup(school_wiki_req.text,'html.parser')
                links = soup.find_all('a')
                hs_link = ''
                #searches for school link in wikipedia page and then Google if not found
                for link in links:
                    school_str = school.text
                    up_to_ind = school_str.find('School')
                    school_str_len = len(school_str)
                    if up_to_ind+5!=school_str_len-1:
                        up_to_ind=school_str_len
                    potential_link = link.get('href')
                    if potential_link and 'philasd.org' in potential_link and any(item.lower() in potential_link for item in school_str[:up_to_ind].split()):
                        hs_link=potential_link
                        school_to_link[school.text]=hs_link
                        break
                if not hs_link:
                    #google search
                    pass
            else:
                #google search
                pass
    print(school_to_link)

            

get_phil_sd_hs_links()
