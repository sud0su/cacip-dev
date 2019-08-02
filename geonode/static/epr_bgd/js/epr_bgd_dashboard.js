function select_region(code){
	if (code <= 34) {
		$(".province-dropdown").select2('val', code);
	} else if (code > 34 && code < 1000) {
		$(".dist-dropdown").select2('val', code);
		prov_code = code.substring(0,1);
		$(".province-dropdown").select2('val', prov_code);
	}else{
		$(".dist-dropdown").select2('val', code);
		prov_code = code.substring(0,2);
		$(".province-dropdown").select2('val', prov_code);
	}
}

function init_select2_region(){
	$('.province-dropdown').select2({
		placeholder: "Select Upazilla"
	});
	$('.dist-dropdown').select2({
		placeholder: "Select Union"
	});

	$('.province-dropdown').on('change', function (e) {
		jump_url(e.val);
	});

	$('.dist-dropdown').on('change', function (e) {
		jump_url(e.val);
	});

	var code_region = getParameterByName("code");
	if (code_region == null) {
		$(".dist-dropdown").hide();
	}else {
		select_region(code_region);
	}
}

// Humanizer
function humanizeFormatter(value){
	// console.log(value)
	var v= value;
	if(v>=1000 && v<1000000){
		return (parseFloat((v/1000).toPrecision(3)))+' K'
		// return (parseFloat((v/1000).toFixed(1)))+' K'
	}
	else if (v>=1000000 && v<1000000000) {
		return (parseFloat((v/1000000).toPrecision(3)))+' M'
		// return (parseFloat((v/1000000).toFixed(1)))+' M'
	}else{
		if (v==null || isNaN(parseFloat(v))) {
			v=0;
		}
		// console.log(parseFloat((v).toPrecision(3)));
		return (parseFloat((v*1).toPrecision(3)))
		// return (parseFloat((v).toFixed(1)))
	}
}

// Datatables
function init_datatable(){
	$.fn.dataTable.moment( 'MMM D, YYYY' );

	$('.print').DataTable({
		"ordering": false, //do this when print
		"paging": false, //do this when print
		"info": false, //do this when print
		"searching": false, //do this when print
		dom: 't', //do this when print

		"columnDefs": [{
			"render": function (data, type, row){
				if (type == 'display') {return humanizeFormatter(data);}
				return data;
			},
			"targets": 'hum'
		}]
	});

	$('.online').DataTable({
		dom: 'Bfrtip',
		// pagingType: "full_numbers",
		buttons: [
			{
				extend: "copy",
				className: "btn btn-default btn-sm"
			},
			{
				extend: "csv",
				filename: 'ASDC Data',
				className: "btn btn-default btn-sm"
			},
			{
				extend: "excel",
				filename: 'ASDC Data',
				className: "btn btn-default btn-sm"
			},
			{
				extend: "print",
				filename: 'ASDC Data',
				// customize: 
				// 	function ( win ) {
	      //               $(win.document.body)
	      //                   .css( 'font-size', '10pt' )
	      //                   .prepend(
	      //                   	'<img src="static/v2/images/usaid-logo.png" style="position:absolute; top:0; left:0;" />')
	      //                   .prepend(
	      //                       '<img src="static/v2/images/iMMAP.png" style="position:absolute; top:0; left:220px;" />'
	      //                   );
	 
	      //               $(win.document.body).find( 'table' )
	      //                   .addClass( 'compact' )
	      //                   .css( 'font-size', 'inherit' );
	      //           },
				className: "btn btn-default btn-sm"
			}
			// {
			//   extend: "colvis"
			//   className: "btn-sm"
			// }
		],

		"columnDefs": [{
			"render": function (data, type, row){
				if (type == 'display') {return humanizeFormatter(data);}
				return data;
			},
			"targets": 'hum'
		}]
	});

	$('.online_security').DataTable({
		"ordering": false,
		// "pageLength": 30,
		dom: 'Bfrtip',
		buttons: [
			{
				extend: "copy",
				className: "btn-sm"
			},
			{
				extend: "csv",
				className: "btn-sm"
			},
			{
				extend: "excel",
				className: "btn-sm"
			},
			{
				extend: "print",
				className: "btn-sm"
			},
			// {
			//   extend: "colvis"
			//   className: "btn-sm"
			// }
		],

		"columnDefs": [{
			"render": function (data, type, row){
				if (type == 'display') {return humanizeFormatter(data);}
				return data;
			},
			"targets": 'hum'
		}]
	});

	$("button").removeClass("dt-button");
}

