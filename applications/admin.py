from django.contrib import admin
from .models import Application, Document, Course

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('type', 'name')
    list_filter = ('type',)
    search_fields = ('name',)
    ordering = ('type', 'name')

# Application and Document are already registered below, so remove duplicate registration
# admin.site.register(Application)
# admin.site.register(Document)

class DocumentInline(admin.TabularInline):
    model = Document
    extra = 0
    fields = ('document_type', 'file', 'uploaded_at', 'image_preview')
    readonly_fields = ('document_type', 'file', 'uploaded_at', 'image_preview')
    can_delete = False

    def image_preview(self, obj):
        from django.utils.html import format_html
        if obj.document_type.lower() in ['photo', 'signature']:
            if obj.file:
                return format_html('<img src="{}" style="max-height: 100px; max-width: 200px;" />', obj.file.url)
        return "-"
    image_preview.short_description = 'Preview'

from django.utils.html import format_html
from django.urls import reverse

@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = (
        'application_number', 'user', 'status', 'submitted_at', 'first_name', 'last_name', 'phone', 'email_display', 'print_button'
    )
    list_filter = ('status', 'submitted_at', 'application_type')
    search_fields = ('application_number', 'user__username', 'first_name', 'last_name', 'phone', 'aadhar_no')
    readonly_fields = ('application_number', 'submitted_at', 'created_at', 'updated_at')
    inlines = [DocumentInline]

    def email_display(self, obj):
        return obj.user.email
    email_display.short_description = 'User Email'

    def print_button(self, obj):
        url = reverse('download_application', args=[obj.id])
        print(f"Generated download URL for application {obj.id}: {url}")
        return format_html(
            '<a class="button" href="{}" target="_blank" style="padding: 5px 10px; font-size: 14px; cursor: pointer; text-decoration: none; color: white; background-color: #3ab543; border-radius: 4px;">Download PDF</a>',
            url
        )
    print_button.short_description = 'Download PDF'

admin.site.register(Document)
admin.site.site_header = "Subham Admin"
admin.site.site_title = "Subham Admin Portal"
admin.site.index_title = "Welcome to Subham Admission Portal"