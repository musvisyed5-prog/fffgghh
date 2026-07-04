from django.contrib import admin
from django.conf.urls.i18n import set_language
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView


from src.views import ( 
    HomView,
    DashboardView
)


urlpatterns = [
    path('admin/', admin.site.urls),
    path("i18n/setlang/", set_language, name="set_language"),
    path('account/', include('allauth.urls')),
    path('account/', include('core.urls', namespace='core')),
    path('', include('portfolio.urls', namespace='portfolio')),

    path('ai/', include('src.services.urls', namespace='ai')),
    path('company/', include('company.urls', namespace='company')),   
    path('jobs/', include('job.urls', namespace='job')),
    path('messages/', include('message.urls', namespace='message')),
    path('', HomView.as_view(template_name='pages/home.html'), name='home'),
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    path('login/',
        TemplateView.as_view(template_name='pages/login_choose.html'),
        name="login-choose"
    ),
    path(
        'choose-role/', 
        TemplateView.as_view(template_name='pages/choose_role.html'),
        name='choose-role'
    ),
    path(
        'i-am-a-company/', 
        TemplateView.as_view(template_name='pages/i_am_a_company.html'),
        name='i_am_a_company'
    ),
    path('about/', TemplateView.as_view(template_name='doc/about.html'), name='about'),
    path('contact/', TemplateView.as_view(template_name='doc/contact.html'), name='contact'),
    path('privacy/', TemplateView.as_view(template_name='doc/privacy.html'), name='privacy'),
    path('terms/', TemplateView.as_view(template_name='doc/terms.html'), name='terms'),
]

if settings.DEBUG:
    from debug_toolbar.toolbar import debug_toolbar_urls
    
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += debug_toolbar_urls()
