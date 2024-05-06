from django.contrib import admin
from . models import UserDetails,UserPosts,PostComment,Follow,Bookmark,Contact,Notification

# Register your models here.
admin.site.register(UserDetails)
admin.site.register(UserPosts)
admin.site.register(PostComment)
admin.site.register(Follow)
admin.site.register(Bookmark)

admin.site.register(Notification)
admin.site.register(Contact)