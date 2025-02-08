from django.contrib import admin
from .models import ParentUser, ChildUser, Group, Event, Menu, Announcement, GalleryMedia, GalleryCategory, Appointment

@admin.register(ParentUser)
class ParentUserAdmin(admin.ModelAdmin):
    list_display = ('email', 'first_name', 'last_name', 'mobile', 'is_active', 'is_staff')
    list_filter = ('is_active', 'is_staff', 'email_confirmed')
    search_fields = ('email', 'first_name', 'last_name', 'mobile')
    ordering = ('email',)

@admin.register(ChildUser)
class ChildUserAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'birth_date')
    search_fields = ('first_name', 'last_name', 'birth_date')
    ordering = ('last_name', 'first_name')

@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'age_range', 'teacher')
    search_fields = ('name', 'age_range', 'teacher__email')
    list_filter = ('age_range',)
    ordering = ('name',)

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'date', 'time', 'group')
    search_fields = ('title', 'group__name')
    list_filter = ('date',)
    ordering = ('date',)

@admin.register(Menu)
class MenuAdmin(admin.ModelAdmin):
    list_display = ('date', 'breakfast', 'lunch')
    search_fields = ('date',)
    ordering = ('date',)

@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at', 'group')
    search_fields = ('title', 'content', 'group__name')
    list_filter = ('created_at',)
    ordering = ('-created_at',)

@admin.register(GalleryCategory)
class GalleryCategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "created_at")
    search_fields = ("name",)
    ordering = ("-created_at",)


@admin.register(GalleryMedia)
class GalleryMediaAdmin(admin.ModelAdmin):
    list_display = ("id", "media_type", "category", "uploaded_at")
    list_filter = ("media_type", "category", "uploaded_at")
    ordering = ("-uploaded_at",)
    readonly_fields = ("uploaded_at",)

    fieldsets = (
        ("Основная информация", {
            "fields": ("media_type", "image", "video", "category"),
        }),
        ("Дополнительно", {
            "fields": ("uploaded_at",),
        }),
    )
@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('parent_full_name', 'phone_number', 'child_full_name', 'child_birth_date', 'message')
    search_fields = ('parent_full_name', 'phone_number', 'child_full_name')

