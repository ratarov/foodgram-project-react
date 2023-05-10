from django.contrib import admin

from users.models import User, Subscription


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'username',
        'email',
        'first_name',
        'last_name',
    )
    search_fields = ('email', 'username')
    list_filter = ('id',)
    empty_value_display = '-пусто-'


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'follower',
        'author',
    )
    search_fields = ('follower', 'author')
    list_filter = ('id',)
    empty_value_display = '-пусто-'
