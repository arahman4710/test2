require 'rubygems'
require 'watir'

#######################
### This script uses watir to navigate priceline.com and get region info
### get the city_list for different states using get_city_list
### Change line 135 for when scraping new section (A-B, C, D-F...etc)

city_list = ["Barre, Vermont", "Bennington, Vermont", "Brattleboro, Vermont", "Burlington, Vermont", "Colchester, Vermont", "Essex Junction, Vermont", "Killington, Vermont", "Ludlow, Vermont", "Middlebury, Vermont", "Rutland, Vermont", "Saint Albans, Vermont", "Saint Johnsbury, Vermont", "South Burlington, Vermont", "Springfield, Vermont", "Stowe, Vermont", "White River Junction, Vermont", "Williston, Vermont", "Abingdon, Virginia", "Alexandria, Virginia", "Altavista, Virginia", "Appomattox, Virginia", "Arlington, Virginia", "Ashburn, Virginia", "Ashland, Virginia", "Bedford, Virginia", "Blacksburg, Virginia", "Bristol, Virginia", "Cape Charles, Virginia", "Centreville, Virginia", "Chantilly, Virginia", "Charlottesville, Virginia", "Chesapeake, Virginia", "Chester, Virginia", "Chincoteague Island, Virginia", "Christiansburg, Virginia", "Collinsville, Virginia", "Colonial Heights, Virginia", "Covington, Virginia", "Culpeper, Virginia", "Daleville, Virginia", "Danville, Virginia", "Doswell, Virginia", "Dublin, Virginia", "Dumfries, Virginia", "Emporia, Virginia", "Exmore, Virginia", "Fairfax, Virginia", "Falls Church, Virginia", "Farmville, Virginia", "Franklin, Virginia", "Fredericksburg, Virginia", "Front Royal, Virginia", "Galax, Virginia", "Glen Allen, Virginia", "Gloucester, Virginia", "Gordonsville, Virginia", "Hampton, Virginia", "Harrisonburg, Virginia", "Herndon, Virginia", "Hillsville, Virginia", "Hopewell, Virginia", "Kilmarnock, Virginia", "King George, Virginia", "La Crosse, Virginia", "Lebanon, Virginia", "Leesburg, Virginia", "Lexington, Virginia", "Lorton, Virginia", "Luray, Virginia", "Lynchburg, Virginia", "Manassas, Virginia", "Marion, Virginia", "Martinsville, Virginia", "Max Meadows, Virginia", "Mc Lean, Virginia", "Mechanicsville, Virginia", "Midlothian, Virginia", "Mount Crawford, Virginia", "Mount Jackson, Virginia", "New Market, Virginia", "Newport News, Virginia", "Norfolk, Virginia", "Norton, Virginia", "Onancock, Virginia", "Orange, Virginia", "Petersburg, Virginia", "Portsmouth, Virginia", "Pounding Mill, Virginia", "Prince George, Virginia", "Radford, Virginia", "Raphine, Virginia", "Reston, Virginia", "Richmond, Virginia", "Roanoke, Virginia", "Rocky Mount, Virginia", "Ruckersville, Virginia", "Ruther Glen, Virginia", "Salem, Virginia", "Sandston, Virginia", "Smithfield, Virginia", "South Boston, Virginia", "South Hill, Virginia", "Spotsylvania, Virginia", "Springfield, Virginia", "Stafford, Virginia", "Staunton, Virginia", "Sterling, Virginia", "Stony Creek, Virginia", "Strasburg, Virginia", "Suffolk, Virginia", "Tappahannock, Virginia", "Triangle, Virginia", "Troutville, Virginia", "Vienna, Virginia", "Virginia Beach, Virginia", "Warrenton, Virginia", "Warsaw, Virginia", "Waynesboro, Virginia", "White Stone, Virginia", "Williamsburg, Virginia", "Winchester, Virginia", "Woodbridge, Virginia", "Woodstock, Virginia", "Wytheville, Virginia", "Yorktown, Virginia", "Airway Heights, Washington", "Auburn, Washington", "Bainbridge Island, Washington", "Battle Ground, Washington", "Bellevue, Washington", "Bellingham, Washington", "Bothell, Washington", "Bremerton, Washington", "Burlington, Washington", "Chehalis, Washington", "Chelan, Washington", "Cheney, Washington", "Cle Elum, Washington", "Colfax, Washington", "Edmonds, Washington", "Ellensburg, Washington", "Elma, Washington", "Everett, Washington", "Federal Way, Washington", "Ferndale, Washington", "Friday Harbor, Washington", "Gig Harbor, Washington", "Greenacres, Washington", "Hoquiam, Washington", "Issaquah, Washington", "Kelso, Washington", "Kennewick, Washington", "Kent, Washington", "Kirkland, Washington", "Lacey, Washington", "Lakewood, Washington", "Leavenworth, Washington", "Liberty Lake, Washington", "Long Beach, Washington", "Lynnwood, Washington", "Marysville, Washington", "Monroe, Washington", "Moses Lake, Washington", "Mount Vernon, Washington", "Mukilteo, Washington", "Oak Harbor, Washington", "Ocean Shores, Washington", "Olympia, Washington", "Omak, Washington", "Othello, Washington", "Pasco, Washington", "Port Angeles, Washington", "Port Townsend, Washington", "Prosser, Washington", "Pullman, Washington", "Puyallup, Washington", "Redmond, Washington", "Renton, Washington", "Richland, Washington", "Ritzville, Washington", "Seattle, Washington", "Sequim, Washington", "Shelton, Washington", "Silverdale, Washington", "Spokane, Washington", "Sumner, Washington", "Sunnyside, Washington", "Tacoma, Washington", "Toppenish, Washington", "Vancouver, Washington", "Veradale, Washington", "Walla Walla, Washington", "Washougal, Washington", "Wenatchee, Washington", "Winthrop, Washington", "Yakima, Washington", "Barboursville, West Virginia", "Beckley, West Virginia", "Belington, West Virginia", "Bluefield, West Virginia", "Bridgeport, West Virginia", "Bruceton Mills, West Virginia", "Buckhannon, West Virginia", "Charleston, West Virginia", "Dunbar, West Virginia", "Elkins, West Virginia", "Elkview, West Virginia", "Fairmont, West Virginia", "Fayetteville, West Virginia", "Gassaway, West Virginia", "Huntington, West Virginia", "Keyser, West Virginia", "Kingwood, West Virginia", "Lewisburg, West Virginia", "Martinsburg, West Virginia", "Mineral Wells, West Virginia", "Morgantown, West Virginia", "Newell, West Virginia", "Nitro, West Virginia", "Oak Hill, West Virginia", "Parkersburg, West Virginia", "Princeton, West Virginia", "Ranson, West Virginia", "Ripley, West Virginia", "Shepherdstown, West Virginia", "Summersville, West Virginia", "Sutton, West Virginia", "Vienna, West Virginia", "Weirton, West Virginia", "Weston, West Virginia", "Wheeling, West Virginia", "Algoma, Wisconsin", "Antigo, Wisconsin", "Appleton, Wisconsin", "Ashland, Wisconsin", "Baraboo, Wisconsin", "Beaver Dam, Wisconsin", "Beloit, Wisconsin", "Berlin, Wisconsin", "Black River Falls, Wisconsin", "Brookfield, Wisconsin", "Chippewa Falls, Wisconsin", "Columbus, Wisconsin", "De Forest, Wisconsin", "De Pere, Wisconsin", "Delafield, Wisconsin", "Delavan, Wisconsin", "Dodgeville, Wisconsin", "Eagle River, Wisconsin", "East Troy, Wisconsin", "Eau Claire, Wisconsin", "Fond Du Lac, Wisconsin", "Fort Atkinson, Wisconsin", "Franklin, Wisconsin", "Germantown, Wisconsin", "Grafton, Wisconsin", "Green Bay, Wisconsin", "Hayward, Wisconsin", "Hudson, Wisconsin", "Hurley, Wisconsin", "Janesville, Wisconsin", "Kaukauna, Wisconsin", "Kenosha, Wisconsin", "Kewaunee, Wisconsin", "Kimberly, Wisconsin", "La Crosse, Wisconsin", "Ladysmith, Wisconsin", "Lake Geneva, Wisconsin", "Little Chute, Wisconsin", "Madison, Wisconsin", "Manitowoc, Wisconsin", "Marshfield, Wisconsin", "Mauston, Wisconsin", "Menomonie, Wisconsin", "Middleton, Wisconsin", "Milwaukee, Wisconsin", "Mineral Point, Wisconsin", "Minocqua, Wisconsin", "Mosinee, Wisconsin", "Neenah, Wisconsin", "New Berlin, Wisconsin", "New London, Wisconsin", "Oak Creek, Wisconsin", "Oconomowoc, Wisconsin", "Onalaska, Wisconsin", "Oshkosh, Wisconsin", "Pewaukee, Wisconsin", "Phillips, Wisconsin", "Pleasant Prairie, Wisconsin", "Plover, Wisconsin", "Plymouth, Wisconsin", "Port Washington, Wisconsin", "Portage, Wisconsin", "Prairie Du Chien, Wisconsin", "Racine, Wisconsin", "Redgranite, Wisconsin", "Reedsburg, Wisconsin", "Rhinelander, Wisconsin", "Rice Lake, Wisconsin", "River Falls, Wisconsin", "Rothschild, Wisconsin", "Saint Croix Falls, Wisconsin", "Saukville, Wisconsin", "Schofield, Wisconsin", "Shawano, Wisconsin", "Sheboygan, Wisconsin", "Solon Springs, Wisconsin", "Sparta, Wisconsin", "Stevens Point, Wisconsin", "Sturgeon Bay, Wisconsin", "Sturtevant, Wisconsin", "Sun Prairie, Wisconsin", "Superior, Wisconsin", "Thiensville, Wisconsin", "Tomah, Wisconsin", "Verona, Wisconsin", "Waterford, Wisconsin", "Watertown, Wisconsin", "Waukesha, Wisconsin", "Waunakee, Wisconsin", "Waupaca, Wisconsin", "Waupun, Wisconsin", "Wausau, Wisconsin", "Wautoma, Wisconsin", "West Bend, Wisconsin", "West Salem, Wisconsin", "Whitewater, Wisconsin", "Windsor, Wisconsin", "Wisconsin Dells, Wisconsin", "Wisconsin Rapids, Wisconsin", "Wittenberg, Wisconsin", "Buffalo, Wyoming", "Casper, Wyoming", "Cheyenne, Wyoming", "Cody, Wyoming", "Douglas, Wyoming", "Evanston, Wyoming", "Evansville, Wyoming", "Gillette, Wyoming", "Green River, Wyoming", "Jackson, Wyoming", "Lander, Wyoming", "Laramie, Wyoming", "Lusk, Wyoming", "Pinedale, Wyoming", "Rawlins, Wyoming", "Riverton, Wyoming", "Rock Springs, Wyoming", "Sheridan, Wyoming", "Thermopolis, Wyoming", "Wilson, Wyoming", "Worland, Wyoming"]
f = File.open("output/last_city.txt", "r")
last_city = f.gets
p last_city
index = city_list.index(last_city)
total_length = city_list.count
starting_pos = total_length - index
city_list = city_list.last(starting_pos - 1)
p city_list[0]


