
//Testing Konova framework
function TestKonova(divId){

    // first we need to create a stage
    var stage = new Konva.Stage({
        container: divId,   // id of container <div>
        width: 500,
        height: 500
      });
  
    // then create layer
    var layer = new Konva.Layer();
  
    // create our shape
    var circle = new Konva.Circle({
        x: stage.width() / 1.5,
        y: stage.height() / 1.5,
        radius: 70,
        fill: 'red',
        stroke: 'black',
        strokeWidth: 4
    });
    //create a triangle
    var triangle = new Konva.Shape({
        sceneFunc: function(context) {
          context.beginPath();
          context.moveTo(20, 50);
          context.lineTo(220, 80);
          context.quadraticCurveTo(150, 100, 260, 170);
          context.closePath();
  
          // special Konva.js method
          context.fillStrokeShape(this);
        },
        fill: '#00D2FF',
        stroke: 'black',
        strokeWidth: 4
  });

  var pentagon = new Konva.RegularPolygon({
    x: stage.width() / 4,
    y: stage.height() / 2,
    sides: 5,
    radius: 70,
    fill: 'red',
    stroke: 'black',
    strokeWidth: 4,
    shadowOffsetX : 20,
    shadowOffsetY : 25,
    shadowBlur : 40,
    opacity : 0.5
});
    // add the shape to the layer
    layer.add(circle);
    layer.add(triangle);
    layer.add(pentagon);
    // add the layer to the stage
    stage.add(layer);
    
    // draw the image
    layer.draw();
}


/*
canvas object
    initialize and get height, width, background color
    turn border on or off
    set background color
    set size
    set columns count
    set rows count
    set grid lines display true/false
*/
function GraphicCanvas(CanvasId){
    //get DOM canvas element
    var gc = document.getElementById(CanvasId);
    //get the 2d drawing context object
    ctx = gc.getContext("2d")
    this.width = gc.width;
    this.height = gc.height;
    this.backgroundColor = gc.style.backgroundColor;

}

function TestCanvasObject(){
    gc =  new GraphicCanvas("d1");
    output = document.getElementById("TestOutput")
    output.innerHTML = "width: " + gc.width + "<p>" + "height: " + gc.height + "<p> background color: " + gc.backgroundColor;

}

function dolime() {
    var dd1 = document.getElementById("d1");
    dd1.style.backgroundColor="lime";

}


function doyellow() {
    var dd1=
    document.getElementById("d1");
    dd1.style.backgroundColor="white";
    var ctx = dd1.getContext("2d");
    ctx.fillStyle="yellow";
    ctx.fillRect(10,10,40,40);
    ctx.fillRect(60,10,40,40);
    
    ctx.fillStyle="black";
    ctx.font="30px Arial";
    ctx.fillText("Hello",10,80);

}

function fillGrid() {
    var dd1=
    document.getElementById("d1");

}

