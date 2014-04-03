from django.conf.urls import patterns, url, include
from rest_framework.urlpatterns import format_suffix_patterns
from api import views


urlpatterns = patterns('api.views',
	url(r'^$', 'api_root'),
	url(r'^sounds/$', views.SoundList.as_view(),
		name='sound-list'),
	url(r'^sounds/(?P<pk>[0-9]+)/$', views.SoundDetail.as_view(),
		name='sound-detail'),
	url(r'^annotations/$', views.AnnotationList.as_view(),
		name='annotation-list'),
	url(r'^annotations/(?P<pk>[0-9]+)/$', views.AnnotationDetail.as_view(),
		name='annotation-detail'),
	url(r'^users/$', views.UserList.as_view(),
		name='user-list'),
	url(r'^users/(?P<pk>[0-9]+)/$', views.UserDetail.as_view(),
		name='user-detail'),
	url(r'^playlists/$', views.PlaylistList.as_view(),
		name='playlist-list'),
	url(r'^playlists/(?P<pk>[0-9]+)/$', views.PlaylistDetail.as_view(),
		name='playlist-detail'),
	url(r'^playlist_types/$', views.PlaylistTypeList.as_view(),
		name='playlist-type-list'),
	url(r'^lessons/$', views.LessonList.as_view(),
		name='lesson-list'),
	url(r'^lessons/(?P<pk>[0-9]+)/$', views.LessonDetail.as_view(),
		name='lesson-detail'),
	url(r'^truth/$', views.GroundTruthList.as_view(),
		name='groundtruth-list'),
	url(r'^truth/(?P<pk>[0-9]+)/$', views.GroundTruthDetail.as_view(),
		name='groundtruth-detail'),
	url(r'^species/$', views.SpeciesList.as_view(),
		name='species-list'),
	url(r'^species/(?P<pk>[0-9]+)/$', views.SpeciesDetail.as_view(),
		name='species-detail'),
)

urlpatterns = format_suffix_patterns(urlpatterns)

urlpatterns += patterns('',
	url(r'^api-auth/', include('rest_framework.urls',
								namespace='rest_framework')),
)