// Chart
function init_chart(){
	colorBarDefault= ["#1F6EBC"];
	colorBarOther= ['#b40002', '#f1000f', '#ff5c3c', '#ffb89c', '#ffe4d7' ];
	colorDonutDefault = ['#1F6EBC', '#ccc'];
	colorAccessibility=[
	    '#c0fee5', /*'#99fcff',*/ '#94fdd5', '#75fcc9', /*'#fffb46',*/ '#fff327', /*'#fffc79', */ /*'#ffdd72',*/
	    /*'#ffd341',*/ '#ffc43b', '#ff9c00', '#ffc9c7', '#ffa8a4', /*'#fdbbac',*/ '#ff9d99' /*'#ffa19a'*/
	];
	// colorFloodRiskForecast = ['#abd9e9', '#74add1', '#4575b4'];
	colorFloodRiskForecast = ['#acd7ff', '#79bfff', '#46a7ff'];
	colorFloodLikelihoodForecast = ['#abedfd', '#c8eb8f', '#fff37f', '#feb24c', '#ff7f80'];
	colorFloodRisk = ['#addbff', '#68a4de', '#1f6ebc', '#ddd'];
	colorAvaRisk = ['#addbff', '#68a4de', '#ddd'];
	colorDrought = [ '#ffef00', '#bdda57' , '#ffca28', '#ef5350', '#212121', '#ccc' ];
	colorLandslide = [ '#43A047', '#FDD835' , '#FB8C00', '#e84c3d', '#ccc' ];
	colorMercalli = [
		// /*'#eeeeee', '#bfccff',*/ '#9999ff', '#88ffff', '#7df894', '#ffff00',
		// '#ffdd00', '#ff9100', '#ff0000', '#dd0000', '#880000', '#440000'

		'#d4e6f1', '#c2fcf7', '#6dffb6', '#ffff5c',
		 '#ffe74c', '#ffc600', '#ff5751', '#e84c3d'
	];
	colorDefault = ['#ffaaab', '#ff6264', '#d13c3e', '#b92527'];

	var colorTimes =
  		function(params){
  			return colorAccessibility[params.dataIndex]
		}

	colorChart={
		'colorDefault': colorBarOther,
		'colorBar': colorBarDefault,
		'colorAccess': colorAccessibility,
		'colorDonut' : colorDonutDefault,
		'colorFloodRiskForecast' : colorFloodRiskForecast,
		'colorFloodLikelihoodForecast' : colorFloodLikelihoodForecast,
		'colorFloodRisk': colorFloodRisk,
		'colorAvaRisk': colorAvaRisk,
		'colorDrought': colorDrought,
		'colorLandslide': colorLandslide,
		'colorEarthquake': colorMercalli,
		'colorSecurity': colorDefault
	}

	function pie_label() {
		if (this.y > 0){
			// return '<b>' + this.key + '</b> : ' + humanizeFormatter(this.y) + '<br/>(' + Highcharts.numberFormat(this.percentage, 2) + '%)';
			return humanizeFormatter(this.y) + '<br/>(' + Highcharts.numberFormat(this.percentage, 2) + '%)';
		}
	}


	Highcharts.theme = {
		chart: {
			style: {
				fontFamily: '"Arial", Verdana, sans-serif'
			}
		},
		title: {
			text: null,
			verticalAlign: 'bottom',
			style: {
				color: '#424242',
				font: 'bold 13px "Trebuchet MS", Verdana, sans-serif'
			}
		},
		subtitle: {
			style: {
				color: '#424242'
			}
		},
		xAxis: {
			
		},
		yAxis: {
			labels: {
				overflow: 'justify'
			},
			title: {
				align: 'high',
				style: {
					// color: '#A0A0A3'
				}
			}
		},
		tooltip: {
			
		},
		plotOptions: {
			series: {
				animation: true
				// color: '#c62828',
			},
			bar: {
				// color: '#c62828',
				dataLabels: {
					enabled: true,
					formatter: function() {
						// return humanizeFormatter(this.y);
					}
				}
			},
			pie: {
				dataLabels: {
					enabled: true,
					softConnector: false,
					// formatter: function() {
					// 	if (this.y > 0){
					// 		return humanizeFormatter(this.y) + '<br/>' + Highcharts.numberFormat(this.percentage, 2) + '%';
					// 	}
					// }
					// formatter: pie_label
				}
			}
		},
		legend: {
			enabled: true
		},
		credits: {
			enabled: false
		},
		labels: {
		},

		drilldown: {
		},

		navigation: {
		},

		// scroll charts
		rangeSelector: {
			
		},

		navigator: {
			
		},

		scrollbar: {
			
		}

		// special colors for some of the
		// legendBackgroundColor: 'rgba(0, 0, 0, 0.5)',
		// background2: '#505053',
		// dataLabelsColor: '#B0B0B3',
		// textColor: '#C0C0C0',
		// contrastTextColor: '#F0F0F3',
		// maskColor: 'rgba(255,255,255,0.3)'
	};

	// Apply the theme
	Highcharts.setOptions(Highcharts.theme);

	// Object Line chart
	function line_chart(id_val, color_val, colorPoint_val, legend_val, y_title, x_title, data_val, title_val, show_title_val){
		$(id_val).highcharts({
			chart: {
				type: 'line'
			},
			title: {
				text: title_val,
				style: {
					display: show_title_val
				}
			},
			xAxis: {
				type: 'datetime'
				// categories: y_title
			},
			yAxis: {
				title: {
					text: x_title
				},
				type: 'logarithmic'
			},
			tooltip: {
				formatter: function() {
					return '<b>'+ this.x +'</b>: '+ humanizeFormatter(this.y);
				}
			},
			legend:{
				enabled: legend_val
			},
			plotOptions:{
				bar: {
					colorByPoint: colorPoint_val,
					dataLabels: {
						enabled: true,
						formatter: function() {
							return humanizeFormatter(this.y);
						}
					}
				}
			},
			colors: color_val,
			// series: [{
			// 	// name: 'Population',
			// 	data: data_val
			// }]
			series: data_val
		});
	}

	// Object Bar chart
	function bar_chart(id_val, color_val, colorPoint_val, legend_val, y_title, x_title, data_val, title_val, show_title_val){
		$(id_val).highcharts({
			chart: {
				type: 'bar'
			},
			title: {
				text: title_val,
				style: {
					display: show_title_val
				}
			},
			xAxis: {
				categories: y_title
			},
			yAxis: {
				title: {
					text: x_title
				},
				type: 'logarithmic'
			},
			tooltip: {
				formatter: function() {
					return '<b>'+ this.x +'</b>: '+ humanizeFormatter(this.y);
				}
			},
			legend:{
				enabled: legend_val
			},
			plotOptions:{
				bar: {
					colorByPoint: colorPoint_val,
					dataLabels: {
						enabled: true,
						formatter: function() {
							return humanizeFormatter(this.y);
						}
					}
				}
			},
			colors: color_val,
			// series: [{
			// 	// name: 'Population',
			// 	data: data_val
			// }]
			series: data_val
		});
	}

	// Object Donut chart
	function donut_chart(id_val, color_val, data_val, title_val, show_title_val){
		$(id_val).highcharts({
			chart: {
				type: 'pie'
			},
			title: {
				text: title_val,
				style: {
					display: show_title_val
				}
			},
			tooltip: {
				formatter: pie_label
			},
			legend:{
				floating: true,
				align: 'left',
				verticalAlign: 'top',
				layout: 'vertical'
			},
			colors: color_val,
			series: [{
				name: 'Flood Risk Population',
				data: data_val,
				dataLabels:{
					formatter: pie_label
				},
				size: '70%',
				innerSize: '65%',
				showInLegend:true
			}]
		});
	}

	// Object Stacked Bar chart
	function bar_stacked_col_chart(id_val, color_val, data_title, data_val){
		$(id_val).highcharts({
			chart: {
				type: 'column'
			},
			xAxis: {
				categories: data_title
			},
			yAxis: {
				min: 0,
				stackLabels:{
					enabled: true
				},
				title: {
					enabled: false
					// text: 'Population'
				}
			},
			tooltip: {
				formatter: function() {
					return '<b>'+ this.x +'</b>: '+ humanizeFormatter(this.y);
				}
			},
			legend:{

			},
			plotOptions: {
				column: {
					stacking: 'normal',
					dataLabels: {
						enabled: true,
						color: (Highcharts.theme && Highcharts.theme.dataLabelsColor) || 'white'
					}
				}
			},
			colors: color_val,
			series: data_val
		});
	}

	// Object Stacked Bar chart in Percent
	function bar_stacked_percent_chart(id_val, color_val, data_title, data_val){
		$(id_val).highcharts({
			chart: {
				type: 'bar'
			},
			xAxis: {
				categories: data_title
			},
			yAxis: {
				reversedStacks: false,
				min: 0,
				title: {
					text: "Percentage (%)"
				}
			},
			tooltip: {
				formatter: function() {
					console.log(this);
					return '<b>'+ this.x +'</b>: '+ humanizeFormatter(this.y) +' ('+ (this.percentage).toFixed(2) + '%)';
				}
			},
			legend:{

			},
			plotOptions: {
				series: {
					stacking: 'percent',
					dataLabels: {
						enabled: true,
						color: (Highcharts.theme && Highcharts.theme.dataLabelsColor) || 'white'
					}
				}
			},
			colors: color_val,
			series: data_val
		});
	}

	// Object Stacked Bar chart
	function polar_chart(id_val, color_val, data_title, data_val){
		$(id_val).highcharts({
			chart: {
				polar: true
			},
			xAxis: {
				categories: data_title
			},
			yAxis: {
				type: 'logarithmic',
				tickInterval: 1,
				title: {
					enabled: false
				}
			},
			tooltip: {
				formatter: function() {
					console.log(this);
					return '<b>'+ this.x +'</b>: '+ humanizeFormatter(this.y);
				}
			},
			legend:{

			},
			plotOptions: {
				
			},
			colors: color_val,
			series: data_val
			
		});
	}

	// Object Spline Chart
	function spline_chart(id_val, color_val, colorPoint_val, legend_val, y_title, x_title, data_val, title_val, show_title_val){
		$(id_val).highcharts('StockChart',{
			rangeSelector: {
				selected: 5,
			    // buttonTheme: {
			    //     width: 60
			    // },
			},

			xAxis: {
				type: 'datetime',
				minTickInterval: moment.duration(1, 'month').milliseconds(),
				// dateTimeLabelFormats: {
				//     millisecond: '%H:%M:%S.%L'
				// },
				labels: {
					rotation: 35
				}
			},

			time:{
				useUTC: false,
				// timezoneOffset: 7 * 60
			},

			tooltip: {
				split: true,
				// crosshairs: true,
				formatter: function() {
					var s = [];

					console.log(this);
					// s.push(Highcharts.dateFormat('%A, %b %e, %Y %H:%M', this.x));   // Use UTC
					s.push(moment(this.x).format("YYYY-MM-DD HH:mm a"));            // Use Local Time

					this.points.forEach(function(point) {
						s.push('<b>' + point.series.name + '</b>: ' + point.y);
					});

					return s;
				},
			},
			legend:{
				enabled: legend_val
			},

			// global: {
			//     useUTC: false
			// },

			colors: color_val,
			series: data_val
		});

		$( ".highcharts-range-selector" ).addClass( "browser-default" );

		// $(id_val).highcharts({
		// 	chart: {
		// 		polar: true
		// 	},
		// 	xAxis: {
		// 		categories: data_title
		// 	},
		// 	yAxis: {
		// 		type: 'logarithmic',
		// 		tickInterval: 1,
		// 		title: {
		// 			enabled: false
		// 		}
		// 	},
		// 	tooltip: {
		// 		formatter: function() {
		// 			console.log(this);
		// 			return '<b>'+ this.x +'</b>: '+ humanizeFormatter(this.y);
		// 		}
		// 	},
		// 	legend:{

		// 	},
		// 	plotOptions: {
				
		// 	},
		// 	colors: color_val,
		// 	series: data_val
			
		// });
	}

	$('.line-chart').each(function(){
		console.log(this.id);
		var id_chart = '#' + this.id;
		color_chart = $(id_chart).attr('data-color'); 
		var data_chart = $(id_chart).data("val");
		var yAxis_chart = $(id_chart).data("yaxis");
		var xAxis_chart = $(id_chart).data("xaxis");
		var colorPoint_bool = $(id_chart).data("colorpoint");
		var legend_bool = $(id_chart).data("legend");
		var title_chart = $(id_chart).attr('data-title');
		var show_title_chart = $(id_chart).attr('data-show-title');

		selected_color = colorChart[color_chart];

		console.log(id_chart);
		console.log(color_chart);
		console.log(data_chart);
		console.log(selected_color);
		console.log(yAxis_chart);

		line_chart(id_chart, selected_color, colorPoint_bool, legend_bool, yAxis_chart, xAxis_chart, data_chart, title_chart, show_title_chart);

	});

	$('.spline-chart').each(function(){
		console.log(this.id);
		var id_chart = '#' + this.id;
		color_chart = $(id_chart).attr('data-color'); 
		var data_chart = $(id_chart).data("val");
		var yAxis_chart = $(id_chart).data("yaxis");
		var xAxis_chart = $(id_chart).data("xaxis");
		var colorPoint_bool = $(id_chart).data("colorpoint");
		var legend_bool = $(id_chart).data("legend");
		var title_chart = $(id_chart).attr('data-title');
		var show_title_chart = $(id_chart).attr('data-show-title');

		selected_color = colorChart[color_chart];

		console.log(id_chart);
		console.log(color_chart);
		console.log(data_chart);
		console.log(selected_color);
		console.log(yAxis_chart);

		spline_chart(id_chart, selected_color, colorPoint_bool, legend_bool, yAxis_chart, xAxis_chart, data_chart, title_chart, show_title_chart);

	});

	$('.bar-chart').each(function(){
		console.log(this.id);
		var id_chart = '#' + this.id;
		color_chart = $(id_chart).attr('data-color'); 
		var data_chart = $(id_chart).data("val");
		var yAxis_chart = $(id_chart).data("yaxis");
		var xAxis_chart = $(id_chart).data("xaxis");
		var colorPoint_bool = $(id_chart).data("colorpoint");
		var legend_bool = $(id_chart).data("legend");
		var title_chart = $(id_chart).attr('data-title');
		var show_title_chart = $(id_chart).attr('data-show-title');

		selected_color = colorChart[color_chart];

		console.log(id_chart);
		console.log(color_chart);
		console.log(data_chart);
		console.log(selected_color);
		console.log(yAxis_chart);

		bar_chart(id_chart, selected_color, colorPoint_bool, legend_bool, yAxis_chart, xAxis_chart, data_chart, title_chart, show_title_chart);

	});

	$('.donut-chart').each(function(){
		console.log(this.id);
		var id_chart = '#' + this.id;
		color_chart = $(id_chart).attr('data-color'); 
		// var color_chart = $(id_chart).data("color");
		var data_chart = $(id_chart).data("val");
		// id_chart.attr('data-chart');
		var title_chart = $(id_chart).attr('data-title');
		var show_title_chart = $(id_chart).attr('data-show-title');

		selected_color = colorChart[color_chart];

		console.log(id_chart);
		console.log(color_chart);
		console.log(data_chart);
		console.log(selected_color);

		donut_chart(id_chart, selected_color, data_chart, title_chart, show_title_chart);

	});

	$('.bar-stacked-col-chart').each(function(){
		console.log(this.id);
		var id_chart = '#' + this.id;
		color_chart = $(id_chart).attr('data-color'); 
		var data_chart = $(id_chart).data("val");
		var xAxis_chart = $(id_chart).data("xaxis");

		selected_color = colorChart[color_chart];

		console.log(id_chart);
		console.log(color_chart);
		console.log(data_chart);
		console.log(selected_color);
		console.log(xAxis_chart);

		bar_stacked_col_chart(id_chart, selected_color, xAxis_chart, data_chart);

	});

	$('.bar-stacked-percent-chart').each(function(){
		console.log(this.id);
		var id_chart = '#' + this.id;
		color_chart = $(id_chart).attr('data-color'); 
		var data_chart = $(id_chart).data("val");
		var xAxis_chart = $(id_chart).data("xaxis");

		selected_color = colorChart[color_chart];

		console.log(id_chart);
		console.log(color_chart);
		console.log(data_chart);
		console.log(selected_color);
		console.log(xAxis_chart);

		bar_stacked_percent_chart(id_chart, selected_color, xAxis_chart, data_chart);

	});

	$('.polar-chart').each(function(){
		console.log(this.id);
		var id_chart = '#' + this.id;
		color_chart = $(id_chart).attr('data-color'); 
		var data_chart = $(id_chart).data("val");
		var xAxis_chart = $(id_chart).data("xaxis");

		selected_color = colorChart[color_chart];

		console.log(id_chart);
		console.log(color_chart);
		console.log(data_chart);
		console.log(selected_color);
		console.log(xAxis_chart);

		var isi_fix = [];
		for (i = 0; i < data_chart.length; i++) { 
			var isi = {
				name: data_chart[i].type,
				type: 'scatter',
				data: data_chart[i].data.map(function (p) {
					var radius = Math.log(p)*1.5;
					return {
						y: p,
						marker: {
							radius: (radius),
							symbol: 'circle'
						}
					}
				})
			}

			isi_fix.push(isi);
		}
		
		console.log(isi_fix);

		polar_chart(id_chart, selected_color, xAxis_chart, isi_fix);

	});
}

$(document).ready(function(){
	init_select2_region();
	init_datatable();
	init_chart();
});