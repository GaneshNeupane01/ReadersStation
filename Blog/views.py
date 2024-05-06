from django.core.files import File
from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from django.contrib.auth.models import User
from .models import UserDetails,PostComment,Follow,Bookmark
from .models import UserPosts
from django.db.models import Count
from django.shortcuts import  HttpResponse
from django.http import JsonResponse
from .models import Bookmark, Notification,Contact
from django.core.paginator import Paginator
from django.views.decorators.csrf import csrf_exempt
from random import shuffle


def notification(request):
    if request.user.is_authenticated:
        notifications = Notification.objects.filter(receiver=request.user,isread=True).order_by('-time')
        unotifications = Notification.objects.filter(receiver=request.user, isread=False).order_by('-time')
        for n in unotifications:
            n.isread = True
            n.save()
    else:
        notifications=None
        unotifications = None

    return render(request,'notification.html',{'notifications':notifications,'unotifications':unotifications})
@login_required
def flist(request):
    if request.user.is_authenticated:
        followers = UserDetails.objects.filter(following=request.user)
        following = UserDetails.objects.filter(followers=request.user)
    else:
        followers=None
        following=None

    followinglist = [u.user.pk for u in following]
    return render(request,'flist.html',{'followers':followers,'following':following,'followinglist':followinglist})
def leaderboard(request):
    onxp = UserDetails.objects.all().order_by('-xp')
    onf = UserDetails.objects.annotate(followers_count=Count('followers'))
    # Order the UserDetails objects by followers count in descending order
    onf = onf.order_by('-followers_count')
    return render(request,'leaderboard.html',{'onxp':onxp,'onf':onf})
@login_required
def status(request):
    bronze=False
    silver=False
    gold=False
    platin=False
    diamond=False
    master=False

    tenpost=False
    tenfollower=False
    hunviews=False
    twohunviews=False
    twentypost=False
    fivtyfollower=False
    txp = UserDetails.objects.get(user=request.user).xp
    sreq = 100 - txp
    greq = 400 - txp
    preq = 1000 - txp
    dreq = 3000 - txp
    total_views = 0
    total_posts = 0
    userinfo = UserDetails.objects.get(user=request.user)
    myposts = UserPosts.objects.filter(author=request.user)
    for post in myposts:
        total_posts += 1
        total_views += post.views_count
    # You can access user attributes like username, email, etc.
    followers_count = request.user.followers.count()
    if tenpost == False:
        if total_posts >= 10:
            tenpost=True
    if tenfollower == False:
        if followers_count >= 10:
            tenfollower=True
    if hunviews == False:
        if total_views >= 100:
            hunviews=True
    if twentypost == False:
        if total_posts >= 20:
            twentypost=True
    if twohunviews == False:
        if total_views >= 200:
            twohunviews=True
    if fivtyfollower == False:
        if followers_count >= 50:
            fivtyfollower=True
    spercent = round((txp / 100) *100 ,1)
    gpercent = round((txp / 400) * 100,1)
    ppercent = round((txp / 1000) * 100,1)
    dpercent = round((txp / 3000) * 100,1)
    if txp>=100 and txp<400:
        silver=True
        spercent=100
        
    elif txp>=400 and txp<1000:
        gold=True
        gpercent=100
        
    elif txp>=1000 and txp<3000:
        platin=True
        ppercent=100
        
    elif txp>=3000:
        diamond=True
        dpercent=100
    elif total_views >= 500 and total_posts >= 40 and followers_count >=200 :
        master=True
    else:
        bronze = True
        percent = (txp / 100) * 100
    if request.user.is_authenticated:
        userinfo = UserDetails.objects.get(user=request.user)
    else:
        userinfo = None
    return render(request,'status.html',{'tenpost':tenpost,'userinfo':userinfo,'twentypost':twentypost,'tenfollower':tenfollower,'fivtyfollower':fivtyfollower,'hunviews':hunviews,'twohunviews':twohunviews,'bronze':bronze,'sreq':sreq,'greq':greq,'preq':preq,'dreq':dreq,'txp':txp,'silver':silver,'gold':gold,'platin':platin,'diamond':diamond,'master':master,'followers_count':followers_count,'total_posts':total_posts,'total_views':total_views,'spercent':spercent,'gpercent':gpercent,'ppercent':ppercent,'dpercent':dpercent})
@login_required
def fav(request):
    if request.method == 'POST' and request.user.is_authenticated:
        user = request.user

        post_id = request.POST.get('post_id')
        post = UserPosts.objects.get(pk=post_id)

        # Check if the user already bookmarked this specific post
        if Bookmark.objects.filter(user=user, post=post).exists():
            # The user already bookmarked this post, so delete it
            Bookmark.objects.filter(user=user, post=post).delete()
            return JsonResponse({'message': 'unbookmarked'})
        else:
            # The user has not bookmarked this post, so create a bookmark
            Bookmark.objects.create(user=user, post=post)
            return JsonResponse({'message': 'bookmarked'})
    posts=Bookmark.objects.filter(user=request.user)

    p=Bookmark.objects.filter(user=request.user).order_by('?')
    page = Paginator(p, 6)
    page_list = request.GET.get('page')
    page = page.get_page(page_list)
    bposts = [post.post.pk for post in posts]
    if request.user.is_authenticated:
        uncount = Notification.objects.filter(receiver=request.user, isread=False).count()

    else:

        uncount = 0
    if request.user.is_authenticated:
        userinfo = UserDetails.objects.get(user=request.user)
    else:
        userinfo = None
    # Return an error response for other cases
    return render(request,'bookmarked.html',{'posts': page,'bposts':bposts,'uncount':uncount,'userinfo':userinfo})
