from django.conf.urls.defaults import patterns, include, url
from django.conf import settings

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'jsb.views.home', name='home'),
    # url(r'^jsb/', include('jsb.foo.urls')),

    url(r'^generator/', 'jsb.generator.views.step1'),     #showing form
    url(r'^step1/', 'jsb.generator.views.step1'),     #showing form -step 1
    url(r'^step2/', 'jsb.generator.views.step2'),     #showing form -step 2
    url(r'^step3/', 'jsb.generator.views.step3'),     #showing form -step 2
    url(r'^gen_out/', 'jsb.generator.views.genout'),     #showing form
    # Uncomment the admin/doc line below to enable admin documentation:
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),

    url(r'^$', 'jsb.generator.views.step1'),
)




if settings.DEBUG:
    urlpatterns += patterns('',
        url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {
            'document_root': settings.MEDIA_ROOT,
        }),
   )