def process_page(browser, exec, cur_city)
	
	
		
	# 6  Finds all of the "zD.areas" variables in the html
	#
	matches = browser.html.scan(/zD.areas\[[0-9]+\].*?\};/m)
	area = nil
	region = nil
	regionid = nil
	lat = nil
	lng = nil
	points = nil
	
	# 7  Process each variable and output its value
	#
	output = ""
	potential_area = browser.table(:id, 'map_tbl').text
	p5 = /Choose more than one area in .* to improve your chances/
	area_match = p5.match potential_area
	
	if area_match then
		new1 = area_match.to_s.gsub(/Choose more than one area in /, '')
		new2 = new1.gsub(/ to improve your chances/, '')
		area = new2
	end

	
	matches.each_with_index do |match, index|
		
		# 7a  On even indices set region names and region id's
		#
		if index % 2 == 0 then
			if match =~ /(name:")(.*?)(")/ then
				region = $2
			end
			if match =~ /(id:")(.*?)(")/ then
				regionid = $2
			end
			
		# 7b  On odd indices decode the co-ordinates
		#
		else
			if match =~ /(lat:")([0-9.]*?)(")/ then
				lat = $2
			end
			if match =~ /(lng:")([-0-9.]*?)(")/ then
				lng = $2
			end
			if match =~ /(points:")(.*?)(")/ then
				points = $2
			end
			
			if (region and regionid and lat and lng and points) then
				
				# 7c  Execute the javascript online
				#
				exec.text_field(:id, "textarea-for-code").value = "function veDecodeLine(a,c,d){var e=a.replace(/0/g,\"\\\\\");var f=e.length;var g=0;var h=[];var i=0;var j=0;var k;try{while(g<f){var b;var l=0;var m=0;do{b=e.charCodeAt(g++)-63;m|=(b&0x1f)<<l;l+=5}while(b>=0x20);var n=((m&1)?~(m>>1):(m>>1));i+=n;l=0;m=0;do{b=e.charCodeAt(g++)-63;m|=(b&0x1f)<<l;l+=5}while(b>=0x20);var o=((m&1)?~(m>>1):(m>>1));j+=o;document.write(c+\";\"+d+\";\"+parseFloat(i*1e-5,10)+\";\"+parseFloat(j*1e-5,10)+\"$\")}}catch(ex){}}veDecodeLine(\"#{points}\", \"#{region}\");"
				exec.link(:class, "button-run").click
				points = exec.div(:id, "code-output").text
				File.open("output/citytoregion.txt", "a") { |f| f.write("#{cur_city} HAS #{region}\n") }
				
				# 7d  Output the centre point, then a list of its boundaries
				#
				if area then
					output += "##{area};"
				else
					output += "#"
				end				
				output += "#{region};#{cur_city};#{lat};#{lng}$"
				output += points
				
				sleep 0.5
			end
			
			# 7e  Reset variables for next loop
			#
			area = nil
			region = nil
			lat = nil
			lng = nil
			points = nil
		end
		
		
	end
	
		
	File.open("output/process_US_priceline_v2.txt", "a") { |file| file.write("#{output}\n") }