def search(request):
    if request.user.is_authenticated:
        userinfo = UserDetails.objects.get(user=request.user)
    else:
        userinfo = None
    return render(request,'search.html',{'userinfo':userinfo})


def clicked_post(request, post_idn):
    post = get_object_or_404(UserPosts, pk=post_idn)

    xp=UserDetails.objects.get(user=post.author).xp
    authposts=UserPosts.objects.filter(author=post.author)
    total_views = 0

    for p in authposts:
        total_views += p.views_count
    if total_views == 100:
        xp += 100
    if total_views == 200:
        xp += 200



    if request.user !=post.author:
        post.views_count += 1  # Increment the view count of the post
        post.save()
        xp = xp + 2
        s = UserDetails.objects.get(user=post.author)
        s.xp = xp
        s.save()
    if request.user.is_authenticated:
        uxp = UserDetails.objects.get(user=request.user).xp
        userinfo = UserDetails.objects.get(user=request.user)
        if request.method == 'POST':
            if 'comment' in request.POST:
                comment = request.POST['comment']
                if comment != '':
                    usercomment = PostComment(post=post, userinfo=userinfo, comment=comment)
                    usercomment.save()
                    xp += 5
                    s = UserDetails.objects.get(user=post.author)
                    s.xp = xp
                    s.save()
                    if request.user != post.author:
                        uxp += 5
                        cs = UserDetails.objects.get(user=request.user)
                        cs.xp = uxp
                        cs.save()




            if request.user != post.author:
                nsender = request.user
                nreceiver = post.author
                message = " commented on your post " + str(post.title)
                n = Notification(sender=nsender, receiver=nreceiver, message=message)
                n.save()





    comments=PostComment.objects.filter(post=post).order_by('-comment_time')
    comment_count=0
    for pcom in comments:
        comment_count+=1
    post.comment_count=comment_count
    post.save()
    if request.user.is_authenticated:
        uncount = Notification.objects.filter(receiver=request.user, isread=False).count()

    else:

        uncount = 0
    if request.user.is_authenticated:
        userinfo = UserDetails.objects.get(user=request.user)
    else:
        userinfo = None
    return render(request, 'clickedpost.html', {'post': post,'comments':comments,'userinfo':userinfo,'uncount':uncount})
@login_required
def editpost(request, post_idn):
    cpost=UserPosts.objects.get(post_id=post_idn)
    if request.method == 'POST':
        post = get_object_or_404(UserPosts, pk=post_idn)
        title = request.POST['title']
        category = request.POST['category']
        content = request.POST['content']

        image = request.FILES.get('image')
        post.title = title
        post.category = category
        if image:
            post.image = image
        post.content = content
        post.save()
        return redirect('profile')
    if request.user == cpost.author:
        return render(request, 'editpost.html', {'currentpost': cpost})
    else:
        return HttpResponse('''error''')


@login_required
def editprofile(request):
    if request.method == 'POST':
        about=request.POST['about']
        nickname=request.POST['nickname']
        uname=request.POST['username']
        gender=request.POST['gender']

        image = request.FILES.get('image')
        user=request.user
        user.username=uname
        user.save()


        userinfo = UserDetails.objects.get(user=request.user)
        if image:
            userinfo.image = image

        userinfo.about=about
        userinfo.gender=gender
        userinfo.nickname=nickname
        userinfo.save()

        return redirect('profile')
    cuser=UserDetails.objects.get(user=request.user)

    return render(request,'editprofile.html',{'cuser':cuser})
def literature_view(request):
    # Filter posts with the 'poem' category
    p = UserPosts.objects.filter(category='literature').order_by('-post_time')
    page = Paginator(p, 6)
    page_list = request.GET.get('page')
    page = page.get_page(page_list)
    if request.user.is_authenticated:
        uncount = Notification.objects.filter(receiver=request.user, isread=False).count()
        bookmarked_posts = Bookmark.objects.filter(user=request.user)
        bposts = [post.post.pk for post in bookmarked_posts]
        # Order the UserDetails objects by followers count in descending order
    else:
        bposts = None
        uncount = 0
    if request.user.is_authenticated:
        userinfo = UserDetails.objects.get(user=request.user)
    else:
        userinfo = None
    return render(request, 'literature.html', {'posts': page,'userinfo':userinfo,'bposts':bposts,'uncount':uncount})
def technology_view(request):
    # Filter posts with the 'poem' category
    p = UserPosts.objects.filter(category='technology').order_by('-post_time')
    page = Paginator(p, 6)
    page_list = request.GET.get('page')
    page = page.get_page(page_list)
    if request.user.is_authenticated:
        uncount = Notification.objects.filter(receiver=request.user, isread=False).count()
        bookmarked_posts = Bookmark.objects.filter(user=request.user)
        bposts = [post.post.pk for post in bookmarked_posts]
        # Order the UserDetails objects by followers count in descending order
    else:
        bposts = None
        uncount = 0
    if request.user.is_authenticated:
        userinfo = UserDetails.objects.get(user=request.user)
    else:
        userinfo = None
    return render(request, 'technology.html', {'posts': page,'userinfo':userinfo,'bposts':bposts,'uncount':uncount})
