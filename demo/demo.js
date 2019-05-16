
function initDemoMap(){

    var Esri_WorldImagery = L.tileLayer('http://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', 
    {
        // attribution: 'Tiles &copy; Esri &mdash; Source: Esri, i-cubed, USDA, USGS, ' +
        // 'AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community'
        attribution: 'DEVELOPMENT VERSION'
    });

    var Esri_DarkGreyCanvas = L.tileLayer(
        "http://{s}.sm.mapstack.stamen.com/" +
        "(toner-lite,$fff[difference],$fff[@23],$fff[hsl-saturation@20])/" +
        "{z}/{x}/{y}.png",
        {
            // attribution: 'Tiles &copy; Esri &mdash; Esri, DeLorme, NAVTEQ, TomTom, Intermap, iPC, USGS, FAO, ' +
            // 'NPS, NRCAN, GeoBase, Kadaster NL, Ordnance Survey, Esri Japan, METI, Esri China (Hong Kong), and the GIS User Community'
            attribution: 'DEVELOPMENT VERSION'
        }
    );

    var baseLayers = {
    	"Grey Canvas": Esri_DarkGreyCanvas,
        "Satellite": Esri_WorldImagery,        
    };

    var map = L.map('map', {
        layers: [ Esri_WorldImagery ]
    });

    var layerControl = L.control.layers(baseLayers);
    layerControl.addTo(map);
    map.setView([37, 188], 3);

    return {
        map: map,
        layerControl: layerControl
    };
}

// demo map
var self = this;
var mapStuff = initDemoMap();
var map = mapStuff.map;
var layerControl = mapStuff.layerControl;
var velocityLayer_10m;
var velocityLayer_250mb;
// var WIND_DATA = {
// 	10m_above_ground: '2019050706_10m.json',
// 	250mb: '2019050706.json'
// };
// var WIND_LAYER = {
// 	10m_above_ground: velocityLayer_10m,
// 	250mb: velocityLayer_250mb
// }
var p;
var ps;
var initWind = function(){
	// load data (u, v grids) from somewhere (e.g. https://github.com/danwild/wind-js-server)
	
	$.getJSON('2019050706_10m.json', function (data) {
		self.velocityLayer_10m = L.velocityLayer({
			displayValues: true,
			displayOptions: {
				velocityType: '10m_above_ground',
				displayPosition: 'bottomleft',
				displayEmptyString: 'No wind data'
			},
			data: data,
			maxVelocity: 10
		});
		console.log(self.velocityLayer_10m)
		layerControl.addOverlay(velocityLayer_10m, 'Wind -10m');
		// velocityLayer_10m.addTo(self.map);
	});
	$.getJSON('2019050706.json', function (data) {

		self.velocityLayer_250mb = L.velocityLayer({
			displayValues: true,
			displayOptions: {
				velocityType: '250mb',
				displayPosition: 'bottomleft',
				displayEmptyString: 'No wind data'
			},
			data: data,
			maxVelocity: 15
		});
		layerControl.addOverlay(velocityLayer_250mb, 'Wind -250mb');
	});

};
var switchLayer = function(point, nextLayer){
	console.log(nextLayer);
	nextLayer.options.test = 1;
	nextLayer.options._clickPostion.lat = point[0];
	nextLayer.options._clickPostion.lng = point[1];
	nextLayer.options._allowClick = 1;
	console.log(nextLayer);
	nextLayer.addTo(self.map);
}
var timer_10m = setInterval(function(){
	var status = velocityLayer_10m._pathStatus;
	var point = velocityLayer_10m._getPathEnd();
	// ps = velocityLayer_10m._path;
	if(status){
		console.log('Last Point: ' + point);
		clearInterval(timer_10m);
		console.log('timer clear');
		switchLayer(point, self.velocityLayer_250mb);
	};
},2000);

initWind();



