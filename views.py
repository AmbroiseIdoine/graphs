from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.views import generic
from django.utils import timezone
from django.template.loader import get_template
from django.contrib.auth import authenticate, login, logout

from .models import Diagram, Topic

class HomeView(generic.ListView):
    template_name = 'graphs\home.html'
    
    def get_queryset(self):
        """ Return the last published reports """
        return Diagram.objects.order_by('-name')
    
def graph_view(request, pk):
    diagram = get_object_or_404(Diagram, id = pk)
    context = {"diagram": diagram, "edit":False}
    return render(request, 'graphs/graph.html', context)
    
def edit_view(request, pk):
    if not request.user.has_perm("graphs.change_diagram"):
        return redirect(auth_view,pk)
    diagram = get_object_or_404(Diagram, id = pk)
    context = {"diagram": diagram, "edit":True}
    return render(request, 'graphs/edit.html', context)
    
def auth_view(request, pk):
    message = "You need to authenticate"
    if "username" in request.POST.keys():
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
        else:
            message = "Authentication failed"
    
    if request.user.is_authenticated:
        if request.user.has_perm("graphs.change_diagram"):
            return redirect(edit_view, pk)
        else:
            message= "You have no permission to edit"
            
    context = {"pk": pk, "message": message} 
    return render(request, "graphs/auth.html", context)

def logout_view(request):
    logout(request) 
    return redirect("home")
    
def update_view(request, pk):
    diagram = get_object_or_404(Diagram, id = pk)
    for node in diagram.nodes.all():
        node.radius=request.POST["radius_%d"%node.id]
        node.X=request.POST["X_%d"%node.id]
        node.Y=request.POST["Y_%d"%node.id]
        node.short_description=request.POST["short_description_%d"%node.id]
        node.save()
    return redirect("home")
    
    
    
    
    
    
    
    
    
    
    
    
    
    