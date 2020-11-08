from django.conf.urls import url

from hero import views

app_name = 'hero'

urlpatterns = [
    url(r'^send-message$', views.send_message, name='contact'),
    url(r'^$', views.HeroView.as_view(), name='home')
]
