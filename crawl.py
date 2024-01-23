import requests
from bs4 import BeautifulSoup
from googlesearch import search
import re
from openpyxl import load_workbook
import openpyxl
from random import randint
from time import sleep
from json import dump, load

def google_search(query):
    links=search(query,stop=1)
    for link in links:
        try:
            req=requests.get(str(link))
            if req.status_code==200:
                return str(link)
        except Exception as e:
            print(f'Error that occurred from query {query}: {e}')
    return None
    
def get_contacts_from_sprdsheet(soup,job_col,name_cols:list[str],email_col,contact_info,school,name_rvrs_order=False):
    if school=='Shoemaker':
        soup=soup.find('table',attrs={'id':'tablepress-263'})
    rows = soup.find_all('tr',attrs={'class':re.compile("row-([2-9]|[1-9]\d{1,}) ?(even|odd)?")})
    for row in rows:
        row_text = row.find('td',attrs={'class':'column-'+job_col}).text
        if ('Counsel' in row_text or 'SPED' in row_text or 'Special Ed' in row_text or 'Autis' in row_text) and 'MS' not in row_text and 'Bilingual' not in row_text:
            names = row.find('td',attrs={'class':'column-'+name_cols[0]}).text.split('\n')
            for i in range(1,len(name_cols)):
                new_names = row.find('td',attrs={'class':'column-'+name_cols[i]}).text.split('\n')
                for j in range(len(names)):
                    names[j]+=' '+new_names[j]
            emails = row.find('td',attrs={'class':'column-'+email_col}).text.split('\n')
            i = 0
            for i in range(len(names)):
                if emails[i]:
                    if name_rvrs_order:
                        if '(' not in names[i]:
                            names[i]=names[i][names[i].find(',')+2:]+' '+names[i][:names[i].find(',')]
                        else:
                            names[i]=names[i][:names[i].find('(')]
                    emails[i]=emails[i].replace('[dot]','.')
                    emails[i]=emails[i].replace('[at]','@')
                    contact_info[school][names[i]]=emails[i]

def get_contacts_from_ul_tags(soup,school,header_num,contact_info,title_included=False):
    ul_tags=soup.find_all('ul',attrs={'class':None,'id':None})[1:]
    regex = '^[A-Z].[a-z]* [A-Z].[a-z]*'
    if title_included:
        regex='^(Mrs?)|(Ms)|(Dr)\. [A-Z].[a-z]* [A-Z].[a-z]*'
    header_tags=soup.find_all('h'+header_num,string=re.compile(regex))
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
        contact_info[school][header_txt[:end_ind]]=ul_tags[i].find('a').text

def get_PA_hs_links(county_to_retrieve=None):
    req = requests.get('https://en.wikipedia.org/wiki/List_of_high_schools_in_Pennsylvania')
    soup = BeautifulSoup(req.text,'html.parser')
    hs_links = dict()
    schools_html = soup.find_all(re.compile('span|div'),attrs={'class':re.compile('mw-headline|div-col')})
    len_schools_html = len(schools_html)
    i=0
    if county_to_retrieve:
        while i<len_schools_html and (schools_html[i].name!='span' or county_to_retrieve not in schools_html[i].text):
            i+=1
    while i<len_schools_html:
        county = schools_html[i].text
        if 'County' not in county:
            break
        hs_links[county]=dict()
        i+=1
        #Added to query to ensure the correct school is retrieved
        city = None
        while i<len_schools_html and (schools_html[i].name=='div' or (schools_html[i].name=='span' and schools_html[i].parent.name!='h2')):
            if schools_html[i].name=='span' and schools_html[i].get('a'):
                city = schools_html[i].text
            elif schools_html[i].name=='div':
                schools=schools_html[i].find_all('li')
                for school in schools:
                    print(school.text)
                    query = school.text
                    if city:
                        query+=' ' + city
                    else:
                        query+=' ' +county
                    goog_srch_res = google_search(query)
                    print(f"Sleeping for 30 seconds")
                    sleep(randint(30, 40))
                    if goog_srch_res:
                        hs_links[county][school.text]=goog_srch_res
            i+=1
        if county_to_retrieve:
            break
    print(hs_links)
    with open('hs_links.json','w') as file:
        dump(hs_links,file)
    file.close()

