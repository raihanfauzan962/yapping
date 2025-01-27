from django.views.generic import TemplateView
from articles.models import Article

class HomePageView(TemplateView):
    template_name = "home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add articles to the context
        context['articles'] = Article.objects.filter(is_published=True)  # Only get published articles
        return context


class AboutPageView(TemplateView):  # new
    template_name = "about.html"