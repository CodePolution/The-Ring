from django.shortcuts import render

def main(request):
    return render(request, 'polls/main.html')
