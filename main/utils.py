from .models import *
from .config import AppConfig
import re


def fetchSidebarLinks(db, username):    
    viewData = {}
    if username != None:
        results = access.ProfileAccess().fetchProfileAccessByUsername(db, username=username, viewType="PAGE")
    else:
        results = access.View().fetchViews(db, queryParams="view_group = \'PUBLIC\'")
        
    for row in results:
        if row.view_group not in viewData:
            viewData[row.view_group] = []
        viewData[row.view_group].append(row)
    
    return viewData 

def fetchSearchableViews(db, username):    
    return access.ProfileAccess().fetchProfileAccessByUsername(db, username)
    
def validateUserAccess(db, username, viewUrl, action=None):    
    if username != None:
        results = access.ProfileAccess().fetchProfileAccessByUsername(db, username, True)
    else:
        results = access.View().fetchViews(db, queryParams="view_group = \'PUBLIC\'")
        
    for row in results:
        if row.view_url == "/" and row.view_url == viewUrl:
            return True
        elif row.view_url in viewUrl and row.view_url != "/":
            return True
    return False     

def changePassword(db, formData):    
    pass

def validateFormData(formData):
    errors = []
    if "email" in formData:
        if not regexCheck(formData["email"], AppConfig.REGEX["EMAIL"]):
            errors.append("- Invalid email address.")
    
    if "password" in formData:
        if not regexCheck(formData["password"], AppConfig.REGEX["PASSWORD"]):
            errors.append("- Password should be a minimum of 8 characters long and contain atleast one each of number, uppercase and special character.")

    if "newpassword" in formData and "newpasswordrepeat" in formData :
        if formData["newpassword"] != formData["newpasswordrepeat"]:
            errors.append("- New passowrds entered do not match.")

        if not regexCheck(formData["newpassword"], AppConfig.REGEX["PASSWORD"]):
            errors.append("- Password should be a minimum of 8 characters long and contain atleast one each of number, uppercase and special character.")

    if "date_of_birth" in formData:
        pass

    print("ERROR", errors)
    return "SUCCESS" if errors == [] else "ERROR: Please correct the below errors before submitting the form.<br/>" + '<br/>'.join([ item for item in errors])

def regexCheck( value, pattern):    
    regexString = r''+ pattern
    print("asdasdasd", regexString)
    if re.fullmatch(regexString, value):
        return True
    return False 