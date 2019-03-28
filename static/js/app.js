
//when new smple is select
d3.select("select").on('change', function() {
  var Sample = d3.select("#selDataset").property('value');
  optionChanged(Sample);
});


function buildMetadata(sample) {

  var url = "/metadata/" + sample;
  //creating js object
  var meta_sample = d3.select("#sample-metadata");
  //send get request to obtain data for that particular sample
  d3.json(url).then(function(result) {
    meta_sample.html("");
    //append metadata to sample-metadata div
    Object.entries(result).forEach(([key, value]) => meta_sample.append("div").text(`${key}: ${value}`));
  });
}


function buildCharts(sample) {
  var url = "/samples/" + sample;
  d3.json(url).then(function(result) {
    console.log(result);


    // build bubble plot
    var bubble_trace = [{
      x: result.otu_ids,
      y: result.sample_values,
      text: result.otu_labels,
      mode: 'markers',
      marker: {
        size: result.sample_values,
        color:result.otu_ids
      }
    }];
    var bubble_layout = {
      showlegend: false,
      height: 650,
      width: 1200,
      title: 'Bubble Chart For Each Sample',
    };

    //Build pie chart for top 10 
    var values = [];
    var ids = [];
    var labels = [];
    var values_index = [];

    for (var i = 0; i < result.sample_values.length; i++) 
    {
      values_index.push(i);
      values_index.sort(function (a, b) {
        //less -1 , greater 1 , 0 for equal for value at current index
        return result.sample_values[a] < result.sample_values[b] ? 1 : result.sample_values[a] > result.sample_values[b] ? -1 : 0; });
    }

    console.log(values_index);

    for (var i =0; i<10; i++){
      var sorted_index = values_index[i];
      values.push(result.sample_values[sorted_index]);
      ids.push(result.otu_ids[sorted_index]);
      labels.push(result.otu_labels[sorted_index]);
    }

    var pie_trace = [{
      type: "pie",
      values: values,
      labels: ids,
      text: labels,
      textinfo: 'percent'
    }];

    var pie_layout = {
      height: 520,
      width: 520,
    };

    var pie_plot_area = document.getElementById('pie');
    var bubble_plot_area = document.getElementById('bubble');

    Plotly.newPlot(pie_plot_area, pie_trace,pie_layout);
    Plotly.newPlot(bubble_plot_area, bubble_trace, bubble_layout);

  });
}


function init() {
  // Grab a reference to the dropdown select element
  var selector = d3.select("#selDataset");
  // Use the list of sample names to populate the select options
  d3.json("/names").then((sampleNames) => {
    sampleNames.forEach((sample) => {
      selector
        .append("option")
        .text(sample)
        .property("value", sample);
    });
    // Use the first sample from the list to build the initial plots
    const firstSample = sampleNames[0];
    buildCharts(firstSample);
    buildMetadata(firstSample);
    //buildGauge(firstSample);
  });
}

function optionChanged(newSample) {
  // Fetch new data each time a new sample is selected
  buildCharts(newSample);
  buildMetadata(newSample);
}

// Initialize the dashboard
init();
