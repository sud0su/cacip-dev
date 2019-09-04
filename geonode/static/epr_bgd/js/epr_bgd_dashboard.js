function select_region(code){
	if (code == "Ukhia" || code == "Teknaf") {
		$(".province-dropdown").select2('val', code);
	} else if (code > 34 && code < 1000) {
		$(".dist-dropdown").select2('val', code);
		prov_code = code.substring(0,1);
		$(".province-dropdown").select2('val', prov_code);
	}else{
		$(".dist-dropdown").select2('val', code);
		prov_code = code.substring(0,2);
		console.log(prov_code);
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

	// $('.area-dropdown.district').select2({
	// 	placeholder: "Select District"
	// });

	// $('.area-dropdown.upazila').select2({
	// 	placeholder: "Select Upazilla"
	// });

	// $('.area-dropdown.union').select2({
	// 	placeholder: "Select Union"
	// });

	// $('.area-dropdown').on('change', function (e) {
	// 	jump_url(e.val);
	// });

	$('.province-dropdown').on('change', function (e) {
		jump_url(e.val);
		console.log('ubah' + e);
	});

	$('.dist-dropdown').on('change', function (e) {
		jump_url(e.val);
	});

	var code_region = getParameterByName("code");
	console.log(code_region);
	if (code_region == null) {
		$(".dist-dropdown").hide();
	}else {
		select_region(code_region);
	}
	if (typeof select2_region === "function") { 
		select2_region();
	}
}

function addUpdateUrlParameter(url, param, value) {
	if (url.indexOf(param) == -1) {
		return url+'&'+param+'='+value;
	}
	else {
		return updateUrlParameter(url, param, value);
	}
}

function init_select2_reporthub_filter(){
	$('.organization-dropdown').select2({
		placeholder: "Select Organization",
	});

	$('.donor-dropdown').select2({
		placeholder: "Select Donor"
	});

	$('.cluster_id-dropdown').select2({
		placeholder: "Select Cluster"
	});

	$('.unit_type_id-dropdown').select2({
		placeholder: "Select Unit Type"
	});

	// $('.organization-dropdown').select2('val', selected_organization);
	// $('.donor-dropdown').select2('val', selected_donor);
	// $('.cluster_id-dropdown').select2('val', selected_cluster_id);
	// $('.unit_type_id-dropdown').select2('val', selected_unit_type_id);
	
	var url = $(location).attr("href");
	console.log(url);

	var org = getParameterByName("organization");
	var donor = getParameterByName("donor");
	var cluster = getParameterByName("cluster_id");
	var unit = getParameterByName("unit_type_id");

	var org_array = [];
	var donor_array = [];
	var cluster_array = [];

	current_selection_org = [];
	current_selection_donor = [];
	current_selection_cluster = [];
	current_selection_unit = [];

	// $('.organization-dropdown').on('select2-selecting', function (e) {
	// 	console.log(e.val);
	// 	org_array = e.val;
	// 	// console.log(url);

	// 	// // type_org += e.val;
	// 	// if (org == null){
	// 	// 	// url += '&organization='+ e.val;
	// 	// }  else {
	// 	// 	// url = updateUrlParameter(url, 'organization', e.val);
	// 	// }
		
	// 	// console.log(url);
	// });

	// $('.organization-dropdown').on('select2-selecting', function (e) {
	// 	org_array = e.val;
	// 	console.log(org_array);
	// });

	// $('.donor-dropdown').on('select2-selecting', function (e) {
	// 	donor_array = e.val;
	// 	console.log(donor_array);
	// });

	// $('.cluster_id-dropdown').on('select2-selecting', function (e) {
	// 	cluster_array = e.val;
	// 	console.log(cluster_array);
	// });

	// $('.organization-dropdown').on('change', function (e) {
	// 	org_array = e.val;
	// 	console.log(org_array);
	// });

	// $('.donor-dropdown').on('change', function (e) {
	// 	donor_array = e.val;
	// 	console.log(donor_array);
	// });

	// $('.cluster_id-dropdown').on('change', function (e) {
	// 	cluster_array = e.val;
	// 	console.log(cluster_array);
	// });

	var reportrange = getParameterByName("reporting_period");
	start_reporting_date = $("#start_date_report").data("DateTimePicker").date();
	end_reporting_date = $("#end_date_report").data("DateTimePicker").date();

	if (start_reporting_date != null){
		start_reporting_date_formatted = start_reporting_date.format('YYYY-MM-DD');
	}

	if (end_reporting_date != null){
		end_reporting_date_formatted = end_reporting_date.format('YYYY-MM-DD');
	}

	// Linking the date
	$("#start_date_report").on("dp.change", function (e) {
		$('#end_date_report').data("DateTimePicker").minDate(e.date);
		start_reporting_date_formatted = $("#start_date_report").data("DateTimePicker").date().format('YYYY-MM-DD');
		console.log(url);
		console.log(reportrange);
		console.log(start_reporting_date_formatted);
	});
	$("#end_date_report").on("dp.change", function (e) {
		$('#start_date_report').data("DateTimePicker").maxDate(e.date);
		if(start_reporting_date == null ){
			$('#start_date_report').data("DateTimePicker").defaultDate(e.date);
		}
		start_reporting_date_formatted = $("#start_date_report").data("DateTimePicker").date().format('YYYY-MM-DD');
		end_reporting_date_formatted = $("#end_date_report").data("DateTimePicker").date().format('YYYY-MM-DD');
		console.log(url);
		console.log(reportrange);
		console.log(end_reporting_date_formatted);
	});


	$('#add_filter').on('click', function(event) {
		type_org = '';
		// type_org += org_array;

		type_donor = '';
		// type_donor += donor_array;

		type_cluster = '';
		// type_cluster += cluster_array;

		type_unit = '';
		
		console.log(type_org);
		console.log(type_donor);
		console.log(type_cluster);

		current_selection_org = $(".organization-dropdown").select2("val");
		current_selection_donor = $(".donor-dropdown").select2("val");
		current_selection_cluster = $(".cluster_id-dropdown").select2("val");
		current_selection_unit = $(".unit_type_id-dropdown").select2("val");

		console.log(current_selection_org);
		console.log(current_selection_donor);
		console.log(current_selection_cluster);

		if(current_selection_org != ''){
			console.log('ga kosong');
			console.log(type_org);
			type_org += current_selection_org;
			console.log(type_org);
		}

		if(current_selection_donor != ''){
			console.log('ga kosong');
			console.log(type_donor);
			type_donor += current_selection_donor;
			console.log(type_donor);
		}

		if(current_selection_cluster != ''){
			console.log('ga kosong');
			console.log(type_cluster);
			type_cluster += current_selection_cluster;
			console.log(type_cluster);
		}

		if(current_selection_unit != ''){
			console.log('ga kosong');
			console.log(type_unit);
			type_unit += current_selection_unit;
			console.log(type_unit);
		}

		console.log(url);

		if (type_org != ''){
			console.log(org);
			console.log(type_org);
			console.log(url);
			if (org == null){
				url += '&organization='+ type_org;
			}  else {
				url = updateUrlParameter(url, 'organization', type_org);
			}
		}else {
			url = removeParam('organization', url);
		}

		if (type_donor != ''){
			console.log(donor);
			console.log(type_donor);
			if (donor == null){
				url += '&donor='+ type_donor;
			}  else {
				url = updateUrlParameter(url, 'donor', type_donor);
			}
		}else {
			url = removeParam('donor', url);
		}

		// if (type_cluster != ''){
		// 	console.log(cluster);
		// 	console.log(type_cluster);
		// 	if (cluster == null){
		// 		url += '&cluster_id='+ type_cluster;
		// 	}  else {
		// 		url = updateUrlParameter(url, 'cluster_id', type_cluster);
		// 	}
		// }else {
		// 	url = removeParam('cluster_id', url);
		// }

		if (type_unit != ''){
			console.log(unit);
			console.log(type_unit);
			if (unit == null){
				url += '&unit_type_id='+ type_unit;
			}  else {
				url = updateUrlParameter(url, 'unit_type_id', type_unit);
			}
		}else {
			url = removeParam('unit_type_id', url);
		}

		if (reportrange == null){
			url += '&reporting_period='+ start_reporting_date_formatted +','+ end_reporting_date_formatted;
		}  else {
			url = updateUrlParameter(url, 'reporting_period', start_reporting_date_formatted +','+ end_reporting_date_formatted);
		}

		console.log(url);

		window.document.location = url;
	});
}

function init_date_range_report() {
	$('#start_date_report').datetimepicker({
		// enabledDates: available_date,
		defaultDate: selected_reporting_period[0],
		viewMode: 'months',
		format: 'DD/MM/YYYY',
		maxDate: new Date(),
		useCurrent: false
	});

	$('#end_date_report').datetimepicker({
		// enabledDates: available_date,
		defaultDate : selected_reporting_period[1],
		viewMode: 'months',
		format: 'DD/MM/YYYY',
		maxDate: new Date(),
		useCurrent: false
	});

	// $('#reporting_period').datetimepicker({
	// 	viewMode: 'months',
	// 	format: 'MM/YYYY'
	// });

	// $("#reporting_period").on("dp.change", function (e) {
	// 	var reporting_date = $("#reporting_period").data("DateTimePicker").date().format('YYYY-MM-DD');
	// 	console.log(url);
	// 	console.log(reportrange);
	// 	console.log(reporting_date);
	// 	if (reportrange == null){
	// 		url += '&reporting_period='+ reporting_date;
	// 		// window.document.location = url+'&reporting_period='+picker.startDate.format('YYYY-MM-DD')+','+picker.endDate.format('YYYY-MM-DD');
	// 	}  else {
	// 		url = updateUrlParameter(url, 'reporting_period', reporting_date);
	// 		// window.document.location = url;
	// 	}
	// 	console.log(url);
	// 	// window.document.location = url;
	// });
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
		}],

		"initComplete": function(settings, json) {
			var api = this.api();
			var colLength = api.columns().count();

			for (i = 1; i < colLength; i++) {
				this_footer = $(api.column(i).footer());
				dispData = humanizeFormatter(this_footer.html());
				if(this_footer.attr('class') == 'hum'){
					this_footer.html(dispData);
				}
			}
		}
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
				// console.log(type);
				// console.log(data);
				if (type == 'display') {return humanizeFormatter(data);}
				return data;
			},
			"cellType": "th",
			"targets": 'hum'
		}],

		"initComplete": function(settings, json) {
			var api = this.api();
			var colLength = api.columns().count();

			for (i = 1; i < colLength; i++) {
				this_footer = $(api.column(i).footer());
				dispData = humanizeFormatter(this_footer.html());
				console.log(this_footer);
				console.log(this_footer.attr('class'));
				console.log(dispData);
				if(this_footer.attr('class') == 'hum'){
					console.log(this_footer);
					this_footer.html(dispData);
				}
			}
		}
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
					allowOverlap: false,
					connectorPadding: 3,
					distance: 10,
					connectorShape: 'crookedLine',
					crookDistance: '100%'
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
					console.log(this);
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

	// Object Pyramid Bar chart
	function pyramid_bar_chart(id_val, color_val, colorPoint_val, legend_val, y_title, x_title, data_neg_val, data_pos_val, title_val, show_title_val, data_title_neg, data_title_pos){
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
			xAxis: [{
				title: 'Age',
				categories: y_title,
				reversed: false,
				labels: {
					step: 1
				}
			}, { // mirror axis on right side
				title: 'Age',
				opposite: true,
				reversed: false,
				categories: y_title,
				linkedTo: 0,
				labels: {
					step: 1
				}
			}],
			yAxis: {
				title: {
					text: x_title,
					enabled: false
				},
				labels: {
					formatter: function () {
						return humanizeFormatter(Math.abs(this.value));
					}
				}
			},
			tooltip: {
				formatter: function() {
					console.log(this);
					return '<b>' + this.series.name + ', age ' + this.point.category + '</b><br/>' + 'Population: ' + humanizeFormatter(Math.abs(this.point.y));
					// return '<b>'+ this.x +'</b>: '+ humanizeFormatter(this.y);
				}
			},
			legend:{
				enabled: legend_val
			},
			plotOptions:{
				series: {
					stacking: 'normal'
				}
				// bar: {
				// 	colorByPoint: colorPoint_val,
				// 	dataLabels: {
				// 		enabled: true,
				// 		formatter: function() {
				// 			return humanizeFormatter(this.y);
				// 		}
				// 	}
				// }
			},
			colors: color_val,
			// series: [{
			// 	// name: 'Population',
			// 	data: data_val
			// }]
			series: 
				[{
					name: data_title_neg,
					data: [
						-13747, -56039, -80028, 
						-49602, -173328, -14074
					]
					// data: data_neg_val
				}, {
					name: data_title_pos,
					data: [
						13811, 58275, 84495, 
						50207, 137263, 12744
					]
					// data: data_pos_val
				}]
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
				size: '60%',
				innerSize: '65%',
				showInLegend:true
			}]
		});
	}

	// Object Combination Donut & Bar chart
	function bar_donut_chart(id_val, color_val, data_val_donut, data_val_bar, data_sum_bar, title_val, show_title_val, colorPoint_val, y_title, x_title){
		$(id_val).highcharts({
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
			colors: color_val,
			series: [
				{
					type: 'bar',
					name: '...',
					colorByPoint: colorPoint_val,
					data: data_val_bar,
					showInLegend: false,
					tooltip: {
						pointFormatter: function() {
							console.log(this);
							var percentage = (this.y / data_sum_bar) * 100;
							return humanizeFormatter(this.y) +' (' + Highcharts.numberFormat(percentage,2,'.') + '%)';
						}
					},
					dataLabels: {
						enabled: true,
						formatter: function() {
							var percentage = (this.y / data_sum_bar) * 100;
							return humanizeFormatter(this.y) +'<br/>(' + Highcharts.numberFormat(percentage,2,'.') + '%)';
						}
					}
				},
				{
					type: 'pie',
					name: '...',
					data: data_val_donut,
					center: ['95%', '10%'],
					size: '30%',
					innerSize: '55%',
					showInLegend: true,
					tooltip: {
						pointFormatter: pie_label
					},
					dataLabels: {
						enabled: false,
						formatter: pie_label
					}
				}
			]
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

	$('.pyramid-chart').each(function(){
		console.log(this.id);
		var id_chart = '#' + this.id;
		color_chart = $(id_chart).attr('data-color'); 
		var dataLeft_chart = $(id_chart).data("val-left");
		var dataRight_chart = $(id_chart).data("val-right");

		var yAxis_chart = $(id_chart).data("yaxis");
		var xAxis_chart = $(id_chart).data("xaxis");
		var colorPoint_bool = $(id_chart).data("colorpoint");
		var legend_bool = $(id_chart).data("legend");
		var titleLeft_chart = $(id_chart).attr('data-title-left');
		var titleRight_chart = $(id_chart).attr('data-title-right');
		var title_chart = $(id_chart).attr('data-title');
		var show_title_chart = $(id_chart).attr('data-show-title');

		selected_color = colorChart[color_chart];

		console.log(id_chart);
		console.log(color_chart);
		console.log(yAxis_chart);
		console.log(xAxis_chart);
		console.log(titleLeft_chart);
		console.log(dataLeft_chart);
		console.log(titleRight_chart);
		console.log(dataRight_chart);

		console.log(selected_color);

		pyramid_bar_chart(id_chart, selected_color, colorPoint_bool, legend_bool, yAxis_chart, xAxis_chart, dataLeft_chart, dataRight_chart, title_chart, show_title_chart, titleLeft_chart, titleRight_chart );

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

	$('.combi-bar-donut-chart').each(function(){
		console.log(this.id);
		var id_chart = '#' + this.id;
		color_chart = $(id_chart).attr('data-color'); 
		// var color_chart = $(id_chart).data("color");
		var data_chart_donut = $(id_chart).data("val-donut");
		var data_chart_bar = $(id_chart).data("val-bar");
		// id_chart.attr('data-chart');
		var title_chart = $(id_chart).attr('data-title');
		var show_title_chart = $(id_chart).attr('data-show-title');

		var colorPoint_bool = $(id_chart).data("colorpoint");
		var xAxis_chart = $(id_chart).data("xaxis");
		var yAxis_chart = $(id_chart).data("yaxis");

		selected_color = colorChart[color_chart];

		var data_sum_bar = 0;
		for (var i=0;i < data_chart_donut.length;i++) {
			data_sum_bar += data_chart_donut[i][1];
		}

		console.log(id_chart);
		console.log(color_chart);
		console.log(data_chart_donut);
		console.log(data_chart_bar);
		console.log(data_sum_bar);
		console.log(selected_color);

		bar_donut_chart(id_chart, selected_color, data_chart_donut, data_chart_bar, data_sum_bar, title_chart, show_title_chart, colorPoint_bool, yAxis_chart, xAxis_chart);

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
	init_date_range_report();
	init_select2_reporthub_filter();
});