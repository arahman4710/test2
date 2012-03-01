require 'rubygems'
require 'watir'

browser = Watir::Browser.start("http://travela.priceline.com/hotels/?plf=pcln")
browser.div(:class, "bidNowBtn").links.first.click
browser.text_field(:id, "OFFER/HOTELS/SEARCH_CITY_OPQ").set "Miami, Florida"
browser.text_field(:id, "bid_htl_checkin_CTL").set((Time.now + 86400 * 3).strftime("%m/%d/%y"))
browser.text_field(:id, "bid_htl_checkout_CTL").set((Time.now + 86400 * 4).strftime("%m/%d/%y"))
browser.form(:name, "bid_htl").submit()
browser.goto("http://www.priceline.com/hotels/Lang/en-us/city_list.asp?r=US")
browser.link(:text, "V-Z").click
File.open('test_html.txt', "w") { |f| f.write(browser.html) }
counter = 1
file = File.new("test_html.txt", "r")
city_list = []
while (line = file.gets)
  if line =~ /itinerary\.asp/
    if line =~ /(>)([a-zA-Z\s]+)(<)/ then city = $2 end
    if line =~ /(href=")(.+)(")/ then link = $2 end
    if city and link
      find_state = true
    end
    
  elsif find_state
    if line =~ /(>)([a-zA-Z\s]+)(<)/ then state = $2 end
    if state
      city_list << "#{city}, #{state}"
    end
  end
end

file.close
city_list = city_list.uniq
File.open('city_list.txt', "w") { |f| f.write(city_list) }

#File.open('test_html.txt', "w") { |f| f.write(browser.html) }
#html = browser.html
#html.each_with_index do |place, index|
#  p place

#end



#browser.link(:text, 'Alabaster').click
#browser.text_field(:id, "Temp/Hotels/@DHTML_CheckInDate").set((Time.now + 86400 * 3).strftime("%m/%d/%y"))
#browser.text_field(:id, "Temp/Hotels/@DHTML_CheckOutDate").set((Time.now + 86400 * 4).strftime("%m/%d/%y"))
#browser.button(:name, "NextCtl").click()
#browser.div(:id, "nyop-box").links.first.click
#browser.back
#browser.back
#browser.back