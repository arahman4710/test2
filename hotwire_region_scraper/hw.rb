require 'rubygems'
require 'watir'
require 'win32ole'
require 'fileutils'
require 'timeout'

class LoadingError < Exception
end
class ProcessingError < Exception
end
class ParsingError < Exception
end

def exists(browser)

	# Checks if the map image exists (results have finished updating)
	#
	browser.images.each do |img|
		if img.alt == "Explore our interactive map" then
			return true
		end
	end
	
	return false
end

def main

	# 1  Update the city list using python (faster than using Watir in Ruby)
	#    Start wireshark also
	#
	filename = "output/hwcities.txt"
	#`python findhwcities.py #{filename}`
	citylist = IO.readlines(filename, "").to_s
	cities = citylist.split(/;/)

	# 2  Search through all of the cities using Watir, output the results using wireshark
	#
	browser = Watir::IE.start "http://www.hotwire.com/hotel/index.jsp"
	wmi = WIN32OLE.connect("winmgmts://")
	count = 0
	
	# 2z Load the last city
	#
	begin
		starter = File.open("last_city.txt", "r") { |f| f.read }
	rescue
		starter = ""
	end
	
	if starter =~ /.+/ then
		until cities.first == starter
			cities.shift
		end
		cities.shift
	end
	
	dead_flag = nil
	
	cities.each_with_index do |city, index|

		count += 1
		
		if count == 20 or dead_flag then
			`taskkill /im iexplore.exe /f`
			browser = Watir::IE.start "http://www.hotwire.com/hotel/index.jsp"
			count = 0
		end
		
		begin

			# 2a  Set the search parameters
			#
			browser.text_field(:name, "destCity").set city
			browser.text_field(:name, "startDate").set((Time.now + 2*60*60*24).strftime("%m/%d/%y"))
			browser.text_field(:name, "endDate").set((Time.now + 3*60*60*24).strftime("%m/%d/%y"))
			
			Timeout::timeout(30) do
				browser.form(:name, "hotelIndexForm").submit
			end
			
			# 2b  Find the city id in the database
			#
			area = city.split(/,/)
			city_name = area[0]
			state = area[1]
			`python find_city.py "#{city_name}" "#{state}"`
			unless $?.success? then raise end
			
			# 2b  Wait for the map, reset wireshark and then open the map
			#
			a = 0
			until exists(browser)
				if a < 20 then
					sleep 1
					a += 1
				else
					raise LoadingError
				end
			end
			
			# 2c  Wait 5 seconds for Wireshark to reset then open the map
			#
			IO.popen("C:\\programs\\Wireshark\\tshark -a duration:7 -x > C:\\programs\\hotwire\\output\\parse.txt")
			#`C:\\programs\\Wireshark\\tshark -a duration:7 -x > C:\\programs\\hotwire\\output\\parse.txt`
			sleep 2
			browser.image(:class, "areaMapLink").click
			
				
			# 2d  Sleep 5 seconds after results have loaded then parse them
			#
			sleep 8
			`python hwparse.py #{city}`
			unless $?.success? then raise ParsingError end
			
			`python process.py`
			unless $?.success? then raise ProcessingError end
			
		rescue LoadingError
			File.open("hw.log", "a") { |f| f.write("SEARCH ERROR: #{city}\n") }
			popen("autoit/delete.exe")
			sleep 5
			dead_flag = 1
		rescue ParsingError
			File.open("hw.log", "a") { |f| f.write("PARSING ERROR: #{city}\n") }
		rescue ProcessingError
			File.open("hw.log", "a") { |f| f.write("PROCESSING ERROR: #{city}\n") }
		else
			File.open("hw.log", "a") { |f| f.write("ERROR: #{city}\n") }
		ensure
			browser.back
			File.open("last_city.txt", "w") { |f| f.write(city) }
			`del "output\\parse.txt"`
			`del "output\\process.txt"`
		end
		
	end
end


begin
	main
rescue
	raise
ensure
	# Clean up temp files
	#
	#`del output/hwcities.txt`
	`taskkill /im iexplore.exe /f`
	#`taskkill /im wireshark.exe /f`
end