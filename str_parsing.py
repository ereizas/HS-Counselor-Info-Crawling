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
    while not txt[i].isnumeric():
        i+=1
    while i<len(txt) and txt[i].isnumeric():
        grade+=txt[i]
        i+=1
    if grade=='K':
        return False
    grade = int(grade)
    return grade>8

def get_char_ind(s:str,char:str,index_reduction:int=0):
    """
    Retrieves the index of the specified character in the string or the length of the string if it does not appear in the string for index slicing purposes
    @param s : the string to search for char in
    @param char : the character to search for
    @param index_reduction : if char is not found in s, then this is used to scale down the index used
    @return char_ind : index of the character or length of string if it does not appear in the string
    """
    char_ind = s.find(',')
    if char_ind==-1:
        char_ind = len(s) - index_reduction
    return char_ind