def history_view(request):
    # Filter posts with the 'poem' category
    p = UserPosts.objects.filter(category='history').order_by('-post_time')
    page = Paginator(p, 6)
    page_list = request.GET.get('page')
    page = page.get_page(page_list)
    if request.user.is_authenticated:
        uncount = Notification.objects.filter(receiver=request.user, isread=False).count()
        bookmarked_posts = Bookmark.objects.filter(user=request.user)
        bposts = [post.post.pk for post in bookmarked_posts]
        # Order the UserDetails objects by followers count in descending order
    else:
        bposts = None
        uncount = 0
    if request.user.is_authenticated:
        userinfo = UserDetails.objects.get(user=request.user)
    else:
        userinfo = None
    return render(request, 'history.html', {'posts': page,'userinfo':userinfo,'bposts':bposts,'uncount':uncount})
def memes_view(request):

    p = UserPosts.objects.filter(category='memes').order_by('-post_time')
    page = Paginator(p, 6)
    page_list = request.GET.get('page')
    page = page.get_page(page_list)
    if request.user.is_authenticated:
        uncount = Notification.objects.filter(receiver=request.user, isread=False).count()
        bookmarked_posts = Bookmark.objects.filter(user=request.user)
        bposts = [post.post.pk for post in bookmarked_posts]
        # Order the UserDetails objects by followers count in descending order
    else:
        bposts = None
        uncount = 0
    if request.user.is_authenticated:
        userinfo = UserDetails.objects.get(user=request.user)
    else:
        userinfo = None
    return render(request, 'memes.html', {'posts': page,'userinfo':userinfo,'bposts':bposts,'uncount':uncount})

def educationandlearning(request):
    # Filter posts with the 'poem' category
    p = UserPosts.objects.filter(category='education and learning').order_by('-post_time')
    page = Paginator(p, 6)
    page_list = request.GET.get('page')
    page = page.get_page(page_list)
    if request.user.is_authenticated:
        uncount = Notification.objects.filter(receiver=request.user, isread=False).count()
        bookmarked_posts = Bookmark.objects.filter(user=request.user)
        bposts = [post.post.pk for post in bookmarked_posts]
        # Order the UserDetails objects by followers count in descending order
    else:
        bposts = None
        uncount = 0
    if request.user.is_authenticated:
        userinfo = UserDetails.objects.get(user=request.user)
    else:
        userinfo = None
    return render(request, 'education_and_learning.html', {'posts': page,'userinfo':userinfo,'bposts':bposts,'uncount':uncount})
def mythology_view(request):
    # Filter posts with the 'poem' category
    p = UserPosts.objects.filter(category='mythology').order_by('-post_time')
    page = Paginator(p, 6)
    page_list = request.GET.get('page')
    page = page.get_page(page_list)
    if request.user.is_authenticated:
        uncount = Notification.objects.filter(receiver=request.user, isread=False).count()
        bookmarked_posts = Bookmark.objects.filter(user=request.user)
        bposts = [post.post.pk for post in bookmarked_posts]
        # Order the UserDetails objects by followers count in descending order
    else:
        bposts = None
        uncount = 0
    if request.user.is_authenticated:
        userinfo = UserDetails.objects.get(user=request.user)
    else:
        userinfo = None
    return render(request, 'mythology.html', {'posts': page,'userinfo':userinfo,'bposts':bposts,'uncount':uncount})
def science_view(request):
    # Filter posts with the 'poem' category
    p = UserPosts.objects.filter(category='science').order_by('-post_time')
    page = Paginator(p, 6)
    page_list = request.GET.get('page')
    page = page.get_page(page_list)
    if request.user.is_authenticated:
        uncount = Notification.objects.filter(receiver=request.user, isread=False).count()
        bookmarked_posts = Bookmark.objects.filter(user=request.user)
        bposts = [post.post.pk for post in bookmarked_posts]
        # Order the UserDetails objects by followers count in descending order
    else:
        bposts = None
        uncount = 0
    if request.user.is_authenticated:
        userinfo = UserDetails.objects.get(user=request.user)
    else:
        userinfo = None
    return render(request, 'science.html', {'posts': page,'userinfo':userinfo,'bposts':bposts,'uncount':uncount})
def gamesandsports_view(request):
    # Filter posts with the 'poem' category
    p = UserPosts.objects.filter(category='games and sports').order_by('-post_time')
    page = Paginator(p, 6)
    page_list = request.GET.get('page')
    page = page.get_page(page_list)
    if request.user.is_authenticated:
        uncount = Notification.objects.filter(receiver=request.user, isread=False).count()
        bookmarked_posts = Bookmark.objects.filter(user=request.user)
        bposts = [post.post.pk for post in bookmarked_posts]
        # Order the UserDetails objects by followers count in descending order
    else:
        bposts = None
        uncount = 0
    if request.user.is_authenticated:
        userinfo = UserDetails.objects.get(user=request.user)
    else:
        userinfo = None
    return render(request, 'games_and_sports.html', {'posts': page,'userinfo':userinfo,'bposts':bposts,'uncount':uncount})
