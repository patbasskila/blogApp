from django.shortcuts import render, redirect, get_object_or_404
from app.models import Post, Comments, Tag, Profile, WebsiteMeta
from .forms import CommentForm, SubscribeForm, NewUserForm
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.models import User
from django.db.models import Count
from django.contrib.auth import login



# Create your views here.
def index(request):
    posts = Post.objects.all()
    top_posts = Post.objects.all().order_by('-view_count')[0:3]  # here we getting the top 3 posts by slicing the list
    recent_posts = Post.objects.all().order_by('-last_updated')[0:3] # here we getting the 3 latest posts by the last_updated field
    featured_blog = Post.objects.filter(is_featured=True)
    subscribe_form = SubscribeForm()
    subscribe_successful = None
    website_info = None

    if WebsiteMeta.objects.all().exists():   # we checking if any of the website meta data exist, if exist, then we render it to the template
        website_info = WebsiteMeta.objects.all()[0]   # we fetch the very first object


    if featured_blog:
        featured_blog = featured_blog[0]  # we only getting the very first blog as the featured blog if multiple blogs return as a list

    if request.POST:
        subscribe_form = SubscribeForm(request.POST)
        if subscribe_form.is_valid():
            subscribe_form.save()
            request.session['subscribed'] = True    # here we assign the session to True if a user sucessfully subscribe to the Newsletter, 
            # so the next time they access the site, the subscribe option won't be shown to them on the page. 'subscribed' is the key against which data is being stored
            subscribe_successful = 'Subscribed Successfully'
            subscribe_form = SubscribeForm()   # here we resetting the form after successful subscription
        
    context = {'posts': posts, 'top_posts': top_posts, 'recent_posts': recent_posts, 'subscribe': subscribe_form, 'subscribe_message': subscribe_successful, 'is_featured': featured_blog, 'website_info': website_info}
    return render(request, 'app/index.html', context)


def post_page(request, slug):
    post = Post.objects.get(slug=slug)
    comments = Comments.objects.filter(post=post, parent=None)
    form = CommentForm()

    # Bookmark logic
    bookmarked = False
    if post.bookmarks.filter(id = request.user.id).exists():  # we filter if a user has bookmarked a particular post, return true if it is bookmarked by the user, else return false
        bookmarked = True
    is_bookmarked = bookmarked

    # likes logic
    liked = False
    if post.likes.filter(id = request.user.id).exists():
        liked = True
    number_of_likes = post.number_of_likes()
    post_is_liked = liked


    if request.POST:
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid:
            if request.POST.get('parent'):
                # save replies
                reply = comment_form.save(commit=False)
                parent = request.POST.get('parent')
                parent_object = Comments.objects.get(id=parent)
                if parent_object:
                    reply.parent = parent_object
                    reply.post = post
                    reply.save()
                    return HttpResponseRedirect(reverse('post_page', kwargs={'slug':slug}))
            else:
                # save comment
                comment = comment_form.save(commit=False) # we dont commit the save yet to save the comment to the DB, instead we only create the comment object
                postid = request.POST.get('post_id')
                post = Post.objects.get(id=postid)
                comment.post = post
                comment.save()
                return HttpResponseRedirect(reverse('post_page', kwargs={'slug':slug}))  # here, we redirect users to the post page after submitting any comments, this way duplicate comments wont be saved to the DB if user click refresh on the page in the browser

    if post.view_count is None:
        post.view_count = 1
    else:
        post.view_count = post.view_count + 1
    post.save()

    # sidebar
    recent_posts = Post.objects.exclude(id=post.id).order_by('-last_updated')[0:3]  # we exclude the current post from showing in sidebar, then we sort by last_updated in descending order
    top_authors = User.objects.annotate(number=Count('post')).order_by('-number')  # we creating the field 'number' which stores the count of post for every author
    tags = Tag.objects.all()
    related_posts = Post.objects.exclude(id=post.id).filter(author=post.author)[0:3]

    context = {'post': post, 'form': form, 'comments': comments, 'is_bookmarked': is_bookmarked, 
               'post_is_liked': post_is_liked, 'number_of_likes': number_of_likes, 
               'recent_posts': recent_posts, 'top_authors': top_authors, 
               'tags': tags, 'related_posts': related_posts}
    return render(request, 'app/post.html', context)


