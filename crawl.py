import requests
from bs4 import BeautifulSoup
from googlesearch import search
import re

def google_search_school(query,qualifying_str):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    s=requests.Session()
    req = s.get('https://www.google.com/search?q='+'+'.join(query.split())+'&num=5&ie=utf-8&oe=utf-8',headers=headers)
    soup=BeautifulSoup(req.text,'html.parser')
    for search_wrapper in soup.find_all('a'):
        link = search_wrapper.get('href')
        if search_wrapper and link and qualifying_str in link:
            return link[:link.find('.org/')+6]
    return None

def get_phil_sd_hs_links():
    """
    Creates list of Philadelphia school district high school links
    """
    '''school_to_link = dict()
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
                        goog_srch_res = google_search_school(school.text,'philasd')
                        if goog_srch_res:
                            school_to_link[school.text]=goog_srch_res
            else:
                goog_srch_res = google_search_school(school.text,'philasd')
                if goog_srch_res:
                    school_to_link[school.text]=goog_srch_res
    #print(len(school_to_link))
    print(school_to_link)'''
    school_to_link={'John Bartram High School': 'https://bartram.philasd.org/', 'Thomas A. Edison High School': 'https://edison.philasd.org/', 'Samuel Fels High School': 'https://fels.philasd.org/', 'Frankford High School': 'https://frankfordhs.philasd.org/', 'Benjamin Franklin High School': 'https://bfhs.philasd.org/', 'Horace Furness High School': 'https://furness.philasd.org/', 'Kensington High School': 'https://kensingtonhs.philasd.org/', 'Martin Luther King High School': 'https://mlkhs.philasd.org/', 'Abraham Lincoln High School': 'https://lincoln.philasd.org/', 'Northeast High School': 'https://nehs.philasd.org/', 'Overbrook High School': 'https://overbrookhs.philasd.org/', 'Penn Treaty School (6-12)': 'https://penntreaty.philasd.org/', 'Roxborough High School': 'https://roxboroughhs.philasd.org/', 'William L. Sayre High School': 'https://sayre.philasd.org/', 'South Philadelphia High School': 'https://sphs.philasd.org/', 'Strawberry Mansion High School': 'https://smhs.philasd.org/', 'George Washington High School': 'https://gwhs.philasd.org/', 'West Philadelphia High School': 'https://wphs.philasd.org/', 'Academy at Palumbo': 'https://palumbo.philasd.org/', 'The Arts Academy at Benjamin Rush': 'https://rush.philasd.org/', 'Bodine International Affairs': 'https://bodine.philasd.org/', 'CAPA': 'https://capa.philasd.org/', 'Carver High School for Engineering and Science': 'https://hses.philasd.org/', 'Central High School': 'https://centralhs.philasd.org/', 'GAMP': 'https://gamp.philasd.org/', 'Franklin Learning Center': 'https://flc.philasd.org/', 'Hill-Freedman World Academy High School': 'https://hfwa.philasd.org/', 'Julia R. Masterman School': 'https://masterman.philasd.org/', 'Kensington Creative & Performing Arts High School': 'https://kcapa.philasd.org/', 'Kensington Health Sciences Academy High School': 'https://khsa.philasd.org/', 'Parkway Center City High School': 'https://parkwaycc.philasd.org/', 'Parkway Northwest High School': 'https://parkwaynw.philasd.org/', 'Parkway West High School': 'https://parkwaywest.philasd.org/', 'Philadelphia High School for Girls': 'https://girlshs.philasd.org/', 'Philadelphia Learning Academy': 'https://planorth.philasd.org/', 'Philadelphia Military Academy': 'https://pma.philasd.org/', 'Philadelphia Virtual Academy': 'https://pva.philasd.org/', 'Science Leadership Academy': 'https://sla.philasd.org/', 'Science Leadership Academy at Beeber (6-12)': 'https://slabeeber.philasd.org/', 'The LINC': 'https://thelinc.philasd.org/', 'Walter Biddle Saul High School for Agricultural Sciences': 'https://saul.philasd.org/', 'Building 21': 'https://building21.philasd.org/', 'Constitution High School': 'https://constitutionhs.philasd.org/', 'Murrell Dobbins Vocational School': 'https://dobbins.philasd.org/', 'High School of the Future': 'https://sof.philasd.org/', 'Lankenau High School': 'https://lankenau.philasd.org/', 'Jules E. Mastbaum Technical High School': 'https://mastbaum.philasd.org/', 'Motivation High School': 'https://motivationhs.philasd.org/', 'Paul Robeson High School for Human Services': 'https://robeson.philasd.org/', 'Randolph Technical High School': 'https://randolph.philasd.org/', 'The U School': 'https://uschool.philasd.org/', 'The Workshop School': 'https://workshopschool.philasd.org/', 'Swenson Arts and Technology High School': 'https://swenson.philasd.org/', 'Vaux Big Picture High School': 'https://vaux.philasd.org/'}
    #school mapped to dict of names mapped to email and phone #
    contact_info = dict()
    for school in school_to_link:
        if school in ['South Philadelphia High School','GAMP','Thomas A. Edison High School','Frankford High School','Kensington High School',
                      'Penn Treaty School (6-12)','Constitution High School','Jules E. Mastbaum Technical High School',
                      'Benjamin Franklin High School','Northeast High School','Roxborough High School','The Arts Academy at Benjamin Rush',
                      'Bodine International Affairs','Randolph Technical High School','CAPA','Central High School',
                      'Hill-Freedman World Academy High School','John Bartram High School','Swenson Arts and Technology High School',
                      'Samuel Fels High School','William L. Sayre High School']:
            contact_info[school]=dict()
            couns_req = None
            suffs = ['counselors-corner','faculty-staff','counselor','counselors','staff']
            for suff in suffs:
                test_req=requests.get(school_to_link[school]+suff)
                if test_req.status_code==200:
                    couns_req=test_req
                    break
            if not couns_req:
                links=search(query='counselor site:'+school_to_link[school],stop=1)
                for link in links:
                    couns_req=requests.get(str(link))
                    break
                soup = BeautifulSoup(couns_req.text,'html.parser')
            if couns_req.status_code==200:
                soup=BeautifulSoup(couns_req.text,'html.parser')
                if school == 'South Philadelphia High School':
                    p_tags=soup.find_all('p')
                    i = 0
                    num_p_tags=len(p_tags)
                    while i<num_p_tags:
                        tag_txt = p_tags[i].text
                        if 'Counselor' in tag_txt:
                            name = tag_txt[:tag_txt.find('(')-1]
                            i+=2
                            tag_txt=p_tags[i].text
                            contact_info[school][name]=[tag_txt[tag_txt.find(':')+2:],None]
                        i+=1   
                elif school == 'GAMP':
                    p_tags=soup.find_all('p')
                    for tag in p_tags:
                        tag_txt = tag.text
                        if '@' in tag_txt:
                            #long dash is used not short dash
                            contact_info[school][tag_txt[4:tag_txt.find('–')-1]]=[tag_txt[tag_txt.find('–')+2:],None]
                elif school == 'Thomas A. Edison High School':
                    rows = soup.find_all('tr',attrs={'class':re.compile("row-[2-9]+\d* (even|odd)")})
                    for row in rows:
                        contact_info[school][row.find('td',attrs={'class':'column-1'}).text]=[row.find('td',attrs={'class':'column-4'}).text]
            
get_phil_sd_hs_links()
