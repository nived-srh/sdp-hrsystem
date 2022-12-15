from .models import *

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
        print( row.view_url , "######", viewUrl, "######", row.view_url in viewUrl)
        if row.view_url == "/" and row.view_url == viewUrl:
            return True
        elif row.view_url in viewUrl and row.view_url != "/":
            print( row.view_url , "######", viewUrl)
            return True
    return False     

def changePassword(db, formData):    
    pass
       