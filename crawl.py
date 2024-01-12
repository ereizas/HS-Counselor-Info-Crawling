import requests
from bs4 import BeautifulSoup

def google_search_school(query):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    s=requests.Session()
    req = s.get('https://www.google.com/search?q='+'+'.join(query.split())+'&num=5&ie=utf-8&oe=utf-8',headers=headers)
    soup=BeautifulSoup(req.text,'html.parser')
    for search_wrapper in soup.find_all('a'):
        link = search_wrapper.get('href')
        if search_wrapper and link and 'philasd' in link:
            return link[:link.find('.org/')+6]
    return None

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
            a_tag_portion = school.find('a')
            school_wiki__domain_suff=None
            if a_tag_portion:
                school_wiki__domain_suff = a_tag_portion.get('href')
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
                        if potential_link and 'philasd.org' in potential_link and 'www.philasd.org' not in potential_link and 'https://philasd.org/' not in potential_link and any(item.lower() in potential_link for item in school_str[:up_to_ind].split()):
                            hs_link=potential_link
                            if hs_link[-1]!='/':
                                hs_link+='/'
                            school_to_link[school.text]=hs_link[:hs_link.find('.org/')+5]
                            break
                    if not hs_link:
                        goog_srch_res = google_search_school(school.text)
                        if goog_srch_res:
                            school_to_link[school.text]=goog_srch_res
            else:
                goog_srch_res = google_search_school(school.text)
                if goog_srch_res:
                    school_to_link[school.text]=goog_srch_res
    #print(len(school_to_link))
    print(school_to_link)
    for school in school_to_link:
        couns_req = None
        suffs = ['counselors-corner','faculty-staff','counselor','counselors','staff']
        for suff in suffs:
            test_req=requests.get(school_to_link[school]+suff)
            if test_req.status_code==200:
                couns_req=test_req
                break
        if not couns_req:
            couns_req=requests.get('https://www.google.com/search?q=counselors&as_sitesearch='+school_to_link[school])
        if couns_req.status_code==200:
            soup=BeautifulSoup(couns_req.text,'html.parser')
get_phil_sd_hs_links()
