
// Use this file to add JavaScript to your project



var network;
var allNodes;
var highlightActive = false;

// create an array with nodes
var nodesDataset = new vis.DataSet(nodes);

// create an array with edges
var edgesDataset = new vis.DataSet(edges);


function redrawAll() {

  // create a network
  var container = document.getElementById('mynetwork');
  var data = {
    nodes: nodesDataset,
    edges: edgesDataset
  };
  var options = {
    autoResize: true,
    groups: {
      1: {  
        borderWidth: 1,
        borderWidthSelected: 2,
        color: {
           border: 'grey',
           background: 'lightblue',
           highlight: {
             border: 'grey',
             background: 'khaki'
         },
           hover: {
             border: '#2B7CE9',
             background: '#D2E5FF'
           }
         }
        }
    },
    nodes: { 
      shape: "dot",  // ellipse, circle, database, box, text, dot, square, icon
      scaling: {
        min: 4,
        max: 30,
        label: {
          min: 10,
          max: 20,
          drawThreshold: 7,
          maxVisible: 20
        }
      },
      },
    edges: {
      smooth: {
        type: 'continuous'
      },
      color:{
        color: 'gainsboro',
        highlight: 'khaki',
        hover: 'lavender'
      },
      shadow:{
        enabled: true,
        color: 'lavender',
        size:10,
        x:5,
        y:5
      },
    },
    interaction: {
        dragNodes: true,
        hideEdgesOnDrag: true,
        hideNodesOnDrag: false,
        navigationButtons: true
    },
    layout: {
        improvedLayout: true
    },
    physics: {
        barnesHut: {
            avoidOverlap: 0,
            centralGravity: 0.3,
            damping: 0.09,
            gravitationalConstant: -80000,
            springConstant: 0.001,
            springLength: 250
        },
        enabled: true,
        repulsion: {
            centralGravity: 0.2,
            damping: 0.09,
            nodeDistance: 300,
            springConstant: 0.05,
            springLength: 200
        },
        solver: 'repulsion',
        stabilization: {
            enabled: true,
            fit: true,
            iterations: 1000,
            onlyDynamicEdges: false,
            updateInterval: 50
        }
    }
  };
  
  network = new vis.Network(container, data, options);

  network.on("stabilizationProgress", function(params) {
    var maxWidth = 496;
    var minWidth = 20;
    var widthFactor = params.iterations/params.total;
    var width = Math.max(minWidth,maxWidth * widthFactor);

    document.getElementById('bar').style.width = width + 'px';
    document.getElementById('bar-text').innerHTML = Math.round(widthFactor*100) + '%';
  });

  network.once("stabilizationIterationsDone", function() {
      document.getElementById('bar-text').innerHTML = '100%';
      document.getElementById('bar').style.width = '496px';
      document.getElementById('loadingBar').style.opacity = 0;
      // really clean the dom element
      setTimeout(function () {document.getElementById('loadingBar').style.display = 'none';}, 500);
  });

  // get a JSON object for neighbours higlighting
  allNodes = nodesDataset.get({returnType:"Object"});
  network.on("click",neighbourhoodHighlight);

}

function neighbourhoodHighlight(params) {
    // if something is selected:
    if (params.nodes.length > 0) {
      highlightActive = true;
      var i,j;
      var selectedNode = params.nodes[0];
      var degrees = 1;


      // ADD NODE TO LIST IN HTML PANEL TOO
      add_node_to_focus_list(selectedNode);
      // console.log(selectedNode);

      // mark all nodes as hard to read.
      for (var nodeId in allNodes) {
        allNodes[nodeId].color = 'gainsboro';
        if (allNodes[nodeId].hiddenLabel === undefined) {
          allNodes[nodeId].hiddenLabel = allNodes[nodeId].label;
          allNodes[nodeId].label = undefined;
        }
      }
      var connectedNodes = network.getConnectedNodes(selectedNode);
      var allConnectedNodes = [];

      // get the second degree nodes
      for (i = 1; i < degrees; i++) {
        for (j = 0; j < connectedNodes.length; j++) {
          allConnectedNodes = allConnectedNodes.concat(network.getConnectedNodes(connectedNodes[j]));
        }
      }

      // all second degree nodes get a different color and their label back
      for (i = 0; i < allConnectedNodes.length; i++) {
        allNodes[allConnectedNodes[i]].color = 'aqua';
        if (allNodes[allConnectedNodes[i]].hiddenLabel !== undefined) {
          allNodes[allConnectedNodes[i]].label = allNodes[allConnectedNodes[i]].hiddenLabel;
          allNodes[allConnectedNodes[i]].hiddenLabel = undefined;
        }
      }

      // all first degree nodes get their own color and their label back
      for (i = 0; i < connectedNodes.length; i++) {
        allNodes[connectedNodes[i]].color = undefined;
        if (allNodes[connectedNodes[i]].hiddenLabel !== undefined) {
          allNodes[connectedNodes[i]].label = allNodes[connectedNodes[i]].hiddenLabel;
          allNodes[connectedNodes[i]].hiddenLabel = undefined;
        }
      }

      // the main node gets its own color and its label back.
      allNodes[selectedNode].color = undefined;
      if (allNodes[selectedNode].hiddenLabel !== undefined) {
        allNodes[selectedNode].label = allNodes[selectedNode].hiddenLabel;
        allNodes[selectedNode].hiddenLabel = undefined;
      }
    }
    else if (highlightActive === true) {
      // reset all nodes
      for (var nodeId in allNodes) {
        allNodes[nodeId].color = undefined;
        if (allNodes[nodeId].hiddenLabel !== undefined) {
          allNodes[nodeId].label = allNodes[nodeId].hiddenLabel;
          allNodes[nodeId].hiddenLabel = undefined;
        }
      }
      highlightActive = false
    }

    // transform the object into an array
    var updateArray = [];
    for (nodeId in allNodes) {
      if (allNodes.hasOwnProperty(nodeId)) {
        updateArray.push(allNodes[nodeId]);
      }
    }
    nodesDataset.update(updateArray);

    // end of neighbourhoodHighlight()
  }



// finally:
redrawAll();



function focus_node(nodeid) {
  network.focus(nodeid, {scale: 2}); 
  scrollTo("mynetwork");
  add_node_to_focus_list(nodeid);

}


// ADD NODE TO CLICKED-NODES HTML PANEL 
function add_node_to_focus_list(nodeid) {

  $("#initial-message").hide();

  // show and bring  to the top
  $( "#node-" + nodeid  ).show();
  $( "#node-" + nodeid  ).prependTo(".node-active");

  // reset previous active node
  $(".node-active").removeClass("node-active");
  $( "#node-" + nodeid  ).addClass("node-active");

}


// SCROLL TO ELEMENT
function scrollTo(elementtoScrollToID) {
  $([document.documentElement, document.body]).animate({
    scrollTop: $("#"+elementtoScrollToID).offset().top
  }, 500);
}