def foodandtravel_view(request):
    # Filter posts with the 'poem' category
    p = UserPosts.objects.filter(category='food and travel').order_by('-post_time')
    page = Paginator(p, 6)
    page_list = request.GET.get('page')
    page = page.get_page(page_list)
    if request.user.is_authenticated:
        uncount = Notification.objects.filter(receiver=request.user, isread=False).count()
        bookmarked_posts = Bookmark.objects.filter(user=request.user)
        bposts = [post.post.pk for post in bookmarked_posts]
        # Order the UserDetails objects by followers count in descending order
    else:
        bposts = None
        uncount = 0
    if request.user.is_authenticated:
        userinfo = UserDetails.objects.get(user=request.user)
    else:
        userinfo = None
    return render(request, 'food_and_travel.html', {'posts': page,'userinfo':userinfo,'bposts':bposts,'uncount':uncount})
def artandculture_view(request):
    # Filter posts with the 'poem' category
    p = UserPosts.objects.filter(category='arts and culture').order_by('-post_time')
    page = Paginator(p, 6)
    page_list = request.GET.get('page')
    page = page.get_page(page_list)
    if request.user.is_authenticated:
        uncount = Notification.objects.filter(receiver=request.user, isread=False).count()
        bookmarked_posts = Bookmark.objects.filter(user=request.user)
        bposts = [post.post.pk for post in bookmarked_posts]
        # Order the UserDetails objects by followers count in descending order
    else:
        bposts = None
        uncount = 0
    if request.user.is_authenticated:
        userinfo = UserDetails.objects.get(user=request.user)
    else:
        userinfo = None
    return render(request, 'art_and_culture.html', {'posts': page,'userinfo':userinfo,'bposts':bposts,'uncount':uncount})
def others_view(request):
    # Filter posts with the 'poem' category
    p = UserPosts.objects.filter(category='others').order_by('-post_time')
    page = Paginator(p, 6)
    page_list = request.GET.get('page')
    page = page.get_page(page_list)
    if request.user.is_authenticated:
        uncount = Notification.objects.filter(receiver=request.user, isread=False).count()
        bookmarked_posts = Bookmark.objects.filter(user=request.user)
        bposts = [post.post.pk for post in bookmarked_posts]
        # Order the UserDetails objects by followers count in descending order
    else:
        bposts = None
        uncount = 0
    if request.user.is_authenticated:
        userinfo = UserDetails.objects.get(user=request.user)
    else:
        userinfo = None
    return render(request, 'others.html', {'posts': page,'userinfo':userinfo,'bposts':bposts,'uncount':uncount})
def search_view(request):
    if request.method == 'POST':
        search_prompt = request.POST.get('search')  # Get the search input from the form
        #  posts = UserPosts.objects.filter(category="poem").filter(   Q(title__icontains=search_prompt) | Q(author__username__icontains=search_prompt))

        # Filter posts based on the search input (title or author)
        posts = UserPosts.objects.filter(
            Q(title__icontains=search_prompt) | Q(author__username__icontains=search_prompt) | Q(
                category__icontains=search_prompt))
    else:
        posts=None
    if request.user.is_authenticated:
        uncount = Notification.objects.filter(receiver=request.user, isread=False).count()
        bookmarked_posts = Bookmark.objects.filter(user=request.user)
        bposts = [post.post.pk for post in bookmarked_posts]
        # Order the UserDetails objects by followers count in descending order
    else:
        bposts = None
        uncount = 0
    if request.user.is_authenticated:
        userinfo = UserDetails.objects.get(user=request.user)
    else:
        userinfo = None
    return render(request, 'searchresult.html', {'posts': posts,'userinfo':userinfo,'bposts':bposts,'uncount':uncount})

def literaturesearch(request):
    search_prompt = request.POST.get('search')  # Get the search input from the form
    if request.user.is_authenticated:
        uncount = Notification.objects.filter(receiver=request.user, isread=False).count()
        bookmarked_posts = Bookmark.objects.filter(user=request.user)
        bposts = [post.post.pk for post in bookmarked_posts]
        # Order the UserDetails objects by followers count in descending order
    else:
        bposts = None
        uncount = 0
    if request.user.is_authenticated:
        userinfo = UserDetails.objects.get(user=request.user)
    else:
        userinfo = None
    posts = UserPosts.objects.filter(category="literature").filter(   Q(title__icontains=search_prompt) | Q(author__username__icontains=search_prompt))
    return render(request, 'searchresult.html', {'posts': posts,'userinfo':userinfo,'bposts':bposts,'uncount':uncount})

def technologysearch(request):
    search_prompt = request.POST.get('search')  # Get the search input from the form
    if request.user.is_authenticated:
        uncount = Notification.objects.filter(receiver=request.user, isread=False).count()
        bookmarked_posts = Bookmark.objects.filter(user=request.user)
        bposts = [post.post.pk for post in bookmarked_posts]
        # Order the UserDetails objects by followers count in descending order
    else:
        bposts = None
        uncount = 0
    if request.user.is_authenticated:
        userinfo = UserDetails.objects.get(user=request.user)
    else:
        userinfo = None
    posts = UserPosts.objects.filter(category="technology").filter(   Q(title__icontains=search_prompt) | Q(author__username__icontains=search_prompt))
    return render(request, 'searchresult.html', {'posts': posts,'userinfo':userinfo,'bposts':bposts,'uncount':uncount})
