import os, mimetypes,re
from django.core.servers.basehttp import FileWrapper
def is_authenticated(user):
    result=True
    authenticated=False
    for filename in ['/var/www/tukey/eralocal/localdown.csv','/var/www/tukey/eralocal/ncbi.csv','/var/www/tukey/eralocal/localup.csv']:
        with open(filename,'rb') as csvfile:
            lines=csvfile.readlines()
            for line in lines:
                row=re.split(",\s*",line)
                if len(row)>0:
                    print row[1]
                if len(row)>0 and row[1]!='email' and row[1].upper()==user.upper():
                    authenticated=True
        if authenticated==False:
            result=False
    return result


