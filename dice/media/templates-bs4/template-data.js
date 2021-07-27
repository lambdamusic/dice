// These variables will be injected into a page that will use them.
/* eslint no-unused-vars: "off" */
// Const won't work here, only var.
/* eslint no-var: "off" */



// Latest approach for HTML in titles
// https://visjs.github.io/vis-network/examples/network/other/html-in-titles.html

function htmlTitle(html) {
    const container = document.createElement("div");
    container.innerHTML = html;
    return container;
  }

// ********
// 1 - nodes 
// ********
// Manual unpacking to ensure titles are rendered correctly

var nodes = [
    {%- for dict_item in NODES %}
        {
            {%- for k,v in dict_item.items() %}
                {%-  if k == "title" %}
                    "{{ k }}" : htmlTitle("{{ v }}") ,
                {%- else %}
                    "{{ k }}" : "{{ v }}" ,
                {%- endif %}
            {%- endfor %}
        } ,   
    {%- endfor %}
]



// ********
// 2 - edges  
// ********
// one-liner unpacking

var edges = {{EDGES|tojson(True)}};