def historysearch(request):
    if request.user.is_authenticated:
        uncount = Notification.objects.filter(receiver=request.user, isread=False).count()
        bookmarked_posts = Bookmark.objects.filter(user=request.user)
        bposts = [post.post.pk for post in bookmarked_posts]
        # Order the UserDetails objects by followers count in descending order
    else:
        bposts = None
        uncount = 0
    if request.user.is_authenticated:
        userinfo = UserDetails.objects.get(user=request.user)
    else:
        userinfo = None
    search_prompt = request.POST.get('search')  # Get the search input from the form
    posts = UserPosts.objects.filter(category="history").filter(   Q(title__icontains=search_prompt) | Q(author__username__icontains=search_prompt))
    return render(request, 'searchresult.html', {'posts': posts,'userinfo':userinfo,'bposts':bposts,'uncount':uncount})
def educationandlearningsearch(request):
    search_prompt = request.POST.get('search')  # Get the search input from the form
    if request.user.is_authenticated:
        uncount = Notification.objects.filter(receiver=request.user, isread=False).count()
        bookmarked_posts = Bookmark.objects.filter(user=request.user)
        bposts = [post.post.pk for post in bookmarked_posts]
        # Order the UserDetails objects by followers count in descending order
    else:
        bposts = None
        uncount = 0
    if request.user.is_authenticated:
        userinfo = UserDetails.objects.get(user=request.user)
    else:
        userinfo = None
    posts = UserPosts.objects.filter(category="education and learning").filter(   Q(title__icontains=search_prompt) | Q(author__username__icontains=search_prompt))
    return render(request, 'searchresult.html', {'posts': posts,'bposts':bposts,'userinfo':userinfo,'uncount':uncount})
def mythologysearch(request):
    search_prompt = request.POST.get('search')  # Get the search input from the form
    if request.user.is_authenticated:
        uncount = Notification.objects.filter(receiver=request.user, isread=False).count()
        bookmarked_posts = Bookmark.objects.filter(user=request.user)
        bposts = [post.post.pk for post in bookmarked_posts]
        # Order the UserDetails objects by followers count in descending order
    else:
        bposts = None
        uncount = 0
    if request.user.is_authenticated:
        userinfo = UserDetails.objects.get(user=request.user)
    else:
        userinfo = None
    posts = UserPosts.objects.filter(category="mythology").filter(   Q(title__icontains=search_prompt) | Q(author__username__icontains=search_prompt))
    return render(request, 'searchresult.html', {'posts': posts,'userinfo':userinfo,'bposts':bposts,'uncoount':uncount})
def sciencesearch(request):
    if request.user.is_authenticated:
        uncount = Notification.objects.filter(receiver=request.user, isread=False).count()
        bookmarked_posts = Bookmark.objects.filter(user=request.user)
        bposts = [post.post.pk for post in bookmarked_posts]
        # Order the UserDetails objects by followers count in descending order
    else:
        bposts = None
        uncount = 0
    search_prompt = request.POST.get('search')
    # Get the search input from the form
    if request.user.is_authenticated:
        userinfo = UserDetails.objects.get(user=request.user)
    else:
        userinfo = None
    posts = UserPosts.objects.filter(category="science").filter(   Q(title__icontains=search_prompt) | Q(author__username__icontains=search_prompt))
    return render(request, 'searchresult.html', {'posts': posts,'userinfo':userinfo,'bposts':bposts,'uncount':uncount})
def gamesandsportssearch(request):
    if request.user.is_authenticated:
        uncount = Notification.objects.filter(receiver=request.user, isread=False).count()
        bookmarked_posts = Bookmark.objects.filter(user=request.user)
        bposts = [post.post.pk for post in bookmarked_posts]
        # Order the UserDetails objects by followers count in descending order
    else:
        bposts = None
        uncount = 0
    if request.user.is_authenticated:
        userinfo = UserDetails.objects.get(user=request.user)
    else:
        userinfo = None
    search_prompt = request.POST.get('search')  # Get the search input from the form
    posts = UserPosts.objects.filter(category="games and sports").filter(   Q(title__icontains=search_prompt) | Q(author__username__icontains=search_prompt))
    return render(request, 'searchresult.html', {'posts': posts,'userinfo':userinfo,'bposts':bposts,'uncount':uncount})
def artandculturesearch(request):
    if request.user.is_authenticated:
        bookmarked_posts = Bookmark.objects.filter(user=request.user)
        bposts = [post.post.pk for post in bookmarked_posts]
    else:
        bposts = None
    if request.user.is_authenticated:
        userinfo = UserDetails.objects.get(user=request.user)
    else:
        userinfo = None
    search_prompt = request.POST.get('search')  # Get the search input from the form
    posts = UserPosts.objects.filter(category="art and culture").filter(   Q(title__icontains=search_prompt) | Q(author__username__icontains=search_prompt))
    return render(request, 'searchresult.html', {'posts': posts,'userinfo':userinfo,'bposts':bposts})
