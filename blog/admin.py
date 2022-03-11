from django.contrib import admin
from blog.models import Post, Tag, Comment


class PostAdmin(admin.ModelAdmin):
  readonly_fields = ('published_at',)
  raw_id_fields = ['author', 'likes']


class CommentAdmin(admin.ModelAdmin):
  readonly_fields = ('published_at',)
  raw_id_fields = ['post', 'author']

admin.site.register(Post, PostAdmin)
admin.site.register(Tag)
admin.site.register(Comment, CommentAdmin)
