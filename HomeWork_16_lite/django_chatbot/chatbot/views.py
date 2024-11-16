from django.shortcuts import render

# render start.html page
def start(request):
    return render(request, "start.html")

# render chatbot.html page
def chatbot(request):
    return render(request, "chatbot.html")
