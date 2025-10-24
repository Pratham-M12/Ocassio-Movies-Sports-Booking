from django.shortcuts import render

# Create your views here.
def giftcards_view(request):
    """Render the Gift Cards Page"""
    return render(request, 'giftcards/gift_cards.html')