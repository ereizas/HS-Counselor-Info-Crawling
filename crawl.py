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

def get_contacts_from_sprdsheet(soup,job_col,name_cols:list[str],email_col,contact_info,school,name_rvrs_order=False):
    rows = soup.find_all('tr',attrs={'class':re.compile("row-([2-9]|[1-9]\d{1,}) ?(even|odd)?")})
    for row in rows:
        row_text = row.find('td',attrs={'class':'column-'+job_col}).text
        if ('Counsel' in row_text or 'SPED' in row_text or 'Special Education' in row_text or 'Autis' in row_text) and 'MS' not in row_text and 'Bilingual' not in row_text:
            names = row.find('td',attrs={'class':'column-'+name_cols[0]}).text.split('\n')
            for i in range(1,len(name_cols)):
                new_names = row.find('td',attrs={'class':'column-'+name_cols[i]}).text.split('\n')
                for j in range(len(names)):
                    names[j]+=' '+new_names[j]
            emails = row.find('td',attrs={'class':'column-'+email_col}).text.split('\n')
            i = 0
            for i in range(len(names)):
                if name_rvrs_order:
                    names[i]=names[i][names[i].find(',')+2:]+' '+names[i][:names[i].find(',')]
                contact_info[school][names[i]]=[emails[i]]

def get_contacts_from_li_tags(soup,contact_info,school,separator):
    li_tags=soup.find_all('li',attrs={'class':None,'id':None})
    for i in range(len(li_tags)):
        strong_tag = li_tags[i].find('strong')
        if strong_tag and 'Counselor' in strong_tag.text:
            j=i+1
            strong_tag = li_tags[j].find('strong')
            while not strong_tag:
                tag_txt=li_tags[j].text
                separator_ind = tag_txt.find(separator)
                name = tag_txt[:separator_ind-1]
                contact_info[school][name]=[tag_txt[separator_ind+1:-1]]
                j+=1
                strong_tag = li_tags[j].find('strong')
            break

def get_contacts_from_ul_tags(soup,school,header_num,contact_info):
    ul_tags=soup.find_all('ul',attrs={'class':None,'id':None})[1:]
    header_tags=soup.find_all('h'+header_num,string=re.compile('[A-Z].[a-z]* [A-Z].[a-z]*'))
    for i in range(len(ul_tags)):
        header_txt = header_tags[i].text
        colon_ind = header_txt.find(':')
        comma_ind = header_txt.find(',')
        len_text = len(header_txt)
        if colon_ind==-1:
            colon_ind=len_text
        if comma_ind==-1:
            comma_ind=len_text
        end_ind = colon_ind if colon_ind<comma_ind else comma_ind
        contact_info[school][header_txt[:end_ind]]=[ul_tags[i].find('a').text]

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
                        goog_srch_res = google_search_school(school.text,'philasd')
                        if goog_srch_res:
                            school_to_link[school.text]=goog_srch_res
            else:
                goog_srch_res = google_search_school(school.text,'philasd')
                if goog_srch_res:
                    school_to_link[school.text]=goog_srch_res
    #print(len(school_to_link))
    return school_to_link

