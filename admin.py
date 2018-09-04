from django.contrib import admin

from .models import Topic, Sector
from .models import Icon, Link, Diagram, GraphNode, GraphArrow
    
class TopicAdmin(admin.ModelAdmin):
    model = Topic
    list_filter = ["sector"]
    list_display = ["name","sector"]

class SectorAdmin(admin.ModelAdmin):
    model = Sector
    list_filter = ["name"]
    list_display = ["name"]
    
class IconAdmin(admin.ModelAdmin):
    model = Icon
    
class LinkAdmin(admin.ModelAdmin):
    model = Link
    list_display=["cause","consequence"]
    list_filter =["cause","consequence"]
  
class GraphNodeInLine(admin.TabularInline):
    model = GraphNode
    fk_name = "diagram"
    extra = 0

class GraphArrowInLine(admin.TabularInline):
    model = GraphArrow
    fk_name = "diagram"
    extra = 0
    
class DiagramAdmin(admin.ModelAdmin):
    model = Diagram
    inlines = [GraphNodeInLine,GraphArrowInLine]
    list_display = ('name','id')
    
    
admin.site.register(Topic, TopicAdmin)
admin.site.register(Sector, SectorAdmin)
admin.site.register(Icon,IconAdmin)
admin.site.register(Link, LinkAdmin)
admin.site.register(Diagram,DiagramAdmin)
