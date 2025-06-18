from django.shortcuts import render

# Create your views here.
def Chathome_view(request):
    """
    Render the chat home page.
    """
    return render(request, 'core/chat.html')