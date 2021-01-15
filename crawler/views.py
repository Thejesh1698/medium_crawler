from django.http import JsonResponse
from django.shortcuts import render
import requests
from bs4 import BeautifulSoup

from .models import Creator, Blog


# existing_medium_topics = ["art", "books", "comics", "fiction", "film", "gaming","humour", "music", "nonfiction",
#                           "photography", "podcasts", "poetry", "tv", "visual-design", "culture", "food", "language",
#                           "makers", "outdoors", "pets", "philosophy", "sports", "style", "travel", "true-crime",
#                           "accessibility", "disability", "equality", "feminism", "lgbtqia", "race", "addiction",
#                           "coronavirus", "fitness", "health", "mental-health", "business", "design", "economy",
#                           "freelancing", "leadership", "marketing", "media", "product-management", "remote-work",
#                           "startups", "ux", "venture-capital", "work", "creativity", "mindfulness", "money",
#                           "productivity", "writing", "election-2020", "gun control", "immigration", "justice",
#                           "politics", "andriod-development", "data-science", "ios-development", "javascript",
#                           "machine-learning", "programming", "software-engineering", "biotech", "climate-change",
#                           "math", "neuroscience", "psychology", "science", "space", "astrology", "beauty", "family",
#                           "lifestyle", "parenting", "relationships", "self", "sexuality", "spirituality", "basic-income",
#                           "cannabis", "cities", "education", "history", "psychedelics", "religion", "san-francisco",
#                           "social-media", "society", "transportation", "world", "artificial-intelligence", "blockchain",
#                           "cryptocurrency", "cybersecurity", "digital-life", "future", "gadgets", "privacy",
#                           "self-driving-cars", "technology"]

def admin(request):
    context = {
        "lol": "lol",
    }
    return render(request, 'crawler/admin.html', context)


def main_crawler(request):
    status = 200
    tag = request.GET["tag"]
    url = 'https://medium.com/tag/'+tag+'/archive/2021'  # get current year
    r = requests.get(url)
    latest_blogs = []
    if url == r.url:
        css_soup = BeautifulSoup(r.text, 'html.parser')
        blogs = css_soup.find_all("div", class_="postArticle postArticle--short js-postArticle js-trackPostPresentation js-trackPostScrolls")
        for blog in blogs:
            creator_img = blog.find("img", class_="avatar-image")
            creator_obj, creator_created = Creator.objects.get_or_create(full_name=creator_img["alt"].replace("Go to the profile of ","").strip())
            if not creator_created:
                creator_obj.image_url = creator_img["src"]
                creator_obj.save()
            blog_title = blog.find("h3")
            blog_title = blog_title.text if blog_title else ""

            blog_date = blog.find("time")
            blog_date = blog_date["datetime"] if blog_date else None

            blog_html = blog.find("h4")
            blog_html = blog_html.text if blog_html else ""

            image_url = blog.find("img", class_="graf-image")
            image_url = image_url["src"] if image_url else ""

            blog_url = blog.find("div", class_="postArticle-readMore").find("a")
            blog_url = blog_url["href"] if blog_url else ""

            blog_obj, blog_created = Blog.objects.get_or_create(creator=creator_obj, title=blog_title, tags="",
                                                                blog_date=blog_date, blog_html=blog_html,
                                                                responses="", image_url=image_url, blog_url=blog_url)
            latest_blogs.append(blog_obj)
    else:
        pass

    latest_blogs.sort(key=lambda x: x.blog_date, reverse=True) # or do the querying from db to decrease the processing time if possible

    return JsonResponse({'status': status})
