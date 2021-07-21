//Using Konova framework
//Random Circles Generation

//To Do
//How to delay the generation of the circles so it can be slowed down
//just figured out how to have the setTimeout work for a call to the overall function
//not sure how to do it per loop cycle

//Now have the whole thing closed in a loop that runs it a certain number of times

//Setting following parameters by sliders
//Central hole.  Where the loop to build the circle starts from as a radius.
//        Range from 0 to cMaxRadius
//Step size the divisions of circles building the primary circle  
//Size of the stroke.  
//

function delayedCircles(divId){
  setTimeout(function(){startCircles(divId);},1000);

}

function startCircles(divId, maxCircles, maxRadius, circleStep, theStroke, hole){
  console.log(divId,maxCircles, maxRadius,circleStep, theStroke, hole);
  //console.log(divid);
  //This resizing does not work interactively
  //Need to have it in a separate function and bound to an event listener
  //get the size of the stage parent
  var stgparent = document.querySelector('#stage-parent');

  // first we need to create a stage
  var stage = new Konva.Stage({
      container: divId,   // id of container <div>
      width: stgparent.offsetWidth * 1,
      height: stgparent.offsetHeight * 1
    });

  // then create layer
  var layer = new Konva.Layer();

  //Loop through and create a certain number of circles
  var cCount = 0;
  var cMax = maxCircles;

  // Properties of the circles
  var cMaxRadius = maxRadius;
  var cStroke = theStroke;
  var cStep  = circleStep;
  var cHole = hole

  for (cCount = 0; cCount < cMax; cCount++){
    console.log("Circle: " + String(cCount))
    //get a random radius for the circle
    var cRadius = Math.random() * cMaxRadius;

    //get random location for the circle
    var cX = Math.random() * stgparent.offsetWidth;
    var cY = Math.random() * stgparent.offsetHeight;

    //Set the increment of the circles, ie stroke width and the step in the 
    //loop that builds the circles.
    //loop variables
    var i;

    for (i=cHole; i < cRadius; i=i+cStep){
      //console.log(i,cHole,cRadius,cStep)
      // create our shape
      var circle = new Konva.Circle({
        x: cX,
          y: cY,
          radius: i,
          stroke: ("rgb("+ String(Math.random()*255) + ","+ String(Math.random()*255) + ","+String(Math.random()*255)+")"),
          strokeWidth: cStroke 
      });
      // add the shape to the layer
      layer.add(circle);
    }
    
  }
  // add the layer to the stage
  stage.add(layer);

  // draw the image
  layer.draw();
    
  
  //Add an event listener to stage
  stage.addEventListener('click',function(event){
    //toggles the show hide state of the controls
    $("#controls").toggle();    
    })

 
}