def foodandtravelsearch(request):
    if request.user.is_authenticated:
        uncount = Notification.objects.filter(receiver=request.user, isread=False).count()
        bookmarked_posts = Bookmark.objects.filter(user=request.user)
        bposts = [post.post.pk for post in bookmarked_posts]
        # Order the UserDetails objects by followers count in descending order
    else:
        bposts = None
        uncount = 0
    if request.user.is_authenticated:
        userinfo = UserDetails.objects.get(user=request.user)
    else:
        userinfo = None
    search_prompt = request.POST.get('search')  # Get the search input from the form
    posts = UserPosts.objects.filter(category="food and travel").filter(   Q(title__icontains=search_prompt) | Q(author__username__icontains=search_prompt))
    return render(request, 'searchresult.html', {'posts': posts,'userinfo':userinfo,'bposts':bposts,'uncount':uncount})
def otherssearch(request):
    search_prompt = request.POST.get('search')  # Get the search input from the form
    if request.user.is_authenticated:
        uncount = Notification.objects.filter(receiver=request.user, isread=False).count()
        bookmarked_posts = Bookmark.objects.filter(user=request.user)
        bposts = [post.post.pk for post in bookmarked_posts]
        # Order the UserDetails objects by followers count in descending order
    else:
        bposts = None
        uncount = 0
    if request.user.is_authenticated:
        userinfo = UserDetails.objects.get(user=request.user)
    else:
        userinfo = None
    posts = UserPosts.objects.filter(category="others").filter(   Q(title__icontains=search_prompt) | Q(author__username__icontains=search_prompt))
    return render(request, 'searchresult.html', {'posts': posts,'userinfo':userinfo,'bposts':bposts,'uncount':uncount})

def Blog(request):
    most_viewed_posts=UserPosts.objects.all().order_by('-views_count')
    newest_posts=UserPosts.objects.all().order_by('-post_time')
    userdetails = UserDetails.objects.annotate(followers_count=Count('followers'))


    # Order the UserDetails objects by followers count in descending order
    userdetails = userdetails.order_by('-followers_count')
    if request.user.is_authenticated:
        uncount = Notification.objects.filter(receiver=request.user, isread=False).count()
        bookmarked_posts = Bookmark.objects.filter(user=request.user)
        bposts = [post.post.pk for post in bookmarked_posts]
    else:
        bposts= None
        uncount= 0
    posts=UserPosts.objects.all()
    if request.user.is_authenticated:
        userinfo = UserDetails.objects.get(user=request.user)
    else:
        userinfo = None
    return render(request,'index.html',{'posts':posts,'uncount':uncount,'userinfo':userinfo,'bposts':bposts,'most_viewed_posts':most_viewed_posts,'newest_posts':newest_posts,'mfuser': userdetails})

def home(request):
    most_viewed_posts = UserPosts.objects.all().order_by('-views_count')


    newest_posts = UserPosts.objects.all().order_by('-post_time')
    userdetails = UserDetails.objects.annotate(followers_count=Count('followers'))
    if request.user.is_authenticated:
        uncount = Notification.objects.filter(receiver=request.user, isread=False).count()
        bookmarked_posts = Bookmark.objects.filter(user=request.user)
        bposts = [post.post.pk for post in bookmarked_posts]
    # Order the UserDetails objects by followers count in descending order
    else:
        bposts= None
        uncount= 0
    userdetails = userdetails.order_by('-followers_count')
    if request.user.is_authenticated:
        userinfo = UserDetails.objects.get(user=request.user)
    else:
        userinfo = None
    posts = UserPosts.objects.all()
    return render(request, 'index.html',
                  {'posts': posts,'bposts':bposts,'userinfo':userinfo, 'most_viewed_posts': most_viewed_posts, 'newest_posts': newest_posts,
                   'mfuser': userdetails,'uncount':uncount})


def most_viewed_posts(request):
    if request.user.is_authenticated:
        bookmarked_posts = Bookmark.objects.filter(user=request.user)
        bposts = [post.post.pk for post in bookmarked_posts]
        uncount = Notification.objects.filter(receiver=request.user, isread=False).count()
    else:
        bposts = None
        uncount = 0
    p = UserPosts.objects.all().order_by('-views_count')
    page = Paginator(p, 6)
    page_list = request.GET.get('page')
    page = page.get_page(page_list)
    if request.user.is_authenticated:
        userinfo = UserDetails.objects.get(user=request.user)
    else:
        userinfo = None
    return render(request,'most_viewed_posts.html',{'posts':page,'bposts':bposts,'uncount':uncount,'userinfo':userinfo})

def newest_posts(request):
    if request.user.is_authenticated:
        bookmarked_posts = Bookmark.objects.filter(user=request.user)
        bposts = [post.post.pk for post in bookmarked_posts]
        uncount = Notification.objects.filter(receiver=request.user, isread=False).count()
    else:
        bposts = None
        uncount = 0
    if request.user.is_authenticated:
        userinfo = UserDetails.objects.get(user=request.user)
    else:
        userinfo = None
    p = UserPosts.objects.all().order_by('-post_time')
    page = Paginator(p, 6)
    page_list = request.GET.get('page')
    page = page.get_page(page_list)
    return render(request,'newest_posts.html',{'posts':page,'bposts':bposts,'userinfo':userinfo,'uncount':uncount})

