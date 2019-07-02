from django.shortcuts import render_to_response, get_object_or_404, render
from django.core.paginator import Paginator
from .models import Blog, BlogType
from django.conf import settings
from django.db.models import Count
from django.contrib.contenttypes.models import ContentType
import calendar
from datetime import datetime
from read_statistics.utils import read_statistics_once_read
# Create your views here.

def get_blog_data(request,blogs_all_list):
    context = {}
    paginator = Paginator(blogs_all_list,settings.BLOGS_PER_PAGE) #devide into 4 per page
    page_num = request.GET.get('page', 1) # GET reuqest
    page_of_blogs = paginator.get_page(page_num)
    current_page_num = page_of_blogs.number
    page_range = [x for x in range(int(page_num)-2, int(page_num)+3) if 0<x<= paginator.num_pages]
    if page_range[0] >= 3:
        page_range.insert(0,'...')
    if paginator.num_pages - page_range[-1] >= 2:
        page_range.append('...')
    if page_range[0] !=1:
        page_range.insert(0,1)
    if page_range[-1] != paginator.num_pages:
        page_range.append(paginator.num_pages)    

    # Get the number of blogs in each type and date
    '''blog_types = BlogType.objects.all()
    blog_types_list = []
    for blog_type in blog_types:
        blog_type.blog_count = Blog.objects.filter(blog_type=blog_type).count()
        blog_types_list.append(blog_type)
    '''
    blog_dates = Blog.objects.dates('created_time', 'month', order='DESC')
    blog_dates_dict = {}
    for blog_date in blog_dates:
        blog_count = Blog.objects.filter(created_time__year=blog_date.year,
                                         created_time__month=blog_date.month).count()
        blog_dates_dict[blog_date] = blog_count
    context['blogs'] = page_of_blogs.object_list
    context['blog_types'] = BlogType.objects.annotate(blog_count=Count('blog_blog'))
    context['blog_dates'] = blog_dates_dict
    context['page_of_blogs'] = page_of_blogs
    context['page_range'] = page_range
    return context

def blog_list(request):
    blogs_all_list = Blog.objects.all()
    context = get_blog_data(request,blogs_all_list)  
    return render(request,'blog/blog_list.html', context)

def blog_detail(request, blog_pk):
    context = {}
    blog = get_object_or_404(Blog, pk=blog_pk)

    # views count
    read_cookie_key = read_statistics_once_read(request,blog)
    context['blog'] = blog
    context['previous_blog'] = Blog.objects.filter(created_time__gt=blog.created_time).last()
    context['next_blog'] = Blog.objects.filter(created_time__lt=blog.created_time).first()
    response = render(request,'blog/blog_detail.html', context) #相应
    response.set_cookie(read_cookie_key,'true')
    return response

def blogs_with_type(request, blogs_with_type):
    blog_type = get_object_or_404(BlogType, type_name = blogs_with_type)
    blogs_all_list = Blog.objects.filter(blog_type=blog_type)
    context = get_blog_data(request,blogs_all_list)
    context['blog_type'] = blog_type
    return render(request,'blog/blogs_with_type.html', context)

def blogs_with_date(request, year, month):
    blogs_all_list = Blog.objects.filter(created_time__year=year, created_time__month=month)
    context = get_blog_data(request,blogs_all_list)
    calendar_month = calendar.month_abbr[month]    
    context['blogs_with_date'] = '%s %s' % (calendar_month,year)
    return render(request,'blog/blogs_with_date.html', context)

