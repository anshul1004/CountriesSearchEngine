/**
 * @author Sasipreetam Morsa
 */
 
var BASE_URL = "http://127.0.0.1:5000//api/v1/indexer"
var data = [];

function customEngine(input) {
    var countriesIFrame = document.getElementById("countries").contentWindow.document;    
    
    let frameElement = document.getElementById("countries");
    let doc = frameElement.contentDocument;
    doc.body.innerHTML = doc.body.innerHTML + '<style>a {margin: 0px 0px 0px 0px;}</style>';
    
    countriesIFrame.open();
    
    var out = "";
    var i;
     for(i = 0; i < data.length; i++) {
         out += '<a href="' + data[i].url + '">' +
         data[i].title + '</a><br>' + "<p>" + data[i].url + "<br>" +
         data[i].meta_info +"</p>";
    }
    countriesIFrame.write(out);
    
    countriesIFrame.close();
}

function queryToGoogleBing() {
    var input = document.getElementById("UserInput").value;
    document.getElementById("google").src = "https://www.google.com/search?igu=1&source=hp&ei=lheWXriYJ4PktQXN-LPgDA&q=" + input;
    document.getElementById("bing").src = "https://www.bing.com/search?q=" + input;
}

function search() {
    var input = document.getElementById("UserInput").value;
    
    var page_rank = document.getElementById("page_rank").checked;
    var hits = document.getElementById("hits").checked;
    var flat_clustering = document.getElementById("flat_clustering").checked;
    var hierarchical_clustering = document.getElementById("hierarchical_clustering").checked;
    var association_qe = document.getElementById("association_qe").checked;
    var metric_qe = document.getElementById("metric_qe").checked;
    var scalar_qe = document.getElementById("scalar_qe").checked;
    var type;
    
    if (page_rank) {
        type = "page_rank";
    }
    else if (hits) {
        type = "hits";
    }
    else if (flat_clustering) {
        type = "flat_clustering";
    }
    else if (hierarchical_clustering) {
        type = "hierarchical_clustering";
    }
    else if (association_qe) {
        type ="association_qe";
    }
    else if (metric_qe) {
        type ="metric_qe";
    }
    else if (scalar_qe) {
        type ="scalar_qe";
    }
    
    
    $.get( BASE_URL, {"query": input, "type": type})
    
    .done(function(resp) {
        data = resp
        customEngine(input);

    })
    .fail(function(e) {
        
        console.log("error", e)
    })
}

