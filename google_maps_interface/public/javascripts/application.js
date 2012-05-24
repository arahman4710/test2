var map;
var chk_changed=0;
var ListenerCity;
var stateMarker=[];
var logged_in=0;
var display_changed=0;
var tooltip=new Array();
var tooltips=new Array();
var Hmarker=new Array();
var region_tooltip=new Array();
var init_zoom=3;
var image="hotel_icon.png";
var paid_image_city="a-map_pin_green_blank.png";
var stateIcon="state.png";
var statecount=0;
var user_viewed_bounds;
var userPreference=new Array();
var region_center=[];
var region_container=new Array();
var region_overlay=[];
var panorama;
var paid_user_city=new Array();

CustomMarker.prototype = new google.maps.OverlayView();
var marker=[];
var markers = [];
var hotelMarkers=[];
var Bounds = new google.maps.LatLngBounds();
var Cbounds=new google.maps.LatLngBounds();
var i = 0,j=0;
var infowindow = new Array();    
var ICurrent;
var INE;
var ISW;
var IMaxLat;
var IMinLat;
var IMinLng;
var IMaxLng;


//  class defination for a custom marker and listeners for functionality

function CustomMarker(bounds,id , map,text) {
      this.bounds_ = bounds;
      this.map_ = map;
      this.text_ = text;
      this.id_ = id;
      this.div_ = null;
      this.setMap(map);
  }

  CustomMarker.prototype.onAdd = function() {

      var div = document.createElement('DIV');
      div.style.border = "solid";
      div.style.borderWidth = "3px";
      div.style.background = "#CCCCCC";
      div.style.position = "absolute";
      div.style.zIndex="1000";
      div.innerHTML = "<b>" + this.text_ + "</b>";
      div.style.textAlign = "center";
      div.setAttribute('id', this.id_);

      div.setOpacity(0.0);
      this.div_ = div;

      var panes = this.getPanes();
      panes.overlayImage.appendChild(this.div_);

  }

  CustomMarker.prototype.draw = function() {

      var overlayProjection = this.getProjection();
      var pos = overlayProjection.fromLatLngToDivPixel(this.bounds_);
      var div = this.div_;
      div.style.left = pos.x + 'px';
      div.style.top = pos.y + 'px';
  }

  CustomMarker.prototype.onRemove = function() {

      if (this.div_.parentNode) {
        this.div_.parentNode.removeChild(this.div_);
      }
  }

  CustomMarker.prototype.hide = function() {

      if (this.div_) {
          this.div_.style.visibility = "visible";
          new Effect.Opacity(this.div_, {from: 0.7, to: 0.0, duration: 0.7}); 
      }
  }

  CustomMarker.prototype.show = function() {

      if (this.div_) {
          new Effect.Opacity(this.div_, {from: 0.0, to: 0.7, duration: 0.7});
      }
  }
  CustomMarker.prototype.getPosition = function(){

      if (this.bounds_) {
        return this.bounds_;
      }
  }


CustomMarker.prototype.panToView = function() {
  var projection = this.getProjection();

  if (!projection) {
    // The map projection is not ready yet so do nothing
    return;
  }

  if (!this.div_) {
    // No Bubble yet so do nothing
    return;
  }
  var height = 10;
  var map = this.get('map');
  var mapDiv = map.getDiv();
  var mapHeight = mapDiv.offsetHeight;

  var latLng = this.getPosition();
  var centerPos = projection.fromLatLngToContainerPixel(map.getCenter());
  var pos = projection.fromLatLngToContainerPixel(latLng);

  // Find out how much space at the top is free
  var spaceTop = centerPos.y - height;

  // Fine out how much space at the bottom is free
  var spaceBottom = mapHeight - centerPos.y;

  var needsTop = spaceTop < 0;
  var deltaY = 0;

  if (needsTop) {
    spaceTop *= -1;
    deltaY = (spaceTop + spaceBottom) / 2;
  }

  pos.y -= deltaY;
  latLng = projection.fromContainerPixelToLatLng(pos);

  if (map.getCenter() != latLng) {
    map.panTo(latLng);
  }
};

//  extends google map polygon object functionality to include point-in-polygon search capabilities

