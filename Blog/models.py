from django.db import models

from django.db import models
from django.contrib.auth.models import User







class Follow(models.Model):
    follower = models.ForeignKey(User, related_name='following', on_delete=models.CASCADE)
    followed = models.ForeignKey(User, related_name='followers', on_delete=models.CASCADE)

class UserDetails(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    fcount=models.IntegerField(default=0)
    xp= models.IntegerField(default=0)
    badge = models.CharField(max_length=10, default="bronze")
    nickname = models.CharField(max_length=50)
    about = models.CharField(max_length=300, default="your description is empty,go to edit profile to add")
    image = models.ImageField(upload_to='Blog/profile_images/', null=True, blank=True)
    GENDER_CHOICES = [
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Other', 'Other'),
    ]
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    followers = models.ManyToManyField(User, related_name='user_followers')
    following = models.ManyToManyField(User, related_name='user_following')

    def save(self, *args, **kwargs):
        followers_count = self.user.followers.count()
        self.fcount=followers_count
        total_views = 0
        total_posts = 0

        myposts = UserPosts.objects.filter(author=self.user)
        for post in myposts:
            total_posts += 1
            total_views += post.views_count

        if followers_count >= 200 and total_posts >=40 and total_views >=500:
            self.badge = 'master'
        elif 100 <= self.xp < 400:
            self.badge = 'silver'
        elif 400 <= self.xp < 1000:
            self.badge = 'gold'
        elif 1000 <= self.xp < 3000:
            self.badge = 'platin'
        elif self.xp >= 3000:
            self.badge = 'diamond'
        else:
            self.badge = 'bronze'
        super(UserDetails, self).save(*args, **kwargs)

class Contact(models.Model):
    content = models.TextField()
    subject = models.CharField(max_length=200)
    time = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=50)
    email=models.CharField(max_length=30)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

# Create a model for user posts
class UserPosts(models.Model):
    post_id = models.AutoField(primary_key=True)
    category = models.CharField(max_length=100)
    title = models.CharField(max_length=200)
    content = models.TextField()
    image = models.ImageField(upload_to='Blog/post_images/', null=True, blank=True)
    post_time = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    author_details = models.ForeignKey(UserDetails, on_delete=models.SET_NULL, null=True, blank=True)
    views_count=models.IntegerField(default=0)
    comment_count=models.IntegerField(default=0)

    def get_author_nickname(self):
        return self.author.userdetails.nickname

class Bookmark(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(UserPosts, on_delete=models.CASCADE)


class Notification(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE,related_name='sent_notifications')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE,related_name='received_notifications')
    time = models.DateTimeField(auto_now_add=True)
    message = models.CharField(max_length=100)
    isread = models.BooleanField(default=False)
class PostComment(models.Model):
    comment_id= models.AutoField(primary_key=True)
    like_count = models.IntegerField(default=0)
    comment=models.TextField()
    userinfo=models.ForeignKey(UserDetails, on_delete=models.CASCADE)
    post=models.ForeignKey(UserPosts, on_delete=models.CASCADE)
    parent=models.ForeignKey('self',on_delete=models.CASCADE, null=True )
    comment_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.post.title + " by " + self.userinfo.user.username