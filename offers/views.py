from django.shortcuts import render

# Create your views here.
def offers_view(request):
    """Render the offers page"""
    return render(request, 'offers/offers.html')