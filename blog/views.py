from django.db.models import Count, Prefetch
from django.shortcuts import render
from blog.models import Comment, Post, Tag


def serialize_post(post):
    return {
        'title': post.title,
        'teaser_text': post.text[:200],
        'author': post.author.username,
        'comments_amount': post.comments_count,
        'image_url': post.image.url if post.image else None,
        'published_at': post.published_at,
        'slug': post.slug,
        'tags': [serialize_tag(tag) for tag in post.tags_with_posts_count],
        'first_tag_title': post.tags_with_posts_count[0].title,
    }


def serialize_tag(tag):
    return {
        'title': tag.title,
        'posts_with_tag': tag.posts_count,
    }


def prefetch_tag_with_posts_count():
    return Prefetch(
        'tags',
        queryset=Tag.objects.annotate(posts_count=Count('posts')),
        to_attr='tags_with_posts_count',
    )


def get_most_popular_posts():
    tag_prefetch = prefetch_tag_with_posts_count()
    return Post.objects.popular() \
                       .prefetch_related('author') \
                       .prefetch_related(tag_prefetch)[:5] \
                       .fetch_with_comments_count()


def get_most_fresh_posts():
    tag_prefetch = prefetch_tag_with_posts_count()
    return Post.objects.prefetch_related('author') \
                       .prefetch_related(tag_prefetch) \
                       .order_by('-published_at')[:5] \
                       .fetch_with_comments_count()


def get_most_popular_tags():
    return Tag.objects.popular()[:5] \
                      .fetch_with_posts_count()


def index(request):
    most_popular_posts = get_most_popular_posts()
    most_fresh_posts = get_most_fresh_posts()
    most_popular_tags = get_most_popular_tags()
    
    context = {
        'most_popular_posts': [
            serialize_post(post) for post in most_popular_posts
        ],
        'page_posts': [serialize_post(post) for post in most_fresh_posts],
        'popular_tags': [serialize_tag(tag) for tag in most_popular_tags],
    }
    return render(request, 'index.html', context)


def post_detail(request, slug):
    comments_prefetch = Prefetch(
        'comments',
        queryset=Comment.objects.select_related('author') \
                                .filter(post__slug=slug)
    )
    tag_prefetch = prefetch_tag_with_posts_count()
    post = Post.objects.annotate(likes_amount=Count('likes')) \
                       .prefetch_related(comments_prefetch) \
                       .prefetch_related(tag_prefetch) \
                       .get(slug=slug)
                       
    serialized_comments = []
    for comment in post.comments.all():
        serialized_comments.append({
            'text': comment.text,
            'published_at': comment.published_at,
            'author': comment.author.username,
        })

    related_tags = post.tags_with_posts_count

    serialized_post = {
        'title': post.title,
        'text': post.text,
        'author': post.author.username,
        'comments': serialized_comments,
        'likes_amount': post.likes_amount,
        'image_url': post.image.url if post.image else None,
        'published_at': post.published_at,
        'slug': post.slug,
        'tags': [serialize_tag(tag) for tag in related_tags],
    }

    most_popular_tags = get_most_popular_tags()
    most_popular_posts = get_most_popular_posts()

    context = {
        'post': serialized_post,
        'popular_tags': [serialize_tag(tag) for tag in most_popular_tags],
        'most_popular_posts': [
            serialize_post(post) for post in most_popular_posts
        ],
    }
    return render(request, 'post-details.html', context)


def tag_filter(request, tag_title):
    tag = Tag.objects.get(title=tag_title)

    tag_prefetch = prefetch_tag_with_posts_count()
    related_posts = tag.posts.prefetch_related('author') \
                             .prefetch_related(tag_prefetch)[:20] \
                             .fetch_with_comments_count()

    most_popular_tags = get_most_popular_tags()
    most_popular_posts = get_most_popular_posts()

    context = {
        'tag': tag.title,
        'popular_tags': [serialize_tag(tag) for tag in most_popular_tags],
        'posts': [serialize_post(post) for post in related_posts],
        'most_popular_posts': [
            serialize_post(post) for post in most_popular_posts
        ],
    }
    return render(request, 'posts-list.html', context)


def contacts(request):
    # позже здесь будет код для статистики заходов на эту страницу
    # и для записи фидбека
    return render(request, 'contacts.html', {})