def get_psd_contact_info():
    contact_info = dict()
    school_to_link=None
    '''with open('philadelphia_school_links.json') as file:
        school_to_link=load(file)
        school_to_link=school_to_link['Philadelphia County (City of Philadelphia)']
    file.close()'''
    school_to_link={"New Foundations Charter School": "https://www.newfoundations.org/"}
    for school in school_to_link:
        #Mastery Charter has several schools to account for programmatically with the same structure
        if school in ['South Philadelphia High School','GAMP','Thomas A. Edison High School','Kensington High School', 'The LINC', 
                      'Penn Treaty School (6-12)','Constitution High School','Benjamin Franklin High School','Northeast High School',
                      'Roxborough High School','Bodine International Affairs','Randolph Technical High School','CAPA','Central High School',
                      'Hill-Freedman World Academy High School','John Bartram High School','Swenson Arts and Technology High School',
                      'Samuel Fels High School','George Washington High School','Science Leadership Academy','Kensington Health Sciences Academy High School',
                      'Philadelphia Military Academy', 'Murrell Dobbins Vocational School','High School of the Future', 
                      'Science Leadership Academy at Beeber (6-12)','Kensington Creative & Performing Arts High School','The Crefeld School',
                      'Parkway Northwest High School','Jules E. Mastbaum Technical High School','Mariana Bracetti Academy Charter School',
                      'New Foundations Charter School']:
            contact_info[school]=dict()
            req = None
            if school not in ['Philadelphia Military Academy','Kensington Creative & Performing Arts High School',
                              'Jules E. Mastbaum Technical High School','Mariana Bracetti Academy Charter School']:
                suffs = ['counselors-corner','counselor-corner','faculty-staff','counselor','counselors','support-team','counseling','staff','faculty',
                     'contact-us','staff-directory','about/staff','high-school-support-services/','apps/staff/','our-team','staff/hs-faculty/',
                     'our-families/support-services','families/staff-directory/','support','faculty-and-staff','about/facultystaffdirectory',
                     'who-we-are/meet-our-educators','discover/facultystaff','about/faculty']
                for suff in suffs:
                    test_req=requests.get(school_to_link[school]+suff)
                    #print(test_req.status_code)
                    if test_req.status_code>=200 and test_req.status_code<300:
                        print(test_req.url)
                        req=test_req
                        break
            elif school not in ['Jules E. Mastbaum Technical High School','Mariana Bracetti Academy Charter School']:
                test_req=requests.get(school_to_link[school]+'staff')
                if test_req.status_code>=200 and test_req.status_code<300:
                    req=test_req
            elif school!='Mariana Bracetti Academy Charter School':
                test_req=requests.get(school_to_link[school]+'contact-us')
                if test_req.status_code>=200 and test_req.status_code<300:
                    req=test_req
            else:
                test_req=requests.get(school_to_link[school]+'our-team')
                if test_req.status_code>=200 and test_req.status_code<300:
                    req=test_req
            if not req:
                link=google_search('counselor site:'+school_to_link[school])
                print(link)
                if link:
                    req=requests.get(link)
            if req and req.status_code>=200 and req.status_code<300:
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
                                name = name[:name.find('(')-1]
                            i+=1
                            a_tag = p_tags[i].find('a')
                            if not a_tag:
                                i+=1
                                tag_txt=p_tags[i].text
                                if school=='South Philadelphia High School':
                                    contact_info[school][name]=tag_txt[tag_txt.find(':')+2:]
                                elif 'Counsel' in p_tags[i-1].text or 'Special Ed' in p_tags[i-1].text or 'SPED' in p_tags[i-1].text:
                                    contact_info[school][name]=p_tags[i].find('a').text
                        i+=1
                elif school == 'GAMP':
                    p_tags=soup.find_all('p')
                    for tag in p_tags:
                        tag_txt = tag.text
                        if '@' in tag_txt:
                            #long dash is used not short dash
                            contact_info[school][tag_txt[4:tag_txt.find('–')-1]]=tag_txt[tag_txt.find('–')+2:]
                elif school == 'Thomas A. Edison High School':
                    rows = soup.find_all('tr',attrs={'class':re.compile("row-[2-9] (even|odd)")})
                    for row in rows:
                        contact_info[school][row.find('td',attrs={'class':'column-1'}).text]=row.find('td',attrs={'class':'column-4'}).text
                elif school=='Kensington High School':
                    get_contacts_from_sprdsheet(soup,'4',['1'],'5',contact_info,school,True)
                elif school in ['Penn Treaty School (6-12)','Constitution High School']:
                    get_contacts_from_sprdsheet(soup,'1',['2'],'3',contact_info,school)
                elif school=='Benjamin Franklin High School':
                    strong_tags=soup.find_all('strong')[2:]
                    for tag in strong_tags:
                        tag_txt=tag.text
                        contact_info[school][tag_txt[:tag_txt.find('–')-1]]=tag_txt[tag_txt.find('–')+2:]
                elif school=='Northeast High School':
                    #first two rows initialize the style
                    span_tags = soup.find_all('span',attrs={'style':re.compile('font-weight: (\d)*')})
                    contact_info[school][span_tags[8].text]=span_tags[11].text
                    #next rows have a different tag
                    td_tags = soup.find_all('td',attrs={'style':re.compile('height: (\d)*px;width: (\d)*px')})
                    for i in range(11,len(td_tags),5):
                        contact_info[school][td_tags[i].text.strip('\xa0')]=td_tags[i+3].text.strip('\xa0')
                elif school=='Roxborough High School':
                    h3_tags = soup.find_all('h3')
                    num_tags=len(h3_tags)
                    for i in range(0,num_tags,2):
                        if i+1<num_tags:
                            contact_info[school][h3_tags[i].text]=h3_tags[i+1].text
                elif school=='Bodine International Affairs':
                    li_tags=soup.find_all('li',attrs={'class':None,'id':None})
                    for tag in li_tags:
                        tag_txt=tag.text
                        if 'Counselor' in tag_txt or 'Special Ed' in tag_txt:
                            contact_info[school][tag_txt[:tag_txt.find(',')]]=tag_txt[tag_txt.rfind(',')+2:]
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
                                contact_info[school][tag_txt[:separator_ind-1]]=tag_txt[separator_ind+1:-1]
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
                        contact_info[school][name]=tag.get('href')
                elif school=='Central High School':
                    td_tags=soup.find_all('td',attrs={'style':'text-align: center'})
                    for i in range(3,len(td_tags),2):
                        tag_txt=td_tags[i].text
                        #' x' should be a valid cutoff for the name assuming names start with a capital letter (i.e. Xavier)
                        contact_info[school][tag_txt[:tag_txt.find(' x')]]=tag_txt[tag_txt.find('/')+2:]
                elif school in ['Hill-Freedman World Academy High School','Philadelphia Military Academy','The LINC']:
                    get_contacts_from_sprdsheet(soup,'2','1','3',contact_info,school)
                elif school=='George Washington High School':
                    p_tags=soup.find_all('p',attrs={'style':'text-align: center'})
                    for i in range(1,len(p_tags)):
                        tag_txt=p_tags[i].text
                        if 'Counsel' in tag_txt:
                            a_tag = p_tags[i].find('a')
                            if  a_tag:
                                contact_info[school][tag_txt[:tag_txt.find('\n')]]=a_tag.text.strip('\xa0')
                elif school=='Kensington Health Sciences Academy High School':
                    tags = soup.find_all(re.compile('th|td'),attrs={'class':re.compile('column-\d|^$')})
                    for tag in tags:
                        tag_txt = tag.text
                        begin_ind = tag_txt.find('\n')
                        if begin_ind!=-1:
                            end_ind = tag_txt.find('\n',begin_ind+1)
                            job_str = tag_txt[begin_ind:end_ind]
                            if 'Counselor' in job_str or 'Special Ed' in job_str:
                                contact_info[school][tag.find('u').text.strip(' ')]=tag.find('a').text.strip(' ')
                elif school in ['Science Leadership Academy','Science Leadership Academy at Beeber (6-12)','The Crefeld School']:
                    p_tags = soup.find_all('p')
                    for tag in p_tags:
                        a_tag=tag.find('a',attrs={'href':re.compile('([A-Za-z])*@([A-Za-z0-9])*.org')})
                        tag_txt=tag.text
                        if a_tag and ('Counselor' in tag_txt or 'Special Ed' in tag_txt) and 'LS' not in tag_txt:
                            contact_info[school][a_tag.text]=a_tag.get('href').strip('mailto:')
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
                            if 'Counselor' in tag_txt or 'SPED' in tag_txt or 'Special Ed' in tag_txt:
                                contact_info[school][h3_tags[i].text]=div_tags[i].find('p').text
                elif school=='Parkway Northwest High School':
                    info_btn = soup.find('a',attrs={'class':'vc_general vc_btn3 vc_btn3-size-md vc_btn3-shape-rounded vc_btn3-style-modern vc_btn3-color-sandy-brown'})
                    contact_info[school][info_btn.text[:info_btn.text.find('-')]]=info_btn.get('href').strip('mailto:')
                elif school=='Jules E. Mastbaum Technical High School':
                    get_contacts_from_sprdsheet(soup,'2','3','4',contact_info,school)
                elif school == 'John Bartram High School':
                    get_contacts_from_ul_tags(soup,school,'3',contact_info,True)
                elif school=='Swenson Arts and Technology High School':
                    get_contacts_from_ul_tags(soup,school,'4',contact_info)
                elif school=='Samuel Fels High School':
                    tags=soup.find_all(re.compile('(^p$)|(^h3$)'))
                    for i in range(1,len(tags),2):
                        name = tags[i].text
                        if not bool(re.match('^(Mrs?)|(Ms)|(Dr)\.. [A-Z].[a-z]* -',name)):
                            break
                        name = name[:name.find(' -')]
                        contact_info[school][name]=tags[i+1].find('em').text
                elif school=='Mariana Bracetti Academy Charter School':
                    div_tags = soup.find_all('div',attrs={'class':re.compile('__column$')})[2:]
                    for tag in div_tags:
                        tag_txt=tag.text
                        if 'Special Ed' in tag_txt:
                            a_tag = tag.find('a')
                            contact_info[school][a_tag.text]=a_tag.get('href').strip('mailto:')
                elif school=='New Foundations Charter School':
                    div_tags=soup.find_all('div',attrs={'class':'col-12 col-md-6 vw-team-item-wrap text-center'})
                    for tag in div_tags:
                        tag_txt=tag.text
                        if 'Counselor' in tag_txt and 'Grade' not in tag_txt:
                            contact_info[school][tag.find('h5').text]=tag.find('a').get('href').strip('mailto:')
        elif school=='Mastery Charter Schools (Gratz, Lenfest, Pickett, Shoemaker, Thomas, Hardy Williams)':
            req=requests.get(school_to_link[school])
            soup = BeautifulSoup(req.text,'html.parser')
            a_tags=soup.find_all('a',string=re.compile('-12$'))
            for tag in a_tags:
                campus_name = ''
                for char in tag.text:
                    if not char.isnumeric():
                        campus_name+=char
                    else:
                        campus_name=campus_name.strip(' ')
                        break
                contact_info[campus_name]=dict()
                temp_req = requests.get(tag.get('href'))
                soup = BeautifulSoup(temp_req.text,'html.parser')
                get_contacts_from_sprdsheet(soup,'3',['1','2'],'4',contact_info,campus_name)
    return contact_info

def write_to_excel_file(contact_info,school_distr,file_name):
    wb = openpyxl.Workbook()
    sheet = wb.active
    sheet.title = school_distr
    sheet.cell(row=1, column=1).value='School'
    sheet.cell(row=1,column=2).value='Counselor Name'
    sheet.cell(row=1, column=3).value='Email'
    i = 2
    for school in contact_info:
        for couns in contact_info[school]:
            sheet.cell(row=i,column=1).value=school
            sheet.cell(row=i,column=2).value=couns
            sheet.cell(row=i,column=3).value=contact_info[school][couns]
            i+=1
    wb.save(file_name)
            
print(get_psd_contact_info())
#write_to_excel_file(get_psd_contact_info(),'Philadelphia School District','counselor_contacts.xlsx')
#get_PA_hs_links('Montgomery County')
#get_PA_hs_links()