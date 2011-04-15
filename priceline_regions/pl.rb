require 'rubygems'
require 'watir'
require 'win32ole'

class NoResults < Exception
end
class ProcessingFailure < Exception
end

def findCities(browser)
	
	# 3  Start a session and go to the cities list
	#
	browser.text_field(:id, "OFFER/HOTELS/SEARCH_CITY_OPQ").set "Miami, Florida"
	browser.text_field(:id, "bid_htl_checkin_CTL").set((Time.now + 86400 * 3).strftime("%d/%m/%y"))
	browser.text_field(:id, "bid_htl_checkout_CTL").set((Time.now + 86400 * 4).strftime("%d/%m/%y"))
	browser.form(:name, "bid_htl").submit()
	browser.goto("http://www.priceline.com/hotels/Lang/en-us/city_list.asp?r=US")
	html = browser.html
	
	# 4  Finds a list of the cities, links, and states
	#    And goes through all of the sections
	#
	city = link = state = find_state = false
	sections = ["A-B", "C", "D-H", "I-L", "M", "N", "O-R", "S-U", "V-Z"]
	exec = Watir::IE.start("http://www.writecodeonline.com/javascript/")
	
	# Find the last city crawled
	#
	begin
		starter = File.open("output/last_city.txt", "r") { |f| f.read }
	rescue
		starter = ""
	end
	
	# Find cities to redo
	#
	begin
		missing = File.open("redo.txt", "r") { |f| f.read }
		missing = missing.split("\n")
	rescue
		missing = []
	end
	
	go = 1 unless starter =~ /.+/
	
	sections.each do |name|
		browser.link(:text, name).click
		
		# 4a  Iterate through the html
		#
		html = browser.html
		html.each_with_index do |place, index|
		
			# 4b  If we find a link with itinerary.asp in it we know it's probably a city link
			#     Save the text of the link and where it points to, and set a flag to find the state name
			#
			if place =~ /itinerary\.asp/
				if place =~ /(>)([a-zA-Z\s]+)(<)/ then city = $2 end
				if place =~ /(href=")(.+)(")/ then link = $2 end
				if city and link
					find_state = true
				end
				
			# 4c  If the flag is set to find a state, try and find one
			#     If found, go to the page of the last link and save its regions
			#
			elsif find_state
				if place =~ /(>)([a-zA-Z\s]+)(<)/ then state = $2 end
				if state
					link.gsub!("amp;", "")
					link.gsub!("undefined", "US")
					
					
					if not go then
						if "#{city},#{state}" == starter then
							go = true
						end
					elsif true then #missing.include?("#{city}, #{state}") then
						begin
							city_id = find_city(city, state)
							browser.link(:href, "http://www.priceline.com#{link}").click
							process_page(browser, exec, city_id, "#{city}, #{state}")
						rescue ProcessingFailure
							File.open("pl.log", "a") { |f| f.write("ERROR PROCESSING: #{city}, #{state}\n") }
						rescue NoResults
							File.open("pl.log", "a") { |f| f.write("NO RESULTS: #{city}, #{state}\n") }
							#IO.popen("delete.exe") # Delete cookies
						else
							File.open("pl.log", "a") { |f| f.write("ERROR: #{city}, #{state}\n") } 
						ensure
							browser.back
							File.open("output/last_city.txt", "w") { |f| f.write("#{city},#{state}") }
							city = link = state = find_state = false
						end
					end
				end
			end
		end
	end

end

def find_city(city, state)
	`python find_city.py "#{city}" "#{state}"`
	unless $?.success?
		raise "Failed to find city #{city}, #{state}"
	end
	File.open("output/city_id.txt") { |f| return f.read}
end

def process_page(browser, exec, city_id, cur_city)

	
	# 6  Finds all of the "zD.areas" variables in the html
	#
	matches = browser.html.scan(/zD.areas\[[0-9]+\].*?\};/m)
	region = nil
	regionid = nil
	lat = nil
	lng = nil
	points = nil
	
	# 7  Process each variable and output its value
	#
	output = ""
	
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
				exec.text_field(:id, "textarea-for-code").value = "function veDecodeLine(a,c,d){var e=a.replace(/0/g,\"\\\\\");var f=e.length;var g=0;var h=[];var i=0;var j=0;var k;try{while(g<f){var b;var l=0;var m=0;do{b=e.charCodeAt(g++)-63;m|=(b&0x1f)<<l;l+=5}while(b>=0x20);var n=((m&1)?~(m>>1):(m>>1));i+=n;l=0;m=0;do{b=e.charCodeAt(g++)-63;m|=(b&0x1f)<<l;l+=5}while(b>=0x20);var o=((m&1)?~(m>>1):(m>>1));j+=o;document.write(c+\";\"+d+\";\"+parseFloat(i*1e-5,10)+\";\"+parseFloat(j*1e-5,10)+\"$\")}}catch(ex){}}veDecodeLine(\"#{points}\", \"#{region}\", \"#{city_id}\");"
				exec.link(:class, "button-run").click
				points = exec.div(:id, "code-output").text
				File.open("pl.citytoregion", "a") { |f| f.write("#{cur_city} HAS #{region}\n") }
				
				# 7d  Output the centre point, then a list of its boundaries
				#
				output += "##{region};#{regionid};#{city_id};#{lat};#{lng}$"
				output += points
				
				sleep 0.5
			end
			
			# 7e  Reset variables for next loop
			#
			region = nil
			lat = nil
			lng = nil
			points = nil
		end
		
		
	end
	
	if output == "" then
		raise NoResults
	end
	
	File.open("output/process.txt", "w") { |file| file.write(output) }
	`python process.py`
	unless $?.success?
		raise ProcessingFailure
	end

end

# 1  Start the browser
#
begin
	browser = Watir::IE.start("http://travela.priceline.com/hotels/?plf=pcln")
	sleep 1 until browser.form(:id, "htl_home").exists?
	
	browser.div(:class, "bidNowBtn").links.first.click
	
	findCities(browser)
rescue
	raise
ensure
	`taskkill /im iexplore.exe /f`
end