from django.conf.urls.defaults import patterns,  url

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'jsb.views.home', name='home'),
    # url(r'^jsb/', include('jsb.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
    url(r'^show/', 'jsb.generator.views.showform'),
    url(r'^$', 'jsb.generator.views.showform'),
)
