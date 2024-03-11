from bs4 import BeautifulSoup
import re
from str_parsing import get_char_ind
import requests

def get_soup(url:str,suff:str=''):
    """
    Makes the request and returns the corresponding BeautifulSoup object
    @param url : base link for the school
    @param suff : suffix which leads to counselor or staff page for the school
    """
    req=requests.get(url+suff)
    return BeautifulSoup(req.text,'html.parser')

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
        comma_ind = get_char_ind(header_txt,',')
        colon_ind = get_char_ind(header_txt,':')
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

def get_contacts_from_staff_info_blocks(school_to_link,school,job_keywords,contact_info):
    i=1
    div_tags=1
    while div_tags:
        soup=get_soup(school_to_link[school],'/staff?page_no='+str(i))
        div_tags=soup.find_all('div',attrs={'class':'staff-info'})
        for tag in div_tags:
            title = tag.find('div',attrs={'class':'title'}).text
            if any([keyword in title for keyword in job_keywords]):
                contact_info[school][tag.find('div',attrs={'class':'name'}).text.strip('\n ')]=tag.find('a').text.strip('\n ')
        i+=1