def get_psd_contact_info():
    school_to_link={'John Bartram High School': 'https://bartram.philasd.org/', 'Thomas A. Edison High School': 'https://edison.philasd.org/', 'Samuel Fels High School': 'https://fels.philasd.org/', 'Frankford High School': 'https://frankfordhs.philasd.org/', 'Benjamin Franklin High School': 'https://bfhs.philasd.org/', 'Horace Furness High School': 'https://furness.philasd.org/', 'Kensington High School': 'https://kensingtonhs.philasd.org/', 'Martin Luther King High School': 'https://mlkhs.philasd.org/', 'Abraham Lincoln High School': 'https://lincoln.philasd.org/', 'Northeast High School': 'https://nehs.philasd.org/', 'Overbrook High School': 'https://overbrookhs.philasd.org/', 'Penn Treaty School (6-12)': 'https://penntreaty.philasd.org/', 'Roxborough High School': 'https://roxboroughhs.philasd.org/', 'William L. Sayre High School': 'https://sayre.philasd.org/', 'South Philadelphia High School': 'https://sphs.philasd.org/', 'Strawberry Mansion High School': 'https://smhs.philasd.org/', 'George Washington High School': 'https://gwhs.philasd.org/', 'West Philadelphia High School': 'https://wphs.philasd.org/', 'Academy at Palumbo': 'https://palumbo.philasd.org/', 'The Arts Academy at Benjamin Rush': 'https://rush.philasd.org/', 'Bodine International Affairs': 'https://bodine.philasd.org/', 'CAPA': 'https://capa.philasd.org/', 'Carver High School for Engineering and Science': 'https://hses.philasd.org/', 'Central High School': 'https://centralhs.philasd.org/', 'GAMP': 'https://gamp.philasd.org/', 'Franklin Learning Center': 'https://flc.philasd.org/', 'Hill-Freedman World Academy High School': 'https://hfwa.philasd.org/', 'Julia R. Masterman School': 'https://masterman.philasd.org/', 'Kensington Creative & Performing Arts High School': 'https://kcapa.philasd.org/', 'Kensington Health Sciences Academy High School': 'https://khsa.philasd.org/', 'Parkway Center City High School': 'https://parkwaycc.philasd.org/', 'Parkway Northwest High School': 'https://parkwaynw.philasd.org/', 'Parkway West High School': 'https://parkwaywest.philasd.org/', 'Philadelphia High School for Girls': 'https://girlshs.philasd.org/', 'Philadelphia Learning Academy': 'https://planorth.philasd.org/', 'Philadelphia Military Academy': 'https://pma.philasd.org/', 'Philadelphia Virtual Academy': 'https://pva.philasd.org/', 'Science Leadership Academy': 'https://sla.philasd.org/', 'Science Leadership Academy at Beeber (6-12)': 'https://slabeeber.philasd.org/', 'The LINC': 'https://thelinc.philasd.org/', 'Walter Biddle Saul High School for Agricultural Sciences': 'https://saul.philasd.org/', 'Building 21': 'https://building21.philasd.org/', 'Constitution High School': 'https://constitutionhs.philasd.org/', 'Murrell Dobbins Vocational School': 'https://dobbins.philasd.org/', 'High School of the Future': 'https://sof.philasd.org/', 'Lankenau High School': 'https://lankenau.philasd.org/', 'Jules E. Mastbaum Technical High School': 'https://mastbaum.philasd.org/', 'Motivation High School': 'https://motivationhs.philasd.org/', 'Paul Robeson High School for Human Services': 'https://robeson.philasd.org/', 'Randolph Technical High School': 'https://randolph.philasd.org/', 'The U School': 'https://uschool.philasd.org/', 'The Workshop School': 'https://workshopschool.philasd.org/', 'Swenson Arts and Technology High School': 'https://swenson.philasd.org/', 'Vaux Big Picture High School': 'https://vaux.philasd.org/'}
    #school_to_link={'Kensington Health Sciences Academy High School': 'https://khsa.philasd.org/'}
    #school mapped to dict of names mapped to email and phone #
    contact_info = dict()
    for school in school_to_link:
        if school in ['South Philadelphia High School','GAMP','Thomas A. Edison High School','Kensington High School', 'The LINC',
                      'Penn Treaty School (6-12)','Constitution High School','Benjamin Franklin High School','Northeast High School',
                      'Roxborough High School','Bodine International Affairs','Randolph Technical High School','CAPA','Central High School',
                      'Hill-Freedman World Academy High School','John Bartram High School','Swenson Arts and Technology High School',
                      'Samuel Fels High School','George Washington High School','Science Leadership Academy','Kensington Health Sciences Academy High School',
                      'Philadelphia Military Academy', 'Murrell Dobbins Vocational School','High School of the Future',
                      'Science Leadership Academy at Beeber (6-12)','Kensington Creative & Performing Arts High School',
                      'Parkway Northwest High School','Jules E. Mastbaum Technical High School']:
            contact_info[school]=dict()
            req = None
            suffs = ['counselors-corner','counselor-corner','faculty-staff','counselor','counselors','support-team','staff','counseling','faculty','contact-us']
            if school not in ['Philadelphia Military Academy','Kensington Creative & Performing Arts High School','Jules E. Mastbaum Technical High School']:
                for suff in suffs:
                    test_req=requests.get(school_to_link[school]+suff)
                    if test_req.status_code>=200 and test_req.status_code<300:
                        print(school_to_link[school]+suff)
                        req=test_req
                        break
            elif school!='Jules E. Mastbaum Technical High School':
                test_req=requests.get(school_to_link[school]+'staff')
                if test_req.status_code>=200 and test_req.status_code<300:
                    print(school_to_link[school]+'staff')
                    req=test_req
            else:
                test_req=requests.get(school_to_link[school]+'contact-us')
                if test_req.status_code>=200 and test_req.status_code<300:
                    print(school_to_link[school]+'contact-us')
                    req=test_req
            if not req:
                links=search(query='counselor site:'+school_to_link[school],stop=1)
                for link in links:
                    print(link)
                    req=requests.get(str(link))
                    break
            if req.status_code>=200 and req.status_code<300:
                soup=BeautifulSoup(req.text,'html.parser')
                if school in ['South Philadelphia High School', 'Murrell Dobbins Vocational School']:
                    p_tags=soup.find_all('p')
                    i = 0
                    num_p_tags=len(p_tags)
                    while i<num_p_tags:
                        tag_txt = p_tags[i].text
                        if (school=='South Philadelphia High School' and 'Counselor' in tag_txt) or school=='Murrell Dobbins Vocational School':
                            name = tag_txt
                            if school=='South Philadelphia High School':
                                name = tag_txt[:tag_txt.find('(')-1]
                            i+=1
                            a_tag = p_tags[i].find('a')
                            if not a_tag:
                                i+=1
                                tag_txt=p_tags[i].text
                                if school=='South Philadelphia High School':
                                    contact_info[school][name]=[tag_txt[tag_txt.find(':')+2:]]
                                elif 'Counsel' in p_tags[i-1].text or 'Special Education' in p_tags[i-1].text or 'SPED' in p_tags[i-1].text:
                                    contact_info[school][name]=[p_tags[i].find('a').text]
                        i+=1
                elif school == 'GAMP':
                    p_tags=soup.find_all('p')
                    for tag in p_tags:
                        tag_txt = tag.text
                        if '@' in tag_txt:
                            #long dash is used not short dash
                            contact_info[school][tag_txt[4:tag_txt.find('–')-1]]=[tag_txt[tag_txt.find('–')+2:]]
                elif school == 'Thomas A. Edison High School':
                    rows = soup.find_all('tr',attrs={'class':re.compile("row-[2-9].\d* (even|odd)")})
                    for row in rows:
                        contact_info[school][row.find('td',attrs={'class':'column-1'}).text]=[row.find('td',attrs={'class':'column-4'}).text]
                elif school=='Kensington High School':
                    get_contacts_from_sprdsheet(soup,'4',['1'],'5',contact_info,school,True)
                elif school in ['Penn Treaty School (6-12)','Constitution High School']:
                    get_contacts_from_sprdsheet(soup,'1',['2'],'3',contact_info,school)
                elif school=='Benjamin Franklin High School':
                    strong_tags=soup.find_all('strong')[2:]
                    for tag in strong_tags:
                        tag_txt=tag.text
                        contact_info[school][tag_txt[:tag_txt.find('–')-1]]=[tag_txt[tag_txt.find('–')+2:]]
                elif school=='Northeast High School':
                    #first two rows initialize the style
                    span_tags = soup.find_all('span',attrs={'style':re.compile('font-weight: (\d)*')})
                    contact_info[school][span_tags[8].text]=[span_tags[11].text]
                    #next rows have a different tag
                    td_tags = soup.find_all('td',attrs={'style':re.compile('height: (\d)*px;width: (\d)*px')})
                    for i in range(11,len(td_tags),5):
                        contact_info[school][td_tags[i].text.strip('\xa0')]=[td_tags[i+3].text.strip('\xa0')]
                elif school=='Roxborough High School':
                    h3_tags = soup.find_all('h3')
                    num_tags=len(h3_tags)
                    for i in range(0,num_tags,2):
                        if i+1<num_tags:
                            contact_info[school][h3_tags[i].text]=[h3_tags[i+1].text]
                elif school=='Bodine International Affairs':
                    li_tags=soup.find_all('li',attrs={'class':None,'id':None})
                    for tag in li_tags:
                        tag_txt=tag.text
                        if 'Counselor' in tag_txt or 'Special Education' in tag_txt:
                            contact_info[school][tag_txt[:tag_txt.find(',')]]=[tag_txt[tag_txt.rfind(',')+2:]]
                elif school=='Randolph Technical High School':
                    li_tags=soup.find_all('li',attrs={'class':None,'id':None})
                    for i in range(len(li_tags)):
                        strong_tag = li_tags[i].find('strong')
                        if strong_tag and 'Counselor' in strong_tag.text:
                            j=i+1
                            strong_tag = li_tags[j].find('strong')
                            while not strong_tag:
                                tag_txt=li_tags[j].text
                                separator_ind = tag_txt.find('(')
                                contact_info[school][tag_txt[:separator_ind-1]]=[tag_txt[separator_ind+1:-1]]
                                j+=1
                                strong_tag = li_tags[j].find('strong')
                            break
                elif school=='CAPA':
                    a_tags = soup.find_all('a',attrs={'href':re.compile('([A-Za-z])@philasd.org')})
                    for tag in a_tags:
                        tag_txt=tag.text
                        name = tag_txt[6:]
                        dot_ind = name.find('.')
                        name = name[0]+name[1:dot_ind+2].lower()+name[dot_ind+2]+name[dot_ind+3:].lower()
                        contact_info[school][name]=[tag.get('href')]
                elif school=='Central High School':
                    td_tags=soup.find_all('td',attrs={'style':'text-align: center'})
                    for i in range(3,len(td_tags),2):
                        tag_txt=td_tags[i].text
                        #' x' should be a valid cutoff for the name assuming names start with a capital letter (i.e. Xavier)
                        contact_info[school][tag_txt[:tag_txt.find(' x')]]=[tag_txt[tag_txt.find('/')+2:]]
                elif school in ['Hill-Freedman World Academy High School','Philadelphia Military Academy','The LINC']:
                    get_contacts_from_sprdsheet(soup,'2','1','3',contact_info,school)
                elif school=='George Washington High School':
                    p_tags=soup.find_all('p',attrs={'style':'text-align: center'})
                    for i in range(1,len(p_tags)):
                        tag_txt=p_tags[i].text
                        if 'Counsel' in tag_txt:
                            a_tag = p_tags[i].find('a')
                            if  a_tag:
                                contact_info[school][tag_txt[:tag_txt.find('\n')]]=[a_tag.text.strip('\xa0')]
                elif school=='Kensington Health Sciences Academy High School':
                    tags = soup.find_all(re.compile('th|td'),attrs={'class':re.compile('column-\d|^$')})
                    for tag in tags:
                        tag_txt = tag.text
                        begin_ind = tag_txt.find('\n')
                        if begin_ind!=-1:
                            end_ind = tag_txt.find('\n',begin_ind+1)
                            job_str = tag_txt[begin_ind:end_ind]
                            if 'Counselor' in job_str or 'Special Education' in job_str:
                                contact_info[school][tag.find('u').text.strip(' ')]=[tag.find('a').text.strip(' ')]
                elif school in ['Science Leadership Academy','Science Leadership Academy at Beeber (6-12)']:
                    p_tags = soup.find_all('p')
                    for tag in p_tags:
                        a_tag=tag.find('a',attrs={'href':re.compile('([A-Za-z])*@([A-Za-z0-9])*.org')})
                        tag_txt=tag.text
                        if a_tag and ('Counselor' in tag_txt or 'Special Education' in tag_txt) and 'LS' not in tag_txt:
                            contact_info[school][a_tag.text]=[a_tag.get('href').strip('mailto:')]
                elif school=='High School of the Future':
                    get_contacts_from_sprdsheet(soup,'3',['1','2'],'4',contact_info,school)
                elif school=='Kensington Creative & Performing Arts High School':
                    a_tags=soup.find_all('a',attrs={'data-vc-container':'.vc_tta','data-vc-tabs':''})
                    panels = soup.find_all('div',attrs={'class':'vc_tta-panel-body'})
                    panels = [panels[i] for i in range(len(a_tags)) if 'Support' in a_tags[i].find('span').text]
                    for panel in panels:
                        h2_tags=panel.find_all('h2')
                        h3_tags=panel.find_all('h3')
                        div_tags=panel.find_all('div',attrs={'class':'vc_toggle_content'})
                        for i in range(len(h2_tags)):
                            tag_txt = h2_tags[i].text
                            if 'Counselor' in tag_txt or 'SPED' in tag_txt or 'Special Education' in tag_txt:
                                contact_info[school][h3_tags[i].text]=[div_tags[i].find('p').text]
                elif school=='Parkway Northwest High School':
                    info_btn = soup.find('a',attrs={'class':'vc_general vc_btn3 vc_btn3-size-md vc_btn3-shape-rounded vc_btn3-style-modern vc_btn3-color-sandy-brown'})
                    contact_info[school][info_btn.text[:info_btn.text.find('-')]]=[info_btn.get('href').strip('mailto:')]
                elif school=='Jules E. Mastbaum Technical High School':
                    get_contacts_from_sprdsheet(soup,'2','3','4',contact_info,school)
                elif school == 'John Bartram High School':
                    get_contacts_from_ul_tags(soup,school,'3',contact_info)
                elif school=='Swenson Arts and Technology High School':
                    get_contacts_from_ul_tags(soup,school,'4',contact_info)
                elif school=='Samuel Fels High School':
                    tags=soup.find_all(re.compile('(^p$)|(^h3$)'))
                    for i in range(1,len(tags),2):
                        name = tags[i].text
                        if not bool(re.match('^(Mrs?)|(Ms)|(Dr)\.. [A-Z].[a-z]* -',name)):
                            break
                        name = name[:name.find(' -')]
                        contact_info[school][name]=[tags[i+1].find('em').text]
    return contact_info
                    
            
print(get_psd_contact_info())
