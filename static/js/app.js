
// var tbody = d3.select("#test");

// d3.json("/getdata").then(function(data){
// 	console.log(data);
// 	data.forEach((d) => {
// 		var row = tbody.append("tr");
// 		Object.entries(d).forEach(([key, value]) => {
// 			var cell = tbody.append("td");
// 			cell.text(value);
//   });
// });
// })



//List Selection 

//  var dropDown = d3.select("body").append("select").attr("name", "name-list");
// d3.json("/getdata").then(function(data){
// 	var options = dropDown.selectAll("option").data(data)
//  						.enter()
//  						.append("option");
// 	 	options.text(function(d) {
// 			return d.App_date + " " + d.With_Doctor
// 	 })
// 	   .attr("value", function(d) {
// 			return d.App_date;
// });
// })

var form = d3.select("body").append("form");
d3.json("/getdata").then(function(data){

	labels = form.selectAll("label")
    .data(data)
    .enter()
    .append("label")
    .text(function(d) {return d;})
    .insert("input")
    .attr({
        type: "radio",
        class: "shape",
        name: "selection",
        value: function(d, i) {return i;}
    })
})



