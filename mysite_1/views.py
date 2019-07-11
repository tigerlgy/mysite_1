import datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from django.db.models import Sum
from django.db.models import Q
from django.core.cache import cache
from django.core.paginator import Paginator

from read_statistics.utils import get_seven_days_read_data, get_today_hot_data, get_yesterday_hot_data
from blog.models import Blog

def get_seven_days_hot_blogs():
    today = timezone.now().date()
    date = today - datetime.timedelta(days=7)
    blogs = Blog.objects \
                .filter(read_details__date__lt=today, read_details__date__gte=date) \
                .values('id','title') \
                .annotate(read_num_sum=Sum('read_details__read_num')) \
                .order_by ('-read_num_sum')
    return blogs[:3]

def home(request):
    blog_content_type = ContentType.objects.get_for_model(Blog)
    dates,read_nums = get_seven_days_read_data(blog_content_type)
    today_hot_data = get_today_hot_data(blog_content_type)

    seven_days_hot_blogs = cache.get('seven_days_hot_blogs')
    if seven_days_hot_blogs is None:
        seven_days_hot_blogs = get_seven_days_hot_blogs()
        cache.set('seven_days_hot_blogs', seven_days_hot_blogs, 3600)

    context = {}
    context['read_nums'] = read_nums
    context['dates'] = dates
    context['today_hot_data'] = get_today_hot_data(blog_content_type)
    context['yesterday_hot_data'] = get_yesterday_hot_data(blog_content_type)
    context['seven_days_hot_blogs'] = seven_days_hot_blogs
    return render(request,'home.html', context)

def search(request):
    search_word = request.GET.get('wd','').strip()
    # Search multiple words
    condition = None
    for word in search_word.split(' '):
        if condition is None:
            condition = Q(title__icontains=word)
        else:
            condition = condition | Q(title__icontains=word)

    # Search selected words
    if condition is not None:
        search_blogs =  Blog.objects.filter(condition)
    else:
        search_blogs = []
        
    # Divide into pages
    paginator = Paginator(search_blogs, 10)
    page_num = request.GET.get('page', 1) # get url page number (GET request)
    page_of_blogs = paginator.get_page(page_num)
    context = {}
    context['search_word'] = search_word
    context['page_of_blogs'] = page_of_blogs
    context['search_blogs_count'] = search_blogs.count()
    return render(request, 'search.html', context)