if (!google.maps.Polygon.prototype.getBounds) {
  google.maps.Polygon.prototype.getBounds = function(latLng) {
    var bounds = new google.maps.LatLngBounds();
    var paths = this.getPaths();
    var path;

    for (var p = 0; p < paths.getLength(); p++) {
      path = paths.getAt(p);
      for (var i = 0; i < path.getLength(); i++) {
        bounds.extend(path.getAt(i));
      }
    }

    return bounds;
  }
}

// Polygon containsLatLng - method to determine if a latLng is within a polygon
google.maps.Polygon.prototype.containsLatLng = function(latLng) {
  // Exclude points outside of bounds as there is no way they are in the poly
  var bounds = this.getBounds();

  if(bounds != null && !bounds.contains(latLng)) {
    return false;
  }

  // Raycast point in polygon method
  var inPoly = false;

  var numPaths = this.getPaths().getLength();
  for(var p = 0; p < numPaths; p++) {
    var path = this.getPaths().getAt(p);
    var numPoints = path.getLength();
    var j = numPoints-1;

    for(var i=0; i < numPoints; i++) {
      var vertex1 = path.getAt(i);
      var vertex2 = path.getAt(j);

      if (vertex1.lng() < latLng.lng() && vertex2.lng() >= latLng.lng() || vertex2.lng() < latLng.lng() && vertex1.lng() >= latLng.lng())  {
        if (vertex1.lat() + (latLng.lng() - vertex1.lng()) / (vertex2.lng() - vertex1.lng()) * (vertex2.lat() - vertex1.lat()) < latLng.lat()) {
          inPoly = !inPoly;
        }
      }

      j = i;
    }
  }

  return inPoly;
}

function Markermouseover(event)
{
    new Effect.Opacity(this, {from: 0.7, to: 1.0, duration: 0.4});
}

//Rails related javascript function

function add_child(element, child_name, new_child) {
  $(child_name + '_children').insert({
    bottom: new_child.replace(/NEW_RECORD/g, new Date().getTime())
  });
}

//Rails related javascript function

function remove_child(element) {
  var hidden_field = $(element).previous("input[type=hidden]");
  if (hidden_field) {
    hidden_field.value = '1';
  }
  $(element).up(".child").hide();
}



//  This function is the entry point for the javascript file, call this function from the html page and make sure you have a div named 'map_canvas'

 function initialize() {

    var myLatlng = new google.maps.LatLng(49.037868,-104.677734);
    var myOptions = {
      zoom: 3,
      center: myLatlng,
      mapTypeId: google.maps.MapTypeId.ROADMAP
    }

    //  load map to div

    map = new google.maps.Map(document.getElementById("map_canvas"), myOptions);
    
    //  add extra plugins to the map for more feature

    map.enableKeyDragZoom({
            visualEnabled: true,
            visualPosition: google.maps.ControlPosition.LEFT,
            visualPositionOffset: new google.maps.Size(35, 0),
            visualPositionIndex: null,
            visualSprite: "http://maps.gstatic.com/mapfiles/ftr/controls/dragzoom_btn.png",
            visualSize: new google.maps.Size(20, 20),
            visualTips: {
             off: "Turn on",
             on: "Turn off"
            }
    });

    $('street_canvas').hide();

    //  Check user authentication from server side, in order to display relevant information on the map

    req = new Ajax.Request('/users/check_authentication', {
        method: 'post',
        onSuccess: function(transport) {
            var result = transport.responseText;
            var A = eval("("+result+")");
                logged_in=A[0];
                if(logged_in){

                    for(var h=0;h<A[1].length;h++){
                        paid_user_city.push(A[1][h]);
                    }

                }
            }
        });

    //  at initialization just show the states

    show_states();

    //  Add event listeners to events such as map resize, zoom_changed
    //  see google map api documentation for more details

    google.maps.event.addListener(map, 'resize',function(){

        map.setZoom( map.getZoom() - 1);
        map.setZoom( map.getZoom() + 1);
        map.setCenter(map.getCenter());

    });

    google.maps.event.addListener(map, 'zoom_changed', function() {
        var current_zoom=map.getZoom();
        if(init_zoom>=0&&init_zoom<=6)
        {
            if(current_zoom>=7&&current_zoom<11){
                //remove states overlay
                //add listeners
                $('sidebar').show();
                remove_states();
                toggle_city_marker('1');
                init_zoom=map.getZoom();
            }
            else
            {
                if(current_zoom>=11)
                {
                    remove_states();
                    show_regions();
                    
                }

            }
            init_zoom=map.getZoom();
        }
        else
        {
            //zoom was in state level
            if(init_zoom>6&&init_zoom<11)
            {
                if(current_zoom<=6)
                {
                    toggle_city_marker('0');
                    //remove listener for city
                    //show states
                    $('sidebar').hide();
                    show_states();
                    init_zoom=map.getZoom();
                }
                else
                {
                    if(current_zoom>=11)
                    {
                       // toggle_city_marker('0');
                       //remove listener for city
                       init_zoom=map.getZoom();

                       show_regions();
                    }   
                }
                init_zoom=map.getZoom();
            }
            //zoom was in city level
            else
            {
                if(current_zoom>6&&current_zoom<11)
                {
                    //clear regions overlay
                    //activate event listener for city
                    remove_regions();

                    $('sidebar').show();
                    $('regiontable').hide();

                    toggle_city_marker('1');
                    init_zoom=map.getZoom();
                }
                else
                {
                    if(current_zoom<7)
                    {
                        //clear regions overlay
                        //show states
                        remove_regions();
                        show_states();

                        $('sidebar').hide();

                        toggle_city_marker('0');
                        init_zoom=map.getZoom();
                        
                    }
                    else
                    {
                        show_regions();
                    }
                    
                }
                init_zoom=map.getZoom();
            }
        }

    });
 }

