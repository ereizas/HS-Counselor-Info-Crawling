from googlesearch import search
import requests

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

def print_couns_page_url(school_to_link,school):
    """
    Prints a potential counselor page url
    """
    req = None
    suffs = ['counselors-corner','counselor-corner','faculty-staff','counselor','counselors','support-team','counseling','staff','faculty',
            'contact-us','staff-directory','about/staff','high-school-support-services/','apps/staff/','our-team','staff/hs-faculty/',
            'our-families/support-services','families/staff-directory/','support','faculty-and-staff','about/facultystaffdirectory',
            'who-we-are/meet-our-educators','discover/facultystaff','about/faculty']
    for suff in suffs:
        test_req=requests.get(school_to_link[school]+suff)
        if test_req.status_code>=200 and test_req.status_code<300:
            print(test_req.url)
            req=test_req
            break
    if not req:
        link=google_search('counselor site:'+school_to_link[school])
        if link:
            print(link)
            req=requests.get(link)