def tag_page(request, slug):
    tag = Tag.objects.get(slug=slug)  # tag object 
    top_posts = Post.objects.filter(tags__in=[tag.id]).order_by('-view_count')[0:3]  # this will return the list of posts associated with the tag object, and the lists is order by the view count
    recent_posts = Post.objects.filter(tags__in=[tag.id]).order_by('-last_updated')[0:3]
    tags = Tag.objects.all()
    context = {'tag': tag, 'top_posts': top_posts, 'recent_posts': recent_posts, 'tags': tags}
    return render(request, 'app/tag.html', context)


def author_page(request, slug):
    profile = Profile.objects.get(slug=slug)
    top_posts = Post.objects.filter(author = profile.user).order_by('-view_count')[0:3]
    recent_posts = Post.objects.filter(author = profile.user).order_by('-last_updated')[0:3]
    top_author = User.objects.annotate(number=Count('post')).order_by('number')[0:3]  # we used the annotate function to add the list of query expressions, in this case we added the 'number' field which representing the count of posts a user has
    
    context = {'profile': profile, 'top_posts': top_posts, 'recent_posts': recent_posts, 'top_author': top_author}
    return render(request, 'app/author.html', context)


def search_posts(request):
    search_query = ''
    if request.GET.get('q'):   # we are checking if the get request has the parameter 'q'
        search_query = request.GET.get('q')  # if the get request has the parameter 'q', then we assign the value of 'q' to the variable
    posts = Post.objects.filter(title__contains=search_query)

    context = {'posts': posts, 'search_query': search_query}
    return render(request, 'app/search.html', context)


def about(request):
    website_info = None

    if WebsiteMeta.objects.all().exists():
        website_info = WebsiteMeta.objects.all()[0]

    context = {'website_info': website_info}
    return render(request, 'app/about.html', context)


def register_user(request):
    form = NewUserForm()
    if request.method == 'POST':
        form = NewUserForm(request.POST)  # here we getting the POST data and pass it to NewUserForm class 
        if form.is_valid():
            user = form.save()
            login(request, user)   # once user info is saved to the DB and registered, we call the inbuilt login function to log user in automatically, login function take two parameters, first is the request and the second is the object
            return redirect('/')  # we redirect user to the home page
        
    context = {'form': form}
    return render(request, 'registration/registration.html', context)


def bookmark_post(request, slug):
    post = get_object_or_404(Post, id=request.POST.get('post_id'))  # get_object_or_404 function does a get call on any model you pass, if it can't fetch the item requested, it will raise 404 
    
    if post.bookmarks.filter(id = request.user.id).exists():
        post.bookmarks.remove(request.user)
    else:
        post.bookmarks.add(request.user)
    return HttpResponseRedirect(reverse('post_page', args=[str(slug)]))


def like_post(request, slug):
    post = get_object_or_404(Post, id=request.POST.get('post_id'))

    if post.likes.filter(id = request.user.id).exists():
        post.likes.remove(request.user)
    else:
        post.likes.add(request.user)
    return HttpResponseRedirect(reverse('post_page', args=[str(slug)]))


def all_bookmarked_post(request):
    all_bookmarked_post = Post.objects.filter(bookmarks=request.user)  # we filtering and getting the bookmarks done by the current user

    context = {'all_bookmarked_post': all_bookmarked_post}
    return render(request, 'app/all_bookmarked_post.html', context)


def all_posts(request):
    all_posts = Post.objects.all()

    context = {'all_posts': all_posts}
    return render(request, 'app/all_posts.html', context)


def all_liked_posts(request):
    all_liked_posts = Post.objects.filter(likes=request.user)

    context = {'all_liked_posts': all_liked_posts}
    return render(request, 'app/all_liked_posts.html', context)