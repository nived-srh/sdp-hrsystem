from .models import *

def fetchSidebarLinks(db, username):    
    results = access.ProfileAccess().fetchProfileAccessByUsername(db, username)
    viewData = {}
    for row in results:
        if row.view_group not in viewData:
            viewData[row.view_group] = []
        if row.allow_read:
            viewData[row.view_group].append(row)
    return viewData 
    
def validateUserAccess(db, username, view, action):    
    results = access.ProfileAccess().fetchProfileAccessByUsername(db, username, True)
    for row in results:
        if row.view_name == view.view_name:
            return True
    return False     