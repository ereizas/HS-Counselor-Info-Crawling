import requests
from bs4 import BeautifulSoup
import re
import openpyxl
from time import sleep
from random import randint
from json import dump, load
from search import google_search

def get_PA_hs_links(county_to_retrieve:str=None):
    """
    Parses wikipedia page to create a dictionary that maps county to a dictionary that maps school name to school url and writes to a json file with 
    the created dictionary hs_links
    @param county_to_retrieve : str of a county in PA
    """
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
        if not county_to_retrieve:
            county = schools_html[i].text
            if 'County' not in county:
                break
            hs_links[county]=dict()
            i+=1
        #Added to query to ensure the correct school is retrieved
        city = None
        while i<len_schools_html and (schools_html[i].name=='div' or (schools_html[i].name=='span' and schools_html[i].parent.name!='h2')):
            if schools_html[i].name=='span' and schools_html[i].find('a'):
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
    with open('hs_links.json' if not county_to_retrieve else county_to_retrieve+'.json','w') as file:
        dump(hs_links,file)
    file.close()

def get_contacts_from_sprdsheet(soup:BeautifulSoup,job_col:str,name_cols:list[str],email_col:str,contact_info:dict,school:str,name_rvrs_order=False):
    """
    Parses contacts of high school Special Ed staff and Counselors into a dictionary from a certain format of spreadsheet within HTML of the school website indicated by school
    @param soup
    @param job_col : str column num where the job of the staff member is located
    @param name_cols : list of columns where the full name or first and last name of the staff member is located
    @param email_col : str column where the email of the staff member is located
    @param contact_info : dictionary mapping school name indicated by school to a dictionary mapping school staff member name to email
    @param school : name of the school
    @param name_rvrs_order : boolean indicating whether the names are in reverse order in a single column
    """
    if school=='Shoemaker':
        soup=soup.find('table',attrs={'id':'tablepress-263'})
    rows = soup.find_all('tr',attrs={'class':re.compile("row-([2-9]|[1-9]\d{1,}) ?(even|odd)?")})
    for row in rows:
        td_tag = row.find('td',attrs={'class':'column-'+job_col})
        if td_tag:
            row_text=td_tag.text
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

def get_contacts_from_ul_tags(soup:BeautifulSoup,school:str,header_num:str,contact_info:dict,title_included=False):
    """
    Parses ul tags of a certain format to retrieve contact info for counselors of the school indicated by school
    @param soup
    @param school : name of the school
    @param header_num : str number for which type of header the staff member info is located
    @param contact_info : dictionary mapping school name indicated by school to a dictionary mapping school staff member name to email
    @param title_included : whether an honorific is included with the staff member name
    """
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

def get_contacts_from_name_pos_class_div_tags(soup:BeautifulSoup,contact_info:dict,school:str):
    """
    Parses div tags that have the classes name-position and email-phone for contact info of counselors of the school indicated by school
    @param soup
    @param contact_info : dictionary mapping school name indicated by school to a dictionary mapping school staff member name to email
    @param school : name of the school
    """
    div_tags=soup.find_all('div',attrs={'class':re.compile('name-position|email-phone')})
    num_tags = len(div_tags)
    for i in range(0,num_tags,2):
        name_txt = div_tags[i].text
        if 'Counselor' in name_txt:
            contact_info[school][div_tags[i].find('a').text.replace('.\n\t','. ').replace('\n','').replace('\t','')]=div_tags[i+1].find('a').text

def get_contacts_from_p_tags(soup:BeautifulSoup,contact_info:dict,school:str):
    """
    Parses p tags of a certain format to extract contact info of Special Education specialists and counselors of the school indicated by school
    @param soup
    @param contact_info : dictionary mapping school name indicated by school to a dictionary mapping school staff member name to email
    @param school : name of the school
    """
    p_tags = soup.find_all('p')
    for tag in p_tags:
        a_tag=tag.find('a',attrs={'href':re.compile('([A-Za-z])*@([A-Za-z0-9])*.org')})
        tag_txt=tag.text
        if a_tag and ('Counselor' in tag_txt or 'Special Ed' in tag_txt) and 'LS' not in tag_txt:
            contact_info[school][a_tag.text]=a_tag.get('href').strip('mailto:')

def is_hs_staff(txt:str):
    """
    Checks if the staff in the given text of a certain format is a high school staff member
    @txt
    """
    grade_ind = txt.find('Grade')
    if grade_ind==-1:
        return True
    i=grade_ind+len('Grade ')+1
    grade = ''
    while txt[i]!='-':
        grade+=txt[i]
        i+=1
    if grade=='K':
        return False
    grade = int(grade)
    return grade>8

