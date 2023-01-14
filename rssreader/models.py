from django.db import models
import feedparser
from django.shortcuts import render, redirect
from .models import Feed, Article

class Feed(models.Model):
    title = models.CharField(max_length=255)
    link = models.URLField()
    description = models.TextField()

    def __str__(self):
        return self.title

class Article(models.Model):
    feed = models.ForeignKey(Feed, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    link = models.URLField()
    description = models.TextField()
    pub_date = models.DateTimeField()

    def __str__(self):
        return self.title

def parse_feed(url):
    feed = feedparser.parse(url)
    title = feed.feed.title
    link = feed.feed.link
    description = feed.feed.description

    # Create or update the Feed object
    feed_obj, created = Feed.objects.get_or_create(
        link=link, defaults={'title': title, 'description': description}
    )

    # Delete old articles associated with this feed
    Article.objects.filter(feed=feed_obj).delete()

    # Add new articles to the database
    for entry in feed.entries:
        title = entry.title
        link = entry.link
        description = entry.description
        pub_date = entry.published
        article = Article(feed=feed_obj, title=title, link=link, description=description, pub_date=pub_date)
        article.save()

def index(request):
    if request.method == 'POST':
        url = request.POST.get('url')
        try:
            parse_feed(url)
            return redirect('feeds')
        except Exception as e:
            # Handle the exception
            pass
    return render(request, 'index.html')

