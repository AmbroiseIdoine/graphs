from django.db import models
import numpy as np
import re

### utilities ###

class IconObj(object):
    """Informations to draw an icon linking to another subject
    (on a causality diagram)"""
    def __init__(self,title,text,pic,color,pos,size,target_id,node_id=None):
        self.title = title
        self.text = text
        self.picture = pic
        self.color = color
        self.pos = pos
        self.size = size
        self.target_id = target_id
        self.node_id = node_id
        
    def norm(self,offset,factor):
        self.pos = [factor*(self.pos[i]+offset[i]) for i in range(2)]
        self.pos = [int(i) for i in self.pos]
        self.size = int(factor*self.size)
        
class ArrowObj(object):
    """To draw arrows on a causality diagram"""
    def __init__(self,pos,color):
        self.pos = pos
        self.color = color
        
    def norm(self,offset,factor):
        pos=[factor*(offset[i[0]%2]+i[1]) for i in enumerate(self.pos)]
        self.pos = [int(i) for i in pos]
                        
class DiagramObj(object):
    """All information needed to draw a causality diagram"""
    def __init__(self,name,icons,pairs,margin,width,height,line_width,
        text_size_factor=3/2, rescale=True):
    
        text_size=text_size_factor*max([i.size for i in icons])
    
        offsetX = - min([i.pos[0]-text_size for i in icons])
        offsetY = - min([i.pos[1]-text_size for i in icons])
        offset = (offsetX,offsetY)
        
        current_width = max([i.pos[0]+text_size for i in icons]) + offset[0]
        current_height = max([i.pos[1]+text_size for i in icons]) + offset[1]
        
        factor = min((width-2*margin)/current_width,
                    (height-2*margin)/current_height)
        if not rescale:
            self.oldfactor = factor
            width=current_width + 50
            height=current_height + 50
            factor = 1
            
        offset=[i+margin/factor for i in offset]
        
        vects= [np.array([p[1].pos[0]-p[0].pos[0],p[1].pos[1]-p[0].pos[1]]) 
                for p in pairs]
        lengths = [np.sqrt(np.dot(v,v)) for v in vects]
        start_end = [(p[0].size/le,(le-p[1].size)/le) for p,le in zip(pairs,lengths)]
        pos = [[p[0].pos[i%2]+se[i//2]*v[i%2] for i in range(4)] for p,se,v in zip(pairs,start_end,vects)]
        colors = [p[0].color for p in pairs]
        
        arrows = [ArrowObj(*i) for i in zip(pos,colors)]
        
        [i.norm(offset,factor) for i in icons]
        [i.norm(offset,factor) for i in arrows]
    
        self.name=name
        self.width = int(width)
        self.height = int(height)
        self.line_width = int(line_width)
        self.icons = icons
        self.arrows = arrows
        self.lines = [i for i in arrows]
        self.text_size = int(factor*text_size)
        
        self.offset=offset
        self.factor=factor
        
    def add_arrows(self,arrows,lines):
        arrows=[ArrowObj(*i) for i in arrows]
        lines = [ArrowObj(*i) for i in lines]
        [i.norm(self.offset,self.factor) for i in arrows]
        [i.norm(self.offset,self.factor) for i in lines]
        self.arrows.extend(arrows)
        self.lines.extend(lines)
            
class Dummy(object):
    def __init__(self,dict):
        self.__dict__.update(dict)

def find_links(s):
    offset=0
    a=re.findall("http[^ ]*",s)
    b=re.split("http[^ ]*",s)
    c=[]
    for i,j in zip(a,b[:-1]):
        if re.search("""<a.*href""",j) is None:
            c.append("<a href='%s'>%s</a>"%(i,i))
        else:
            c.append(i)
    res=b[0]
    for i,j in zip(c,b[1:]):
        res+=i+j
    return res
        

        
class Icon(models.Model):
    title = models.CharField(max_length=100, blank=True)
    source = models.CharField(max_length=200, blank=True)
    picture = models.ImageField(upload_to = "graphs/icons/",
                                null = True, blank=True)
    def __str__(self):
        return self.title

    color = models.CharField(max_length = 50, default="grey")
    order = models.IntegerField(default = 0)    

### Topic and links
  
class Sector(models.Model): 
    name = models.CharField(max_length = 100)
    short_description = models.CharField(max_length=400, blank=True)
    color = models.CharField(max_length=100)
   
    def __str__(self):
        return self.name
        
class Topic(models.Model):
    """ Class for storing topics (ex: "Le charbon")
    
    The main content is stored in <SujetSection> objects
    
    Attributes:
        header_picture : will be placed above the title
        left_picture : optionnally to be placed on the left_picture
        causes : <Link> topics causing the present issue
        consequences : <Link> topics caused by the present issue
    """
    name = models.CharField(max_length = 100)
    sector = models.ForeignKey(Sector, null = True, blank=True,
                               on_delete = models.SET_NULL)
    icon_picture = models.ForeignKey(Icon, null = True, blank = True,
        on_delete = models.SET_NULL,
        related_name="+")
    url = models.URLField(max_length=200, default = "https://www.linparable.org/")
    
    def __str__(self):
        return self.name

    def get_cause_diagram(self, width=500, height = 500):
        """ Prepare the diagram of issues that cause the present ones
        
        pics : <list of Picture> icon of the causes
        colors : <list of str> the corresponding Sector color
        text : <list of str> a short description of the cause
        pos : <list of (x,y) tuples> position of the cause image
        sizes : <list of float> size of the cause image
        
        """
        size_center= 7
        default_size = 3
        distance = 15
        line_width = 2
        margin = 5
        side_angle = 0.7
        
        causes = self.causes.all()
        lien_causes = [link.cause for link in causes]
        
        if len(causes)>0:
            # computing position and size of the graphic elements
            sizes= [link.relative_share for link in causes]
            sizes= [np.sqrt(i) if i is not None else default_size for i in sizes]
            sizes= [min(i,distance-size_center-2) for i in sizes]
            
            titles=[c.name for c in lien_causes]
            pics=[c.icon_picture for c in lien_causes]
            colors=["grey" if c.sector is None else 
                    c.sector.color for c in lien_causes]
            text = [link.cause_description for link in causes]
            ids = [c.id for c in lien_causes]
            
            
            angle=[0]
            angle.extend([i+j for i,j in zip(sizes[:-1],sizes[1:])])
            angle=np.cumsum(angle)*(2*np.pi/(2*sum(sizes)))
            angle += np.pi - angle[-1]/2
            angle *= side_angle/2 
            angle += (1-side_angle)/2*np.pi + np.pi/2
            pos =  [(distance*np.cos(i),distance*np.sin(i)) for i in angle]
               
            # storing as object list 
            icons=[IconObj(*i) for i in 
                zip(titles,text,pics,colors,pos,sizes,ids)]
        else:
            icons=[]
        
        try:
            color_center=self.sector.color 
        except AttributeError:
            color_center="grey"
        center = IconObj(self.name,self.short_description,
                            self.icon_picture,color_center,
                            (0,0),size_center,self.id)
                            

        con = self.consequences.all()
        
        if len(con)>0:
            # computing position and size of the graphic elements
            titles2 =[link.consequence.name for link in con]
            text2 = [link.consequence_description for link in con]
            pics2 =[link.consequence.icon_picture for link in con]
            colors2 =["grey" if link.consequence.sector is None else 
                    link.consequence.sector.color for link in con]
            ids2 = [link.consequence.id for link in con]

            angle2=np.linspace(0,2*np.pi,len(con),endpoint=False)
            angle2 += np.pi - angle2[-1]/2
            angle2 *= side_angle/2 
            angle2 += (1-side_angle)/2*np.pi - 1/2*np.pi
            pos2 =  [(distance*np.cos(i),distance*np.sin(i)) for i in angle2]
            sizes2= [default_size]*len(con)
            
            # storing as object list 
            icons2=[IconObj(*i) for i in 
                zip(titles2,text2,pics2,colors2,pos2,sizes2,ids2)]
        else:
            icons2=[]
        
        pairs=[(i,center) for i in icons]
        pairs.extend([(center,i) for i in icons2])
        
        icons.extend(icons2)
        icons.append(center)
        
        if len(icons)==0:
            return False

        diag=DiagramObj("causes",icons,pairs,margin,width,height,line_width,
            text_size_factor=2)
        self.cause_diagram = diag
        return True
         
class Link(models.Model):
        """Class for storing a causality link between two Sujets:
        
        Attributes:
            cause: <Topic> topics causing the other issue
            consequence: <Topic> topics caused by the former issue
            relative_share: <float> between 0 and 100, quantifies 
                                          the impact this issue has on another
            description: <str> small text explaining the causality between both
        """
        cause = models.ForeignKey(Topic,related_name="consequences",
                                        on_delete = models.CASCADE)
        consequence = models.ForeignKey(Topic,related_name="causes",
                                        on_delete = models.CASCADE)
        relative_share = models.FloatField(default=None,blank=True, null=True)
        cause_description = models.CharField(max_length=400, blank=True)
        consequence_description = models.CharField(max_length=400, blank=True)
        
        def __str__(self):
            s="%s --> %s"%(self.cause.name,self.consequence.name)
            return s

### Draw the diagram
      
class Diagram(models.Model):
    name = models.CharField(max_length=50,default="Illustration")
    height = models.IntegerField()
    width = models.IntegerField()
    
    def get_diagram(self,rescale=True):
        """Returns a DiagramObj using nodes, liens and arrows"""
        self_nodes=self.nodes.all()
        self_arrows=self.arrows.all()
        
        
        if len(self_nodes)==0:
            return False
        
        nodes = [n.get_icon_obj() for n in self_nodes]
        node_liens = [n.liens.all() for n in self_nodes]
        
        pairs = []
        for n,n_liens in zip(nodes,node_liens):
            if len(n_liens)==0:
                    liens = Link.objects.filter(cause__id=n.target_id).all()
                    liens = [l.consequence.id for l in liens]
                    temp = [(n,target) for target in nodes if target.target_id in liens]
                    pairs.extend(temp)
            else:
                ids=set([(i.cause.id,i.consequence.id) for i in n_liens])
                for n in nodes:
                    pairs.extend([(n,i) for i in nodes if i is not n and 
                                    (n.target_id,i.target_id) in ids])
        ids = set([(i.cause.id,i.consequence.id) for i in self_arrows])
        pairs = [p for p in pairs if (p[0].target_id,p[1].target_id) not in ids]
        
        lines=[]
        arrows=[]
        for obj in self_arrows:
            
            n0=[i for i in nodes if i.node_id==obj.cause.id]
            n1=[i for i in nodes if i.node_id==obj.consequence.id]
            if len(n0)!=1 or len(n1)!=1:
                continue
            n0=n0[0]
            n1=n1[0]
            
            pt=[(obj.X0, obj.Y0), (obj.X1,obj.Y1)]
            pt=[np.array(i) for i in pt if None not in i]
            if len(pt)==0:
                pairs.append((n0,n1))
                continue
            pairs = [p for p in pairs if (p[0].node_id,p[1].node_id)!=(n0.node_id,n1.node_id)]
            vect = pt[0]-np.array(n0.pos)
            first_pt = np.array(n0.pos)+vect*n0.size/np.sqrt(sum(vect*vect))
            vect = np.array(n1.pos) - pt[-1]
            last_pt = np.array(n1.pos)-vect*n1.size/np.sqrt(sum(vect*vect))
            pt=[first_pt,*pt,last_pt]
            
            lines.extend([((*i,*j),n0.color) for i,j in zip(pt[:-1],pt[1:])])
            arrows.append(((*pt[-2],*pt[-1]),n0.color))
            
        
        margin=10
        line_width=2
            
        diagram=DiagramObj(self.id,nodes,pairs,margin,
                            self.width,self.height,line_width,rescale=rescale)
        diagram.add_arrows(arrows,lines)
        print(diagram.lines)
        return diagram
    
    def get_diagram_norescale(self):
        return self.get_diagram(rescale=False)
    
class GraphNode(models.Model):
    """Stores the impact map nodes and arrows"""
    diagram = models.ForeignKey(Diagram, on_delete = models.CASCADE,
        related_name="nodes")
    topic = models.ForeignKey(Topic, on_delete = models.CASCADE,
        related_name="+")
    short_description = models.CharField(max_length=400, blank=True)
    radius = models.FloatField(default=20)
    X = models.FloatField(default=50)
    Y = models.FloatField(default=50)
    
    # optional arguments
    sector = models.ForeignKey(Sector,on_delete = models.SET_NULL, 
        null=True, blank = True)
    liens = models.ManyToManyField(Link, blank = True)
    
    def get_icon_obj(self):
        
        if self.sector is None:
            sector = self.topic.sector 
        else:
            sector = self.sector
        
        color= "grey" if sector is None else sector.color
        res = IconObj(self.topic.name, self.short_description, 
            self.topic.icon_picture, color, (self.X,self.Y), 
            self.radius, self.topic.id, node_id=self.id)
        return res
         
class GraphArrow(models.Model):
    """Stores broken Arrows"""
    diagram = models.ForeignKey(Diagram, on_delete = models.CASCADE,
        related_name="arrows")
    cause = models.ForeignKey(GraphNode, on_delete = models.CASCADE,
        related_name = "+")
    consequence = models.ForeignKey(GraphNode, on_delete = models.CASCADE,
        related_name = "+")
    X0 = models.FloatField(null=True, blank=True)
    Y0 = models.FloatField(null=True, blank=True) 
    X1 = models.FloatField(null=True, blank=True)
    Y1 = models.FloatField(null=True, blank=True) 

   

    
    

    
    
    
    

    
  