//  this function enables the user to show the street view of a hotel clicked

function showStreetView(loc)
{     
    if($('street_canvas').style.display=="none"){

        var options={scaleMode: {originalHeight: 800, originalWidth: 1500}}

        $('hide').show();

        //resize all elements in the page to make room for the streetview stuff

        new Effect.Scale($('map_canvas'), 75,options);
        new Effect.Appear($('street_canvas'));

        //adjust for the resizing of the map (when resizing map canvas, after initializtion, make sure to check if the map is loaded correctly =)

        $('street_canvas').setOpacity(1.0);
        google.maps.event.trigger(map, 'resize');
        map.setZoom( map.getZoom() );
        map.panBy(200, 80);

        if(region_overlay[0]!=null)
        {
            for(var i=0;i<region_overlay.length;i++)
            {
                region_overlay[i].setMap(map);
            }
        }
        var panoramaOptions = {
            position: loc,
            pov: {
                heading: 34,
                pitch: 10,
                zoom: 1
            }
        };

        panorama= new  google.maps.StreetViewPanorama(document.getElementById("street_canvas"), panoramaOptions);

    }
    else{
        panorama.setPosition(loc);
    }
}

//  hides the streetview from the page

function hideStreetView()
{
    $('hide').fade();
    $(street_canvas).fade();
    var options={
        scaleMode: {originalHeight: 800, originalWidth: 1500}
    }
    new Effect.Scale($(map_canvas), 100,options);
    
    google.maps.event.trigger(map, 'resize');
    map.setZoom( map.getZoom() );
    map.panBy(-200, -80);

    if(region_overlay[0]!=null)
    {
        for(var i=0;i<region_overlay.length;i++)
        {
            region_overlay[i].setMap(map);
        }
    }
}


//  this function is called depanding on the zoom level of the map instance, it calls the server side and retrives all region information

function show_regions()
{
    if(typeof(paid_user_city[0])!="undefined"&&($('regionlistdiv').visible()==false)){
        
        //effects
        new Effect.BlindUp('sidebar', {duration: 0.6});
        new Effect.BlindDown('regiontable', {duration: 0.6});
        //ajax call
        var req = new Ajax.Request('/hotels/get_regions', {
                method: 'post',
                onSuccess: function(transport) {
                    var result = transport.responseText;
                    var A = eval("("+result+")");
                    var states = A[0];
                    for(var ji=0;ji<states.length;ji++)
                    {
                        var polypath=[];
                        for(var t=0;t<states[ji].length;t++)
                        {
                           var point= new google.maps.LatLng(states[ji][t].lat,states[ji][t].lng);
                           polypath.push(point);
                        }
                        if(!region_overlay[states[ji][0].id])
                            MakeRegions(states[ji][0].id,states[ji][0].name,polypath,states[ji][0].clt,states[ji][0].clg);
                            region_tooltip[states[ji][0].id]=new CustomMarker(new google.maps.LatLng(states[ji][0].clt,states[ji][0].clg),states[ji][0].id , map,states[ji][0].name);
                    }
                }
            });

        //if user is authorized, enable the user to click the regions the user has paid for
        for(var i = 0 ;i <paid_user_city.length;i++)
           google.maps.event.trigger(marker[paid_user_city[i]], 'click');
    }
}

