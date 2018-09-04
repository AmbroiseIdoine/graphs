$(document).ready(function() {
    $("cause_text").hide();
    $(".diagram_text").hide();
    $(".secteur_description").hide();
    $(".edit_node").hide();
});

function show_text(id){
    document.getElementById(id).style.display = 'block';
}

function hide_text(id){
    document.getElementById(id).style.display = 'none';
}

function show_node(id){
    $(".edit_node").hide();
    document.getElementById("edit_node_"+id).style.display = 'block';
    $(".diagram_text_edit").hide();
    document.getElementById("text_"+id).style.display = 'block';
    test(id);
}

function test(id){
    cur=document.getElementById("oldx");
    cur.value=event.clientX;
    cur=document.getElementById("oldx");
    cur.value=10;
}

function num(s){
    return float(s.match(/\d+/)[0])
}

function resize(id){
    radius = document.getElementById("rad_"+id).value;
    cur=document.getElementById("image_"+id);
    oldradius=parseFloat(cur.style.width)/2/0.8;
    cur.style="width: ".concat(radius*2*0.8).concat(";height: ").concat(radius*2*0.8);
    cur=document.getElementById("diagram_icon_"+id);
    newleft=parseFloat(cur.style.left)+(oldradius-radius)*0.8;
    newtop=parseFloat(cur.style.top)+(oldradius-radius)*0.8;
    cur.style = "position: absolute; left: ".concat(newleft).concat("; top: ").concat(newtop).concat(";");

    cur=document.getElementById("canvas_"+id);
    newleft=parseFloat(cur.style.left)+(oldradius-radius)*0.8;
    newtop=parseFloat(cur.style.top)+(oldradius-radius)*0.8;
    posx = parseFloat(cur.style.left)+oldradius*0.8;
    posy = parseFloat(cur.style.top)+oldradius*0.8;
    style = "position: absolute; left: ".concat(newleft).concat("; top: ").concat(newtop);
    cur.style = style.concat("; width: "+2*radius+"; height: "+2*radius+";");
    
    cur = document.getElementById("circle_"+id);
    newleft=parseFloat(cur.style.left)+(oldradius-radius);
    newtop=parseFloat(cur.style.top)+(oldradius-radius);
    style = "left: ".concat(newleft).concat("; top: ").concat(newtop);
    cur.style = style.concat("; width: "+(2*radius+10)+"; height: "+(2*radius+10)+";");
}

function translate(id,offx,offy){
    x = parseFloat(document.getElementById("X_"+id).value);
    y = parseFloat(document.getElementById("Y_"+id).value);
    radius = parseFloat(document.getElementById("rad_"+id).value);
    
    cur=document.getElementById("diagram_icon_"+id);
    oldx=parseFloat(cur.style.left)+radius*0.8-offx;
    oldy=parseFloat(cur.style.top)+radius*0.8-offy;

    dx=x-oldx;
    dy=y-oldy;
    
    cur.style = "position: absolute; left: ".concat(x-radius*0.8+offx).concat("; top: ").concat(y-radius*0.8+offy).concat(";");
    
    cur=document.getElementById("canvas_"+id);
    style = "position: absolute; left: ".concat(x+offx-radius).concat("; top: ").concat(y+offy-radius);
    cur.style = style.concat("; width: "+2*radius+"; height: "+2*radius+";");
    
    cur = document.getElementById("circle_"+id);
    newleft=parseFloat(cur.style.left)+dx;
    newtop=parseFloat(cur.style.top)+dy;
    style = "left: ".concat(newleft).concat("; top: ").concat(newtop);
    cur.style = style.concat("; width: "+(2*radius+10)+"; height: "+(2*radius+10)+";");
}

