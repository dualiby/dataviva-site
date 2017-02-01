var occugrid = document.getElementById('occugrid')
    lang = document.documentElement.lang,
    cicles = occugrid.getAttribute('cicles'),
    size = occugrid.getAttribute('size'),
    group = occugrid.getAttribute('group'),
    dataset = occugrid.getAttribute('dataset'),
    industry_id = "14126";

// Temporarily translates text until dictionary is updated
dictionary['state'] = lang == 'en' ? 'State' : 'Estado';
dictionary['municipality'] = lang == 'en' ? 'Municipality' : 'Municipio';
dictionary['section'] = lang == 'en' ? 'Section' : 'Seção';
dictionary['product'] = lang == 'en' ? 'Product' : 'Produto';
dictionary['product'] = lang == 'en' ? 'Product' : 'Produto';
dictionary['data_provided_by'] = lang == 'en' ? 'Data provided by' : 'Dados fornecidos por';
dictionary['by'] = lang == 'en' ? 'by' : 'por';
dictionary['of'] = lang == 'en' ? 'of' : 'de';
dictionary['port'] = lang == 'en' ? 'Port' : 'Porto';
dictionary['country'] = lang == 'en' ? 'Country' : 'País';
dictionary['continent'] = lang == 'en' ? 'Continent' : 'Continente';
dictionary['kg'] = 'KG';


var buildData = function(apiResponse, metadataFamily, metadataGroup) {

    var getAttrByName = function(item, attr) {
        var index = headers.indexOf(attr);
        return item[index];
    }

    var data = [];
    var headers = apiResponse.headers;

    apiResponse.data.forEach(function(item) {
        var dataItem = {};

        headers.forEach(function(header){   
            dataItem[header] = getAttrByName(item, header);
        });
        try{
            if(dataItem['jobs'] > 3000){
                dataItem['occupation_family'] = metadataFamily[dataItem['occupation_family']]["name_" + lang];
                dataItem['occupation_group'] = metadataGroup[dataItem['occupation_group']]["name_" + lang];
                data.push(dataItem);
            }
        }catch(e){
            ;
        }
    });

    return data;
}

var loadViz = function(data) {
  // instantiate d3plus
  var visualization = d3plus.viz()
    .container("#occugrid")     // container DIV to hold the visualization
    .data(data)     // data to use with the visualization
    .type("bubbles")       // visualization type
    .id(["occupation_group", "occupation_family"]) // nesting keys
    .depth(1)
    .size("jobs")         // key name to size bubbles
    .title("Emprego Estimado para a <cnae> em Minas Gerais (2013)")
    .draw()                // finally, draw the visualization!

};

var loading = dataviva.ui.loading('.loading').text(dictionary['loading'] + '...');

$(document).ready(function() {
    switch(industry_id.length){
        case 1:
            industryDepth = "section";
            break;
        case 2:
            industryDepth = "division";
            break;
        case 5:
            industryDepth = "class";
            break;
    }

    var urls = ["http://api.staging.dataviva.info/rais/year/industry_" + industryDepth + "/occupation_group/occupation_family/?industry_" + industryDepth + "=" + industry_id + "&year=2014", 
                "http://api.staging.dataviva.info/metadata/occupation_family",
                "http://api.staging.dataviva.info/metadata/occupation_group"]
    ajaxQueue(
        urls, 
        function(responses){
            var data = responses[0], 
                metadataFamily = responses[1],             
                metadataGroup = responses[2];

            data = buildData(data, metadataFamily, metadataGroup);

            loading.hide();
            loadViz(data);

        })
});