function isPointinPolygon(region,point)     //region is an polygon (google.polygon) and point is a position google.Latlng
{
    if(region.containsLatLng(point))
    {
        return true;
    }
    return false;
}

//  stores user preferences and adds functionality to region navigation table

function showRegionNav(x)   //takes in a | delimited 0 1 depending on the user preferance
{
    new Effect.BlindUp('sidebar', {duration: 0.6});
    new Effect.BlindUp('regiontable', {duration: 0.6});

 
    $('regionnavlist').childElements().each(function(e){e.show();e.removeClassName('regionselected');});
    map.panTo(region_center[x]);
    map.fitBounds(region_overlay[x].getBounds());
    $('list|'+x).addClassName('regionselected');

    for(var tempi=0;tempi<userPreference.length;tempi++)
    {
       var list_id="list|"+userPreference[tempi];
  
       $(list_id).hide();
    }

    new Effect.BlindDown('regionlistdiv', {duration: 0.6});
    new Effect.BlindDown('backbutton', {duration: 0.6});
}

//  removes the regions from the map

function remove_regions()
{

    for(var temp=0;temp<region_container.length;temp++)
        region_container[temp].setMap(null);

    new Effect.BlindUp('regionlistdiv', {duration: 0.6});
    new Effect.BlindUp('backbutton', {duration: 0.6});
    new Effect.BlindUp('regiontable', {duration: 0.6});
}

//  given the data retrieved from the server side for regions, this function makes region polygon for the google map, then adds event listeners for the overlays as well

function MakeRegions(id,name,patharray,x,y)
{
    //make regions for google maps
    region_center[id]= new google.maps.LatLng(parseFloat(x),parseFloat(y));
    region_overlay[id] = new google.maps.Polygon({
        paths: patharray,
        strokeColor: "#FF0000",
        strokeOpacity: 0.2,
        strokeWeight: 3,
        fillColor: "#FF0000",
        fillOpacity: 0.15
    });

    region_container.push(region_overlay[id]);
    region_overlay[id].setMap(map);

    //add event listeners to add interactive functionality to the region polygons on the map

    google.maps.event.addListener(region_overlay[id], 'mouseout',function(event)
    {
         this.setOptions({strokeOpacity:0.2, fillOpacity: 0.15});
         region_tooltip[id].hide();
    });

    google.maps.event.addListener(region_overlay[id], 'mouseover', function(event)
    {
        this.setOptions({strokeOpacity:0.6, fillOpacity: 0.35});
        region_tooltip[id].show();
    });
    
    google.maps.event.addListener(region_overlay[id], 'click', function(event)
    {
        map.panTo(region_center[id]);
        region_tooltip[id].hide();
        map.fitBounds(region_overlay[id].getBounds());
    });

    // add entry for the new region in the navigation table

    var column=document.createElement('tr');
    
    var sidebarEntry = createSidebarEntryForRegion(region_overlay[id], name, '1',id);
    column.appendChild(sidebarEntry);
    document.getElementById('regiontable').appendChild(column);
    add_li(name,id);

}

//goes back to previous navigation table from the region navigation

function back()
{
    new Effect.BlindUp('regionlistdiv', {duration: 0.6});
    new Effect.BlindUp('backbutton', {duration: 0.6});
    new Effect.BlindDown('regiontable', {duration: 0.6});
    
}

//  constructs html for every region entry and adds event listeners to add interactivity

function add_li(text,id) {

    //construct html for region entry

    var list = document.getElementById('regionnavlist');
    var li = document.createElement("li");
    li.setAttribute('id', 'list|'+id);
    li.innerHTML = text;
    li.style.cursor="pointer";
    li.setOpacity(0.5);

    //add event listeners

    li.onmouseover=function(){
        new Effect.Opacity(li, {from: 0.5, to: 1.0, duration: 0.3});
         google.maps.event.trigger(region_overlay[id], 'mouseover');

    }
    li.onmouseout=function(){
        new Effect.Opacity(li, {from: 1.0, to: 0.5, duration: 0.3});
                 google.maps.event.trigger(region_overlay[id], 'mouseout');
    }
    li.onclick=function(){
        $('regionnavlist').childElements().each(
            function(s){
                if(s.hasClassName('regionselected')){
                    s.removeClassName('regionselected');
                }
            }
        );
        
        li.setAttribute('class', 'regionselected');
        google.maps.event.trigger(region_overlay[id], 'click');

    }
    list.appendChild(li);
}