end


puts city_list.count
puts "\n"
browser = Watir::Browser.start("http://travela.priceline.com/hotels/?plf=pcln")
exec = Watir::Browser.start("http://www.writecodeonline.com/javascript/")
browser.div(:class, "bidNowBtn").links.first.click
browser.text_field(:id, "OFFER/HOTELS/SEARCH_CITY_OPQ").set "Miami, Florida"
browser.text_field(:id, "bid_htl_checkin_CTL").set((Time.now + 86400 * 3).strftime("%m/%d/%y"))
browser.text_field(:id, "bid_htl_checkout_CTL").set((Time.now + 86400 * 4).strftime("%m/%d/%y"))
browser.form(:name, "bid_htl").submit()
p1 = /.*,/
p2 = /.*\w/
p3 = /,\s.*/
p4 = /\w.+/
$k = 0

while $k < city_list.count do
  begin
    city = p1.match city_list[$k]
    city = p2.match city[0]
    state = p3.match city_list[$k]
    state = p4.match state[0]
    browser.goto("http://www.priceline.com/hotels/Lang/en-us/city_list.asp?&plf=pcln&c=US&l=9&r=US")
    browser.link(:text, city[0]).click
	
	if $k < 1 then
		browser.text_field(:id, "Temp/Hotels/@DHTML_CheckInDate").set((Time.now + 86400 * 3).strftime("%m/%d/%y"))
		browser.text_field(:id, "Temp/Hotels/@DHTML_CheckOutDate").set((Time.now + 86400 * 4).strftime("%m/%d/%y"))
		browser.button(:name, "NextCtl").click()
		browser.div(:id, "nyop-box").links.first.click
	end
	
    if browser.text.include? "Please Confirm Your Destination"
      browser.link(:text, "#{city[0]}, #{state[0]}, United States").click
    end
	
    process_page(browser, exec, "#{city[0]},#{state[0]}")
    File.open("output/last_city.txt", "w") { |f| f.write("#{city}, #{state}") }

    $k += 1
  end
  
 
end

