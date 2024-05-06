
from . import views
from django.contrib import admin
from django.urls import include,path


urlpatterns = [
  path('',views.Blog,name='index'),
path('most_viewed_posts/',views.most_viewed_posts, name='most_viewed_posts'),
    path('newest_posts/',views.newest_posts, name='newest_posts'),
    path('all_posts/',views.all_posts, name='all_posts'),
    path('status/', views.status, name='status'),
    path('search/', views.search, name='search'),
path('memes/', views.memes_view, name='memes'),
    path('leaderboard/', views.leaderboard, name='leaderboard'),
path('flist/', views.flist, name='flist'),
    path('notification/', views.notification, name='notification'),
path('fav/',views.fav,name='fav'),
path('following_posts/', views.following_posts, name='following_posts'),
    path('follow/<int:user_id>/', views.follow, name='follow'),
    path('unfollow/<int:user_id>/', views.unfollow, name='unfollow'),
path('login/',views.login_view,name='login'),
path('register/',views.register_view,name='register'),
path('addpost/',views.addpost,name='addpost'),

path('contact/',views.contact,name='contact'),
path('about/',views.about,name='about'),
path('editpost/<int:post_idn>/',views.editpost,name='editpost'),

path('editprofile/',views.editprofile,name='editprofile'),
path('profile/', views.profile_view, name='profile'),
path('userprofile/<int:user_id>/', views.userprofile_view, name='userprofile'),
path('logout/', views.logout_view, name='logout'),
path('literature/', views.literature_view, name='literature'),
path('search_view/', views.search_view, name='search_view'),
path('technology/', views.technology_view, name='technology'),
path('history/', views.history_view, name='history'),
path('educationandlearning/', views.educationandlearning, name='educationandlearning'),
path('mythology/', views.mythology_view, name='mythology'),
path('science/', views.science_view, name='science'),
path('gameshandsports/', views.gamesandsports_view, name='gamesandsports'),
path('foodandtravel/', views.foodandtravel_view, name='foodandtravel'),
path('artandculture/', views.artandculture_view, name='artandculture'),
path('others/', views.others_view, name='others'),
path('literaturesearch/', views.literaturesearch, name='literaturesearch'),
path('technologysearch/', views.technologysearch, name='technologysearch'),
path('historysearch/', views.historysearch, name='historysearch'),
path('educationandlearningsearch/', views.educationandlearningsearch, name='educationandlearningsearch'),
path('mythologysearch/', views.mythologysearch, name='mythologysearch'),
path('sciencesearch/', views.sciencesearch, name='sciencesearch'),
path('gameshandsportssearch/', views.gamesandsportssearch, name='gamesandsportssearch'),
path('foodandtravelsearch/', views.foodandtravelsearch, name='foodandtravelsearch'),
path('artandculturesearch/', views.artandculturesearch, name='artandculturesearch'),
path('otherssearch/', views.otherssearch, name='otherssearch'),
path('clickedpost/<int:post_idn>/', views.clicked_post, name='clickedpost'),
path('home/',views.home,name='home')
]
