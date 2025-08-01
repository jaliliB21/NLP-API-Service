from django.contrib import admin
from .models import AnalysisHistory, SummarizationHistory, AggregateAnalysisHistory


@admin.register(AnalysisHistory)
class AnalysisHistoryAdmin(admin.ModelAdmin):
    list_display = ('user', 'analysis_source', 'timestamp')
    list_filter = ('analysis_source', 'timestamp')
    search_fields = ('user__username', 'text_input')
    readonly_fields = ('user', 'text_input', 'analysis_result', 'analysis_source', 'analysis_type', 'timestamp') # These fields should be read-only

    def has_add_permission(self, request):
        # Prevent manual creation of history records from the admin panel
        return False
        

@admin.register(SummarizationHistory)
class SummarizationHistoryAdmin(admin.ModelAdmin):
    list_display = ('user', 'summarization_source', 'timestamp')
    list_filter = ('summarization_source', 'timestamp')
    search_fields = ('user__username', 'text_input', 'summarized_text')
    readonly_fields = ('user', 'text_input', 'summarized_text', 'summarization_source', 'max_words_summarization', 'timestamp') # These fields should be read-only

    def has_add_permission(self, request):
        # Prevent manual creation of history records from the admin panel
        return False


@admin.register(AggregateAnalysisHistory)
class AggregateAnalysisHistoryAdmin(admin.ModelAdmin):
    list_display = ('user', 'analysis_type', 'analysis_source', 'timestamp', 'url')
    list_filter = ('analysis_source', 'analysis_type', 'timestamp')
    search_fields = ('user__username', 'url')
    
    # Make all fields read-only in the admin panel
    readonly_fields = [field.name for field in AggregateAnalysisHistory._meta.fields]

    def has_add_permission(self, request):
        # Prevent manual creation of history records from the admin panel
        return False
