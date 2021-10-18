from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group

from .models import Achievement, Comment, Submission, Task, Topic, User


class UserCreationForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('email',)

    def save(self, commit=True):
        user = super(UserCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user


@admin.register(User)
class UserAdmin(UserAdmin):
    add_form = UserCreationForm
    list_display = ('email', 'name',)
    ordering = ('email',)
    fieldsets = (
        (None, {
            'fields': (
                'email', 'password', 'name', 'is_active', 'is_staff', 'is_superuser',
                'premium', 'birthday', 'achievement',)
        }),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password')}
         ),
    )


@admin.register(Achievement)
class AchievementAdmin(admin.ModelAdmin):
    list_display = ('name', 'desc', 'discount',)
    ordering = ('name',)
    search_fields = ('name', 'desc',)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('user', 'task', 'message', 'datetime',)
    ordering = ('user',)
    search_fields = ('message',)


@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ('task', 'user', 'status', 'datetime', 'language', 'time', 'memory',)
    ordering = ('datetime',)


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('name', 'desc', 'complexity', 'topic', 'input', 'output', 'solution',)
    ordering = ('topic', 'name',)
    search_fields = ('name',)


@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    list_display = ('name', 'desc',)
    ordering = ('name',)
    search_fields = ('name',)


admin.site.unregister(Group)