//  displays states on the map

function show_states()
{
    document.getElementById('sidebar').innerHTML="";

    // if not initialized, get info from server else use the information that is already loaded

    if(typeof(stateMarker[1])=="undefined"){
        statecount=0;
        //ajax call for states info from server side
        var req = new Ajax.Request('/hotels/get_states', {
                    method: 'post',
                    onSuccess: function(transport) {
                        var result = transport.responseText;
                        var A = eval("("+result+")");
                        var states = A[0];
                        for(var ji=0;ji<states.length;ji++)
                        {
                            Makestates(statecount,states[ji].name,states[ji].code,parseFloat(states[ji].lat),parseFloat(states[ji].lng));
                            statecount++;
                        }
                    }
         });
    }
    else
    {
        for(var stateI=0;stateI<stateMarker.length;stateI++)
        {
            stateMarker[stateI].setVisible(true);
        }
        for(var cityM=0;cityM<markers.length;cityM++)
        {
            markers[cityM].setMap(null);
            tooltips[cityM].onRemove();
        }
    }
}

//  removes states from the map

function remove_states()
{
    for(var stateI=0;stateI<stateMarker.length;stateI++)
        {
            stateMarker[stateI].setVisible(false);
        }

}

//  makes the state icons for the google maps provided the server side

function Makestates(id,name,code,lat,lng)
{
    var stateName=name+", "+code;
    var myLatlng = new google.maps.LatLng(lat,lng);

    stateMarker[id] = new google.maps.Marker({
            position: myLatlng,
            map: map,
            title: stateName,
            icon: stateIcon
    });
}

//  this function adds/removes city markers from the map
//  it uses the current user pan to determine what city markers should be requested to the server
//  it initially loads the city markers needed for the current user pane
//  then it adds an event listener to load relevant markers according to the users pane

function toggle_city_marker(set)
{
    if(set=='1')
    {
        ICurrent=map.getBounds();
        INE=ICurrent.getNorthEast();
        ISW=ICurrent.getSouthWest();
        IMaxLat=INE.lat();
        IMinLat=ISW.lat();
        IMinLng=ISW.lng();
        IMaxLng=INE.lng();
        user_viewed_bounds=map.getBounds();

        //  initial city marker info retrival ajax call

        var req = new Ajax.Request('/hotels/loadmarker', {
            method: 'post',
            parameters: {minlat: IMinLat,maxlat: IMaxLat, minlng: IMinLng, maxlng: IMaxLng},
            onSuccess: function(transport) {
                var result = transport.responseText;
                var A = eval("("+result+")");
                var hotelM = A[0];

                for(var ji=0;ji<hotelM.length;ji++)
                {
                    MakeMarkers(parseFloat(hotelM[ji].lat),parseFloat(hotelM[ji].lng),hotelM[ji].name,hotelM[ji].sum,hotelM[ji].id,hotelM[ji].paid_for);

                    var sidebarEntry = createSidebarEntry(marker[hotelM[ji].id], hotelM[ji].name,hotelM[ji].id ,hotelM[ji].sum);

                    document.getElementById('sidebar').appendChild(sidebarEntry);
                }

                Cbounds=new google.maps.LatLngBounds();
            }
        });

        //  add listeners to load markers when user paning bounds are changed

        ListenerCity=google.maps.event.addListener(map, 'bounds_changed', function() {
            var Current=map.getBounds();
            var NE=Current.getNorthEast();
            var SW=Current.getSouthWest();
            var MaxLat=NE.lat();
            var MinLat=SW.lat();
            var MinLng=SW.lng();
            var MaxLng=NE.lng();
            if(typeof(ICurrent)=="undefined"){}

            var threshold=parseFloat(50/((parseFloat(map.getZoom()))*(parseFloat(map.getZoom())) ));
            if((MaxLat>(IMaxLat + threshold))||(MinLat<(IMinLat - threshold))||(MaxLng>(IMaxLng + threshold))||(MinLng<(IMinLng - threshold)))
            {
                            
                if(!user_viewed_bounds.contains(NE)||!user_viewed_bounds.contains(SW)){
                            
                    document.getElementById('sidebar').innerHTML="";

                    req = new Ajax.Request('/hotels/loadmarker', {
                        method: 'post',
                        parameters: {minlat: MinLat,maxlat: MaxLat, minlng: MinLng, maxlng: MaxLng},

                        onSuccess: function(transport) {
                            var result = transport.responseText;
                            var A = eval("("+result+")");
                            var hotelM = A[0];
                            for(var ji=0;ji<hotelM.length;ji++)
                            {
                                if(!marker[hotelM[ji].id]){

                                    MakeMarkers(parseFloat(hotelM[ji].lat),parseFloat(hotelM[ji].lng),hotelM[ji].name,hotelM[ji].sum,hotelM[ji].id,hotelM[ji].paid_for);
                                }
                                
                                var sidebarEntry = createSidebarEntry(marker[hotelM[ji].id], hotelM[ji].name,hotelM[ji].id ,hotelM[ji].sum);
                                document.getElementById('sidebar').appendChild(sidebarEntry);

                            }

                            Cbounds=new google.maps.LatLngBounds();
                        }
                    });

                    user_viewed_bounds.union(Current);
                }

                ICurrent=map.getBounds();
                IMaxLat=MaxLat;
                IMinLat=MinLat;
                IMinLng=MinLng;
                IMaxLng=MaxLng;
            }
        });

    }
    else
    {
        google.maps.event.removeListener(ListenerCity);
        user_viewed_bounds=new google.maps.LatLngBounds();
    }

}

