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
    search_fields = ('email',)
    readonly_fields = ('time_zone',)
    fieldsets = (
        (None, {
            'fields': (
                'email', 'password', 'name', 'is_active', 'is_staff', 'is_superuser',
                'premium', 'birthday', 'achievement', 'time_zone',)
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
    list_display = ('name', 'desc', 'link', 'discount',)
    ordering = ('id',)
    search_fields = ('name', 'desc',)

    def get_form(self, request, obj=None, **kwargs):
        kwargs['widgets'] = {'desc': forms.Textarea(
            attrs={'rows': 5, 'cols': 100})}
        return super().get_form(request, obj, **kwargs)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('user', 'task', 'message', 'datetime',)
    ordering = ('-datetime',)
    search_fields = ('message',)

    def get_form(self, request, obj=None, **kwargs):
        kwargs['widgets'] = {'message': forms.Textarea(
            attrs={'rows': 5, 'cols': 100})}
        return super().get_form(request, obj, **kwargs)


@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ('task', 'user', 'status', 'datetime',
                    'language', 'time', 'memory',)
    ordering = ('-datetime',)


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('name', 'desc', 'complexity', 'topic',
                    'input', 'output', 'solution',)
    ordering = ('topic', 'name',)
    search_fields = ('name',)

    def get_form(self, request, obj=None, **kwargs):
        kwargs['widgets'] = {
            'desc': forms.Textarea(attrs={'rows': 15, 'cols': 100}),
            'input': forms.Textarea(attrs={'rows': 25, 'cols': 25}),
            'output': forms.Textarea(attrs={'rows': 25, 'cols': 25}),
            'solution': forms.Textarea(attrs={'rows': 15, 'cols': 100})
        }
        return super().get_form(request, obj, **kwargs)


@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    list_display = ('name', 'desc',)
    ordering = ('name',)
    search_fields = ('name',)

    def get_form(selfT, request, obj=None, **kwargs):
        kwargs['widgets'] = {'desc': forms.Textarea(
            attrs={'rows': 10, 'cols': 100})}
        return super().get_form(request, obj, **kwargs)


admin.site.unregister(Group)