def get_soup(url:str,suff:str):
    """
    Makes the request and returns the corresponding BeautifulSoup object
    @param url : base link for the school
    @param suff : suffix which leads to counselor or staff page for the school
    """
    req=requests.get(url+suff)
    return BeautifulSoup(req.text,'html.parser')

def get_school_to_link(file_name:str, county:str):
    """
    Extracts dictionary that maps school to link from json indicated by file_name
    @param file_name
    """
    file = open(file_name)
    school_to_link=load(file)[county]
    file.close()
    return school_to_link

def get_phila_county_contacts():
    """
    Retrieves the contact info for high school counselors and special education specialists in Philadelphia County
    """
    contact_info = dict()
    school_to_link=get_school_to_link('philadelphia_school_links.json','Philadelphia County (City of Philadelphia)')
    for school in school_to_link:
        contact_info[school]=dict()
        if school == 'John Bartram High School':
            soup=get_soup(school_to_link[school],'counselors-corner')
            get_contacts_from_ul_tags(soup,school,'3',contact_info,True)
        elif school=='Thomas A. Edison High School':
            soup=get_soup(school_to_link[school],'counselors-corner')
            rows = soup.find_all('tr',attrs={'class':re.compile("row-[2-9] (even|odd)")})
            for row in rows:
                contact_info[school][row.find('td',attrs={'class':'column-1'}).text]=row.find('td',attrs={'class':'column-4'}).text
        elif school=='Samuel Fels High School':
            soup=get_soup(school_to_link[school],'counselors-and-social-work')
            tags=soup.find_all(re.compile('(^p$)|(^h3$)'))
            for i in range(1,len(tags),2):
                name = tags[i].text
                if not bool(re.match('^(Mrs?)|(Ms)|(Dr)\.. [A-Z].[a-z]* -',name)):
                    break
                name = name[:name.find(' -')]
                contact_info[school][name]=tags[i+1].find('em').text
        elif school=='Benjamin Franklin High School':
            soup=get_soup(school_to_link[school],'counselors')
            strong_tags=soup.find_all('strong')[2:]
            for tag in strong_tags:
                tag_txt=tag.text
                contact_info[school][tag_txt[:tag_txt.find('–')-1]]=tag_txt[tag_txt.find('–')+2:]
        elif school=='Kensington High School':
            soup=get_soup(school_to_link[school],'faculty-staff')
            get_contacts_from_sprdsheet(soup,'4',['1'],'5',contact_info,school,True)
        elif school=='Northeast High School':
            soup=get_soup(school_to_link[school],'counseling')
            #first two rows initialize the style
            span_tags = soup.find_all('span',attrs={'style':re.compile('font-weight: (\d)*')})
            contact_info[school][span_tags[8].text]=span_tags[11].text
            #next rows have a different tag
            td_tags = soup.find_all('td',attrs={'style':re.compile('height: (\d)*px;width: (\d)*px')})
            for i in range(11,len(td_tags),5):
                contact_info[school][td_tags[i].text.strip('\xa0')]=td_tags[i+3].text.strip('\xa0')
        elif school=='Penn Treaty School (6-12)':
            soup=get_soup(school_to_link[school],'who-we-are')
            get_contacts_from_sprdsheet(soup,'1',['2'],'3',contact_info,school)
        elif school=='Constitution High School':
            soup=get_soup(school_to_link[school],'staff')
            get_contacts_from_sprdsheet(soup,'1',['2'],'3',contact_info,school)
        elif school=='Roxborough High School':
            soup=get_soup(school_to_link[school],'support-team')
            h3_tags = soup.find_all('h3')
            num_tags=len(h3_tags)
            for i in range(0,num_tags,2):
                if i+1<num_tags:
                    contact_info[school][h3_tags[i].text]=h3_tags[i+1].text
        if school=='South Philadelphia High School':
            soup=get_soup(school_to_link[school],'counselor')
            p_tags=soup.find_all('p')
            i = 0
            num_p_tags=len(p_tags)
            while i<num_p_tags:
                tag_txt = p_tags[i].text
                if 'Counselor' in tag_txt:
                    name = tag_txt
                    name = name[:name.find('(')-1]
                    i+=1
                    a_tag = p_tags[i].find('a')
                    if not a_tag:
                        i+=1
                        tag_txt=p_tags[i].text
                        contact_info[school][name]=tag_txt[tag_txt.find(':')+2:]
                i+=1
        elif school=='George Washington High School':
            soup=get_soup(school_to_link[school],'support-team')
            p_tags=soup.find_all('p',attrs={'style':'text-align: center'})
            for i in range(1,len(p_tags)):
                tag_txt=p_tags[i].text
                if 'Counsel' in tag_txt:
                    a_tag = p_tags[i].find('a')
                    if  a_tag:
                        contact_info[school][tag_txt[:tag_txt.find('\n')]]=a_tag.text.strip('\xa0')
        elif school=='Bodine International Affairs':
            soup=get_soup(school_to_link[school],'faculty-staff')
            li_tags=soup.find_all('li',attrs={'class':None,'id':None})
            for tag in li_tags:
                tag_txt=tag.text
                if 'Counselor' in tag_txt or 'Special Ed' in tag_txt:
                    contact_info[school][tag_txt[:tag_txt.find(',')]]=tag_txt[tag_txt.rfind(',')+2:]
        elif school=='CAPA':
            soup=get_soup(school_to_link[school],'counselor-page')
            a_tags = soup.find_all('a',attrs={'href':re.compile('([A-Za-z])@philasd.org')})
            for tag in a_tags:
                tag_txt=tag.text
                name = tag_txt[6:]
                dot_ind = name.find('.')
                name = name[0]+name[1:dot_ind+2].lower()+name[dot_ind+2]+name[dot_ind+3:].lower()
                contact_info[school][name]=tag.get('href')
        elif school=='Central High School':
            soup=get_soup(school_to_link[school],'parents-2/counselors/')
            td_tags=soup.find_all('td',attrs={'style':'text-align: center'})
            for i in range(3,len(td_tags),2):
                tag_txt=td_tags[i].text
                #' x' should be a valid cutoff for the name assuming names start with a capital letter (i.e. Xavier)
                contact_info[school][tag_txt[:tag_txt.find(' x')]]=tag_txt[tag_txt.find('/')+2:]
        elif school == 'GAMP':
            soup=get_soup(school_to_link[school],'counselors-corner')
            p_tags=soup.find_all('p')
            for tag in p_tags:
                tag_txt = tag.text
                if '@' in tag_txt:
                    #long dash is used not short dash
                    contact_info[school][tag_txt[4:tag_txt.find('–')-1]]=tag_txt[tag_txt.find('–')+2:]
        elif school in ['Hill-Freedman World Academy High School','The LINC']:
            soup=get_soup(school_to_link[school],'parents/faculty-staff')
            get_contacts_from_sprdsheet(soup,'2','1','3',contact_info,school)
        elif school=='Kensington Health Sciences Academy High School':
            soup=get_soup(school_to_link[school],'counseling')
            tags = soup.find_all(re.compile('th|td'),attrs={'class':re.compile('column-\d|^$')})
            for tag in tags:
                tag_txt = tag.text
                begin_ind = tag_txt.find('\n')
                if begin_ind!=-1:
                    end_ind = tag_txt.find('\n',begin_ind+1)
                    job_str = tag_txt[begin_ind:end_ind]
                    if 'Counselor' in job_str or 'Special Ed' in job_str:
                        contact_info[school][tag.find('u').text.strip(' ')]=tag.find('a').text.strip(' ')
        elif school=='Parkway Northwest High School':
            soup=get_soup(school_to_link[school],'counselor-corner')
            info_btn = soup.find('a',attrs={'class':'vc_general vc_btn3 vc_btn3-size-md vc_btn3-shape-rounded vc_btn3-style-modern vc_btn3-color-sandy-brown'})
            contact_info[school][info_btn.text[:info_btn.text.find('-')]]=info_btn.get('href').strip('mailto:')
        elif school in 'Science Leadership Academy':
            soup=get_soup(school_to_link[school],'faculty')
            get_contacts_from_p_tags(soup,contact_info,school)
        elif school in ['Science Leadership Academy at Beeber (6-12)','The Crefeld School']:
            soup=get_soup(school_to_link[school],'faculty-and-staff')
            get_contacts_from_p_tags(soup,contact_info,school)
        elif school=='Murrell Dobbins Vocational School':
            soup=get_soup(school_to_link[school],'about-us/staff-list')
            p_tags=soup.find_all('p')
            i = 0
            num_p_tags=len(p_tags)
            while i<num_p_tags:
                tag_txt = p_tags[i].text
                name = tag_txt
                i+=1
                a_tag = p_tags[i].find('a')
                if not a_tag:
                    i+=1
                    tag_txt=p_tags[i].text
                    if 'Counsel' in p_tags[i-1].text or 'Special Ed' in p_tags[i-1].text or 'SPED' in p_tags[i-1].text:
                        contact_info[school][name]=p_tags[i].find('a').text
                i+=1
        elif school=='Philadelphia Military Academy':
            soup=get_soup(school_to_link[school],'staff')
            get_contacts_from_sprdsheet(soup,'2','1','3',contact_info,school)
        elif school=='Kensington Creative & Performing Arts High School':
            soup=get_soup(school_to_link[school],'staff')
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
        elif school=='Jules E. Mastbaum Technical High School':
            soup=get_soup(school_to_link[school],'contact-us')
            get_contacts_from_sprdsheet(soup,'2','3','4',contact_info,school)
        elif school=='High School of the Future':
            soup=get_soup(school_to_link[school],'staff')
            get_contacts_from_sprdsheet(soup,'3',['1','2'],'4',contact_info,school)
        elif school=='Randolph Technical High School':
            soup=get_soup(school_to_link[school],'about-us/staff')
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
        if school=='Swenson Arts and Technology High School':
            soup=get_soup(school_to_link[school],'counselors-corner')
            get_contacts_from_ul_tags(soup,school,'4',contact_info)
        elif school=='New Foundations Charter School':
            soup=get_soup(school_to_link[school],'counseling')
            div_tags=soup.find_all('div',attrs={'class':'col-12 col-md-6 vw-team-item-wrap text-center'})
            for tag in div_tags:
                tag_txt=tag.text
                if 'Counselor' in tag_txt and 'Grade' not in tag_txt:
                    contact_info[school][tag.find('h5').text]=tag.find('a').get('href').strip('mailto:')
        elif school=='Philadelphia Performing Arts Charter School':
            soup=get_soup(school_to_link[school],'our-families/support-services')
            p_tags = soup.find_all('p')
            for tag in p_tags:
                tag_txt=tag.text
                #manual function to check for grade
                if is_hs_staff(tag_txt) and ('Counselor' in tag_txt or 'Special Ed' in tag_txt):
                    strong_txt = tag.find('strong').text
                    lines = tag_txt.split('\n')
                    contact_info[school][strong_txt[:strong_txt.find('\n')].replace('\xa0',' ')]=lines[-1]
        elif school=='Springside Chestnut Hill Academy':
            soup=get_soup(school_to_link[school],'support')
            h3_tags=soup.find_all('h3')
            a_tags=soup.find_all('a',string=re.compile('([A-Za-z])*@([A-Za-z0-9])*.org'))
            i = 0
            while i < len(h3_tags):
                h3_txt = h3_tags[i].text
                if 'Upper School' in h3_txt:
                    contact_info[school][h3_txt[:h3_txt.find(',')]]=a_tags[i].text
                i+=1
        elif school=='Archbishop Ryan High School':
            soup=get_soup(school_to_link[school],'apps/staff/')
            get_contacts_from_name_pos_class_div_tags(soup,contact_info,school)
        elif school=='Father Judge High School':
            soup=get_soup(school_to_link[school],'apps/staff/')
            get_contacts_from_name_pos_class_div_tags(soup,contact_info,school)
        elif school=='St. Hubert Catholic High School for Girls':
            soup=get_soup(school_to_link[school],'apps/staff/')
            get_contacts_from_name_pos_class_div_tags(soup,contact_info,school)
        elif school=='Mastery Charter Schools (Gratz, Lenfest, Pickett, Shoemaker, Thomas, Hardy Williams)':
            #Mastery Charter has several schools to account for programmatically with the same structure
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
                campus_name+=' Mastery Charter School Campus'
                contact_info[campus_name]=dict()
                temp_req = requests.get(tag.get('href'))
                soup = BeautifulSoup(temp_req.text,'html.parser')
                get_contacts_from_sprdsheet(soup,'3',['1','2'],'4',contact_info,campus_name)
        elif school=='Mariana Bracetti Academy Charter School':
            soup=get_soup(school_to_link[school],'our-team')
            div_tags = soup.find_all('div',attrs={'class':re.compile('__column$')})[2:]
            for tag in div_tags:
                tag_txt=tag.text
                if 'Special Ed' in tag_txt:
                    a_tag = tag.find('a')
                    contact_info[school][a_tag.text]=a_tag.get('href').strip('mailto:')
        elif school=='Freire Charter School':
            soup=get_soup(school_to_link[school],'staff-directory/')
            div_tags=soup.find_all('div',attrs={'class':'wp-block-genesis-blocks-gb-column gb-block-layout-column gb-is-vertically-aligned-center'})
            for tag in div_tags:
                job_txt = tag.find('p',attrs={'class':None}).text
                if 'Support Service' in job_txt or 'Psychologist' in job_txt:
                    contact_info[school][tag.find('p').text]=tag.find('a').text

    return contact_info

def write_to_excel_file(contact_info:dict,county:str,file_name:str):
    """
    Writes the content of contact_info to an Excel file 
    @param contact_info : dictionary mapping school name indicated by school to a dictionary mapping school staff member name to email
    @param county
    @param file_name
    """
    wb = openpyxl.Workbook()
    sheet = wb.active
    sheet.title = county
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

print(get_phila_county_contacts())
#write_to_excel_file(get_psd_contact_info(),'Philadelphia School District','counselor_contacts.xlsx')
#get_PA_hs_links('Pittsburgh')
#get_PA_hs_links()