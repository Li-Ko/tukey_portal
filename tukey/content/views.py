import re, os
import mimetypes
from django.core.servers.basehttp import FileWrapper
from tukey.content.models import Page
from django.conf import settings
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.template import RequestContext
from django.utils.safestring import mark_safe
from horizon.decorators import require_auth, require_perms
from django.utils.http import urlencode
from .forms import PageForm

def page(request, slug=''):
    #slug can either be blank or contain \w and -, safe because from urls.py regex
    p = get_object_or_404(Page, pk=slug)
    nav_pages = Page.objects.order_by('nav_order')
    template = os.path.abspath(os.path.join(settings.ROOT_PATH, '..', 'tukey/templates/page.html'))
    return render(request, 'content/page.html', {'content' : p, 'nav_pages' : nav_pages})


def gnos(request):
    user=request.META.get(settings.SHIB_HEADERS[0]).split("!")[-1]
    if user=='':
        return redirect('https://itrusteauth.nih.gov/affwebservices/public/saml2sso?SPID=https://bionimbus-pdc.opensciencedatacloud.org/shibboleth&TARGET=https://bionimbus-pdc.opensciencedatacloud.org/gnos')
    else:
        return render(request,'content/gnos.html',{'user':user,'authenticated':is_authenticated(user)})



def gnos_key(request):
    user=request.META.get(settings.SHIB_HEADERS[0]).split("!")[-1]
    user='allisonheath'
    if user!='':
        if is_authenticated(user):
            os.system("/var/www/tukey/sync.sh keygen "+user)
            the_file='/gtrepo/'+user+'/gtorrent.pem'
            filename=os.path.basename(the_file)
            response=HttpResponse(FileWrapper(open(the_file)),content_type="application/x-pem-file")
            response['Content-Length'] = os.path.getsize(the_file)
            response['Content-Disposition'] = "attachment; filename=%s" % user+"_"+filename
            return response
    return HttpResponse(status=204)

def is_authenticated(user):
    user='allisonheath'
    result=True
    for filename in settings.GNOS_CHECK_LIST:
        authenticated=False
        with open(filename,'rb') as csvfile:
            lines=csvfile.readlines()
            for line in lines:
                row=re.split(",\s*",line)
                if len(row)>0:
                    print row[-3]
                if len(row)>0 and row[1] not in ['email','login']  and row[1].upper()==user.upper():
                    authenticated=True
        if authenticated==False:
            result=False
    return result


@require_auth
def content_admin(request):
    if request.user.has_perm("openstack.roles.tukeycontentadmin"):
        pages = Page.objects.order_by('slug')
        content_pages = []
        non_content_pages = []
        for page in pages:
            #hackity hack hack
            if page.content == '':
                non_content_pages.append(page)
            else:
                content_pages.append(page)

        return render(request, 'content/admin.html', {'content_pages' : content_pages,
            'non_content_pages' : non_content_pages})
    else:
        return HttpResponseRedirect("/")

def page_edit(request, slug=''):
    page = get_object_or_404(Page, pk=slug)

    if request.method == 'POST':
        form = PageForm(request.POST, instance=page)
        if form.is_valid():
            form.save()
            return redirect("/content-admin")
    else:
        form = PageForm(instance=page) # An unbound form

    return render(request, 'content/edit.html', {
        'form': form,
        'page': page,
    })

def page_add(request):
    if request.method == 'POST':
        form = PageForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("/content-admin")
    else:
        form = PageForm() # An unbound form

    return render(request, 'content/add.html', {
        'form': form,
    })

def page_delete(request, slug='', confirm=None):
    page = get_object_or_404(Page, pk=slug)
    if not confirm:
        return render(request, 'content/delete.html', {'page' : page})
    if confirm == "YES":
        page.delete()
        return redirect("/content-admin")


def rss_page(request):
    return render(request, 'content/news.html', {'rss_category': None})

