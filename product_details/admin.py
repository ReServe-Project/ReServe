from django.contrib import admin
from django.utils.html import format_html
from .models import Review


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'class_item', 'star_rating', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('user__username', 'class_item__name', 'comment')
    ordering = ('-created_at',)

    def star_rating(self, obj):
        stars = '⭐' * obj.rating
        return format_html(f'<span style="font-size: 1.2em;">{stars}</span>')
    star_rating.short_description = 'Rating'
