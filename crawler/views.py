from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse
from django.shortcuts import render
import requests, enchant, json
from bs4 import BeautifulSoup
from django.core import serializers
from datetime import datetime
from .models import Creator, Blog, Tag
from django.utils.timezone import make_aware

set_range = 10


def admin(request):
    search_query = request.GET.get('tag', '')
    search_history = Tag.objects.all()
    search_history = serializers.serialize('json', search_history)
    context = {
        "search_history": search_history,
        "search_query": search_query
    }
    return render(request, 'admin.html', context)


def blog_page(request):
    article_id = int(request.GET.get('article', 0))
    blog_obj = Blog.objects.get(pk=article_id)
    article_url = blog_obj.blog_url
    r = requests.get(article_url)
    css_soup = BeautifulSoup(r.text, 'html.parser')

    ul_tag = css_soup.find("ul")
    blog_tags = []
    for li_tag in css_soup.find_all("li"):
        blog_tags.append(li_tag.find("a").text)

    css_soup = css_soup.find("article")
    for next_sibling in css_soup.find("h1").find_next_siblings():
        next_sibling.decompose()
    for s in css_soup.select('h1'):
        s.decompose()

    blog_obj.blog_html = str(css_soup)
    blog_obj.tags = json.dumps(blog_tags)
    blog_obj.save()

    context = {"blog_obj": blog_obj, "creator": blog_obj.creator}
    return render(request, 'article.html', context)


def main_crawler(request):
    status = 200
    tag = request.GET["tag"]
    tag_obj, tag_created = Tag.objects.get_or_create(name=tag)
    current_year = datetime.now().year
    url = 'https://medium.com/tag/' + tag + '/archive/'
    r = requests.get(url)
    context = {}
    ten_set_value = request.GET["ten_set_value"]

    result_action = ""

    if r.text.find('Page Not Found') != -1:
        result_action = "list_of_tags"

        r = requests.get('https://medium.com/search/tags?q=' + tag)
        css_soup = BeautifulSoup(r.text, 'html.parser')
        suggestions = css_soup.find("ul", class_="tags tags--postTags tags--light")
        suggestions = suggestions.find_all("li") if suggestions else []

        tag_list = []

        for li_tag in suggestions:
            tag_list.append(li_tag.find("a").text)

        if len(tag_list) == 0:
            english_dict = enchant.Dict("en_US")
            english_dict.check(tag)
            tag_list = english_dict.suggest(tag)

        context['tag_list'] = tag_list
    else:
        result_action = "list_of_blogs"
        css_soup = BeautifulSoup(r.text, 'html.parser')
        year_list = []

        year_tag = css_soup.find_all("div", class_="timebucket u-inlineBlock u-width50")
        for year in year_tag:
            year_list.append(year.find("a").text)

        if len(year_list) > 0:
            year_list = sorted(year_list)

            if tag_obj.latest_crawled_year > 0:
                recent_year_index = year_list.index(str(tag_obj.latest_crawled_year))
            else:
                recent_year_index = len(year_list) - 1

            while recent_year_index < len(year_list):
                actual_crawler(tag, tag_obj, year_list[recent_year_index])
                recent_year_index += 1

            tag_obj.latest_crawled_year = year_list[len(year_list) - 1]

            if tag_obj.old_crawled_year > 0:
                old_year_index = year_list.index(str(tag_obj.old_crawled_year))
            else:
                old_year_index = len(year_list) - 1

            while int(ten_set_value) * set_range > tag_obj.blogs.count():
                old_year_index -= 1
                actual_crawler(tag, tag_obj, year_list[old_year_index])
                tag_obj.old_crawled_year = int(year_list[old_year_index])
        else:
            actual_crawler(tag, tag_obj, "")

        tag_obj.save()

        sql_query = 'select * from (select * from crawler_blog where id in (select blog_id from crawler_tag_blogs where tag_id='+str(tag_obj.id)+') order by blog_date desc limit '+str(int(ten_set_value) * set_range)+') as T order by T.blog_date limit '+str(set_range)
        latest_blogs = Blog.objects.raw(sql_query)
        latest_blogs = serializers.serialize('json', latest_blogs)
        context['latest_blogs'] = latest_blogs

    context['status'] = status
    context['result_action'] = result_action

    return JsonResponse(context)


def actual_crawler(tag, tag_obj, crawl_year):
    r = requests.get('https://medium.com/tag/' + tag + '/archive/' + str(crawl_year))
    css_soup = BeautifulSoup(r.text, 'html.parser')
    blogs = css_soup.find_all("div",
                              class_="postArticle postArticle--short js-postArticle js-trackPostPresentation js-trackPostScrolls")
    for blog in blogs:
        creator_img = blog.find("img", class_="avatar-image")
        creator_obj, creator_created = Creator.objects.get_or_create(
            full_name=creator_img["alt"].replace("Go to the profile of ", "").strip())
        if not creator_created:
            creator_obj.image_url = creator_img["src"]
            creator_obj.save()
        blog_title = blog.find("h3")
        blog_title = blog_title.text if blog_title else ""

        blog_date = blog.find("time")
        if blog_date:
            blog_date = datetime.strptime(blog_date["datetime"], "%Y-%m-%dT%H:%M:%S.%fZ")
            blog_date = make_aware(blog_date)
        else:
            blog_date = None

        blog_html = blog.find("h4")
        blog_html = blog_html.text if blog_html else ""

        image_url = blog.find("img", class_="graf-image")
        image_url = image_url["src"] if image_url else ""

        blog_url = blog.find("div", class_="postArticle-readMore")
        if not blog_url:
            blog_url = blog.find("div",
                                 class_="postMetaInline postMetaInline-authorLockup ui-captionStrong u-flex1 u-noWrapWithEllipsis")
        blog_url = blog_url.find("a")["href"] if blog_url else ""

        blog_obj, blog_created = Blog.objects.get_or_create(creator=creator_obj, title=blog_title, tags="",
                                                            blog_date=blog_date, blog_html=blog_html,
                                                            responses="", image_url=image_url,
                                                            blog_url=blog_url)
        tag_obj.blogs.add(blog_obj)

    tag_obj.save()