//  this function makes the city markers for google maps, provided the server side info

function MakeMarkers(x, y, name,sum,id, pf) {

    var myLatlng = new google.maps.LatLng(x,y);
    var imloc="";

    if(pf=='1')
        imLoc='http://chart.apis.google.com/chart?chst=d_map_pin_letter&chld=' + sum +'|2ad22a|ffffff';
    else
        imLoc='http://chart.apis.google.com/chart?chst=d_map_pin_letter&chld='+sum+'|FF0000|000000';

    var iconImage = new google.maps.MarkerImage( imLoc,
	                     new google.maps.Size(20, 34),
	                     new google.maps.Point(0, 0),
	                     new google.maps.Point(10, 34))

    
    marker[id] = new google.maps.Marker({
        position: myLatlng,
        map: map,  
        icon: iconImage,
        zIndex:3
    });

    tooltip[id]=new CustomMarker(myLatlng,id,map,name);

    markers.push(marker[id]);
    tooltips.push(tooltip[id]);
    Bounds.extend(marker[id].position);

    google.maps.event.addListener(marker[id], 'mouseover', function() {tooltip[id].show()});
    google.maps.event.addListener(marker[id], 'mouseout', function() {tooltip[id].hide()});

    if(logged_in=='1')
        addInfo(marker[id],infowindow[i],id);

    i++;
}

//  simple function to change map zoom level

function panToLevel(level)
{
    if(level=='3')
    {
        map.setZoom(3);
    }
    else
    {
        if(level=='2'){

            map.setZoom(5);
        }
        else
        {
            if(level=='1')
                map.setZoom(9);

        }

    }

}

//  this function creates html to represent city markers in the city navigation andd adds relevant listeners

function createSidebarEntry(marker, name, markerID, sum) {

      var div = document.createElement('div');
      var html = '<b>' + name + '</b> (' + sum + ')<br/>';   
      div.innerHTML = html;
      div.style.cursor = 'pointer';
      div.style.marginBottom = '5px';
      div.setAttribute('class', 'item');

      google.maps.event.addDomListener(div, 'click', function() {
        google.maps.event.trigger(marker, 'click');
        map.panTo(marker.getPosition());
        tooltip[markerID].hide();
      });

      google.maps.event.addDomListener(div, 'mouseover', function() {
        div.style.backgroundColor = '#eee';
        tooltip[markerID].show();
      });

      google.maps.event.addDomListener(div, 'mouseout', function() {
        div.style.backgroundColor = '#fff';
        tooltip[markerID].hide();
      });
      
      return div;
}

//  function adds html for regions in the region navigation, adds event listeners