def all_posts(request):
    p=UserPosts.objects.all().order_by('?')
    page=Paginator(p,6)
    page_list=request.GET.get('page')
    page=page.get_page(page_list)

    if request.user.is_authenticated:
        bookmarked_posts = Bookmark.objects.filter(user=request.user)
        bposts = [post.post.pk for post in bookmarked_posts]
        uncount = Notification.objects.filter(receiver=request.user, isread=False).count()

    else:
        bposts = None
        uncount = 0

    #pl=list(posts)
    #shuffle(pl)
    if request.user.is_authenticated:
        userinfo = UserDetails.objects.get(user=request.user)
    else:
        userinfo = None
    return render(request,'all_posts.html',{'posts':page,'bposts':bposts,'uncount':uncount,'userinfo':userinfo})

def about(request):
    if request.user.is_authenticated:
        uncount = Notification.objects.filter(receiver=request.user, isread=False).count()

    # Order the UserDetails objects by followers count in descending order
    else:

        uncount = 0
    if request.user.is_authenticated:
        userinfo = UserDetails.objects.get(user=request.user)
    else:
        userinfo = None
    return render(request,'about.html',{'userinfo':userinfo,'uncount':uncount})

def contact(request):
    if request.method == 'POST':
        uname=request.POST['uname']
        subject=request.POST['subject']
        content=request.POST['content']
        uemail=request.POST['uemail']
        c=Contact(name=uname,email=uemail,subject=subject,content=content)
        c.save()
    if request.user.is_authenticated:
        uncount = Notification.objects.filter(receiver=request.user, isread=False).count()

    # Order the UserDetails objects by followers count in descending order
    else:

        uncount = 0
    if request.user.is_authenticated:
        userinfo = UserDetails.objects.get(user=request.user)
    else:
        userinfo = None
    return render(request,'contact.html',{'userinfo':userinfo,'uncount':uncount})

def addpost(request):
    if request.method == 'POST':

        category = request.POST['category']
        title = request.POST['title']
        content = request.POST['content']
        image = request.FILES.get('image')
        if request.user.is_authenticated:
            author = request.user
        else:
                author = 'anonymous'

        author_details=UserDetails.objects.get(user=request.user)
        author = request.user if request.user.is_authenticated else None  # Set author to the logged-in user or None

        user_post = UserPosts(category=category, title=title, content=content, image=image, author=author,author_details=author_details)
        user_post.save()
        xp=UserDetails.objects.get(user=request.user).xp
        xp+=30
        npost=UserPosts.objects.filter(author=author).count()
        if npost == 10:
            xp+=100
        if npost == 20:
            xp+=200
        s = UserDetails.objects.get(user=request.user)
        s.xp = xp
        s.save()

        # Redirect to a page where the user can view their post or do something else
        return redirect('profile')
    if request.user.is_authenticated:
        uncount = Notification.objects.filter(receiver=request.user, isread=False).count()
       
    # Order the UserDetails objects by followers count in descending order
    else:
       
        uncount= 0
    userinfo = UserDetails.objects.get(user=request.user)

    return render(request,'addpost.html',{'uncount':uncount,'userinfo': userinfo})

def register_view(request):
    if request.method == 'POST':
        # Process the registration form submission
        username = request.POST['username']  # Updated to match the field name in your HTML form
        pass1 = request.POST['password1']  # Updated to match the field name in your HTML form

        email = request.POST['email']  # Updated to match the field name in your HTML form
        nickname = request.POST['nickname']

         # Create a new user (or your custom user profile) and save it
        user = User.objects.create_user(username=username, password=pass1, email=email)
        user.save()

        # Check if nickname is empty, if so, set it to the username
        if not nickname:
            nickname = username




        # Create a UserDetails instance associated with the User

        user_details = UserDetails(user=user, nickname=nickname,xp=0)
        user_details.save()

        # Log the user in after registration
        login(request, user)

        # Redirect to the user's profile or another page
        return redirect('profile')


    return render(request, 'register.html')


def login_view(request):
    if request.method == 'POST':
        # Process the login form submission
        username = request.POST['username']
        password = request.POST['password']

        # Authenticate the user
        user = authenticate(request, username=username, password=password)

        if user is not None:
            # User is authenticated, log them in
            login(request, user)
            return redirect('profile')
        else:

            # Authentication failed, return an error message or redirect back to the login page
            # For simplicity, let's return an error message
            error_message = "Invalid credentials. Please try again."
            return render(request, 'login.html', {'error_message': error_message})

    return render(request, 'login.html')


def userprofile_view(request, user_id):
    total_views = 0
    total_posts = 0

    posts = UserPosts.objects.filter(author=user_id)
    for post in posts:

        total_posts += 1
        total_views += post.views_count

    user = User.objects.get(id=user_id)
    ouserinfo = UserDetails.objects.get(user=user)

    if user == request.user:
        return redirect('profile')
    if request.user.is_authenticated:
        uncount = Notification.objects.filter(receiver=request.user, isread=False).count()
        is_following = Follow.objects.filter(follower=request.user, followed=user).exists()
        bookmarked_posts = Bookmark.objects.filter(user=request.user)
        bposts = [post.post.pk for post in bookmarked_posts]
    else:
        is_following = False
        bposts = None
        uncount = 0


    followers_count = user.followers.count()
    following_count = user.following.count()
    if request.user.is_authenticated:
        userinfo = UserDetails.objects.get(user=request.user)
    else:
        userinfo = None
    return render(request, 'userprofile.html', {'posts': posts, 'ouserinfo': ouserinfo,'userinfo': userinfo, 'total_views': total_views, 'total_posts': total_posts,'is_following': is_following,
        'followers_count': followers_count, 'following_count': following_count,'bposts':bposts})

