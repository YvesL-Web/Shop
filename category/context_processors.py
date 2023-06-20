from .models import Category

def category_list(request):
    categories = Category.objects.all()
    context = {
        "categories": categories
    }
    return context