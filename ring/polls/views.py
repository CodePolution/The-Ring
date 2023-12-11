from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.views.generic import TemplateView
from django.contrib.auth import authenticate, login
from django.contrib import messages

def main(request):
    return render(request, 'polls/main.html')

class Login(TemplateView):
    template_name = "polls/login.html"

    def lgn(self, request):
        if request.method == "POST":
            llogin = request.POST.get("username")        
            password = request.POST.get("password")    
            user = authenticate(username=llogin, password=password)
            
            if user is not None:
                login(request, user)
                return redirect('main')
                
            else:
                return redirect("login")            