function createSidebarEntryForRegion(region, name, sum,id) {

      var row = document.createElement("tr");
      var cellforDiv = document.createElement("td");
      var cellforZoom = document.createElement("td");
      var div = document.createElement('div');
      var html = '<b>' + name + '</b> (' + sum + ')<br/>';
      var span=document.createElement('span');

      span.innerHTML="<a href=\"javascript:showRegionNav("+id+");\"><i>zoom</i></a>";
      span.style.cursor="pointer";
      span.setAttribute('id', 'span|'+id);
      span.style.visibility = "visible";
      span.hide();

      div.style.marginBottom = '5px';
      div.innerHTML = html;
      div.style.cursor = 'pointer';
      div.style.marginBottom = '5px';

      var chkbox = document.createElement('input');

      chkbox.type='checkbox';
      chkbox.id = 'chk|' + id;
      chkbox.name = 'chk|' + id;
      chkbox.setAttribute('checked','true');
      
      chkbox.onchange=function()
      {
          var extract=new Array();
          extract=this.id.toString().split('|');
          var temp="";
          var tempup=new Array();

          if(this.getAttribute('checked')=="true"){
            temp=extract[1];
            $('span|'+extract[1]).fade();
            userPreference.push(temp);

            for(var i=0;i<Hmarker.length;i++)
            {
                if(region.containsLatLng(Hmarker[i].getPosition())){
                    Hmarker[i].setMap(null);
                }
            }
            region_tooltip[id].hide();

            chkbox.setAttribute('checked','false');
          }

          else{

              for(var j=0;j<Hmarker.length;j++)
              {
                if(region.containsLatLng(Hmarker[j].getPosition())){
                    Hmarker[j].setMap(map);
                }
              }
              chkbox.setAttribute('checked','true');
              $('span|'+extract[1]).appear();
              for(var tb=0;tb<userPreference.length;tb++){
                if(userPreference[tb]==extract[1])
                {
                    var cp=0;
                    for(var tempor=0;tempor<userPreference.length;tempor++)
                    {
                        if(userPreference[tempor]!=extract[1])
                        {
                            tempup[cp]=userPreference[tempor];
                            cp++;
                        }
                    }

                    userPreference=tempup;
                }
             }
          }

          if(this.getAttribute('checked')=="false")
            region_overlay[parseInt(extract[1])].setMap(null);
          else
              region_overlay[parseInt(extract[1])].setMap(map);
      }

      //add event listeners

      google.maps.event.addDomListener(div, 'mouseover', function() {
        div.style.backgroundColor = '#eee';
        google.maps.event.trigger(region, 'mouseover');
      });

      google.maps.event.addDomListener(div, 'mouseout', function() {
        div.style.backgroundColor = '#fff';
        google.maps.event.trigger(region, 'mouseout');
      });

      google.maps.event.addDomListener(row, 'mouseover', function() {
        row.style.backgroundColor = '#eee';

        if(chkbox.getAttribute('checked')=="true")
        span.show();
      
      });

      google.maps.event.addDomListener(row, 'mouseout', function() {
        row.style.backgroundColor = '#fff';
        span.hide();
      });

      div.appendChild(chkbox);
      cellforDiv.appendChild(div);
      cellforZoom.appendChild(span);
      row.appendChild(cellforDiv);
      row.appendChild(cellforZoom);
      
      return row;
}

//  this function requests server side for hotels in one city

function addInfo(tempmarker, info,id) {
    
    google.maps.event.addListener(tempmarker, 'click', function() {
        tooltip[id].hide();
        var req = new Ajax.Request('/hotels/get_hotels', {
            method: 'post',
            parameters: {cityid: id},
            onSuccess: function(transport) {

                var result = transport.responseText;

                if(result=="[[]]"){
                    return;
                }

                tempmarker.setVisible(false);
                    
                
                var A = eval("("+result+")");
                var hotelM = A[0];


                for(var ji=0;ji<hotelM.length;ji++)
                {
                    MakeHotels(parseFloat(hotelM[ji].lat),parseFloat(hotelM[ji].lng),id);
                }

                Cbounds=new google.maps.LatLngBounds();
            }
        });
    });
}

//this function makes hotel markers for the google maps from server side info
 
function MakeHotels(x_,y_,ids)
{
    var Latlng = new google.maps.LatLng(x_,y_);

    hotelMarkers[j] = new google.maps.Marker({
        position: Latlng,
        map: map,
        title: "hotel-"+ids,
        icon: image
    });

    Cbounds.extend(hotelMarkers[j].position);
    Hmarker.push(hotelMarkers[j]);

    google.maps.event.addListener(hotelMarkers[j], 'click', function() {showStreetView(Latlng)});

    j++;
}
function center()
{
    map.fitBounds(Bounds);
}