@login_required
def following_posts(request):
    # Get the list of users the current user is following
    following_users = Follow.objects.filter(follower=request.user).values_list('followed', flat=True)

    # Retrieve posts from the users the current user is following
    pl = UserPosts.objects.filter(author__in=following_users).order_by('-post_time')
    page = Paginator(pl, 6)
    page_list = request.GET.get('page')
    page = page.get_page(page_list)
    bookmarked_posts = Bookmark.objects.filter(user=request.user)
    bposts = [post.post.pk for post in bookmarked_posts]
    if request.user.is_authenticated:
        uncount = Notification.objects.filter(receiver=request.user, isread=False).count()

    else:

        uncount = 0

    userinfo = UserDetails.objects.get(user=request.user)
    context = {
        'posts': page,
        'userinfo':userinfo,
        'bposts':bposts,
        'uncount':uncount,

    }

    return render(request, 'following_post.html', context)

@login_required
def follow(request, user_id):
    followed_user = get_object_or_404(User, id=user_id)
    follower = request.user
    xp = UserDetails.objects.get(user=followed_user).xp
    xp+=20
    s = UserDetails.objects.get(user=followed_user)
    s.xp = xp
    s.save()
    # Check if the user is not trying to follow themselves
    if followed_user != follower:
        follow, created = Follow.objects.get_or_create(follower=follower, followed=followed_user)
        nsender = request.user
        nreceiver = followed_user
        message = " started following you "
        n = Notification(sender=nsender, receiver=nreceiver, message=message)
        n.save()
    followers_count = request.user.followers.count()
    if followers_count == 10:
        xp+=100
    if followers_count == 50:
        xp+=300
    followers = Follow.objects.filter(followed=followed_user).values_list('follower', flat=True)
    followers_list = list(User.objects.filter(pk__in=followers))
    following = Follow.objects.filter(follower=request.user).values_list('followed', flat=True)
    following_list = list(User.objects.filter(pk__in=following))

    # Create a UserDetails instance associated with the User
    followed_user_details = UserDetails.objects.filter(user=followed_user).first()
    if followed_user_details:
        followed_user_details.followers.set(followers_list)

    follower_user_details = UserDetails.objects.filter(user=request.user).first()
    if follower_user_details:
        follower_user_details.following.set(following_list)

    return redirect('userprofile', user_id)


@login_required
def unfollow(request, user_id):
    followed_user = get_object_or_404(User, id=user_id)
    follower = request.user
    xp = UserDetails.objects.get(user=followed_user).xp
    xp -= 20
    s = UserDetails.objects.get(user=followed_user)
    s.xp=xp
    s.save()
    try:
        follow = Follow.objects.get(follower=follower, followed=followed_user)
        follow.delete()

    except Follow.DoesNotExist:
        pass

    followers = Follow.objects.filter(followed=followed_user).values_list('follower', flat=True)
    followers_list = list(User.objects.filter(pk__in=followers))
    following = Follow.objects.filter(follower=request.user).values_list('followed', flat=True)
    following_list = list(User.objects.filter(pk__in=following))

    # Create a UserDetails instance associated with the User
    followed_user_details = UserDetails.objects.filter(user=followed_user).first()
    if followed_user_details:
        followed_user_details.followers.set(followers_list)

    follower_user_details = UserDetails.objects.filter(user=request.user).first()
    if follower_user_details:
        follower_user_details.following.set(following_list)

    return redirect('userprofile', user_id)


@login_required
def profile_view(request):


    total_views = 0
    total_posts = 0
    userinfo = UserDetails.objects.get(user=request.user)
    myposts = UserPosts.objects.filter(author=request.user).order_by('-post_time')
    for post in myposts:
        total_posts += 1
        total_views += post.views_count
    # You can access user attributes like username, email, etc.
    followers_count = request.user.followers.count()
    following_count = request.user.following.count()


    # This view is protected and can only be accessed by logged-in users
     # The logged-in user
    #user = get_object_or_404(User, id=user_id)

    p = Bookmark.objects.filter(user=request.user)
    bookmarked_posts = list(p)
    shuffle(bookmarked_posts)
    bposts = [post.post.pk for post in bookmarked_posts]

    following_users = Follow.objects.filter(follower=request.user).values_list('followed', flat=True)
    if request.user.is_authenticated:
        uncount = Notification.objects.filter(receiver=request.user, isread=False).count()

    else:
        uncount = 0
    # Retrieve posts from the users the current user is following

    posts = UserPosts.objects.filter(author__in=following_users).order_by('-post_time')
    return render(request, 'profile.html',{'myposts':myposts,'uncount':uncount,'posts':posts,'bposts':bposts,'bookmarked_posts':bookmarked_posts,'userinfo':userinfo,'total_views':total_views,'total_posts':total_posts,'followers_count':followers_count,'following_count':following_count})
@login_required
def logout_view(request):
    logout(request)
   # messages.success(request, "Successfully logged out")
    return redirect('login')

#def login_view(request):
    #return render(request,'login.html')



#def register_view(request):
  #  return render(request,'register.html')



#def profile_view(request):

    #return render(request,'profile.html')

