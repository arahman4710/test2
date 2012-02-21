class Hotel < ActiveRecord::Base
  
  set_primary_key :hotel_id

  def get_city_info

    return City.find_by_uid(self.city_id)

  end

end
