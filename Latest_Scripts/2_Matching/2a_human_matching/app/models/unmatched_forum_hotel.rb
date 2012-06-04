class UnmatchedForumHotel < ActiveRecord::Base

  set_table_name :unmatched_forum_hotel_table
  set_primary_key :uid

  #has_many :PossibleForumHotelMatches, :through => :forum_hotel_id

  belongs_to :ProcessedRawForumData#, :through => :forum_hotel_id

  def update_match(match)

    self.update_attribute(matched, match)

  end


  def get_forum_hotel_info

    return ProcessedRawForumData.find_by_uid(self.forum_hotel_id)

  end

  def get_matched_hotel_info

    return Hotel.find_by_hotel_id(self.matched)

  end

  def is_in_city

    if self.city_id.integer?

      return true

    end

    return false

  end

  def get_possible_hotel_matches

    return PossibleForumHotelMatch.find_all_by_unmatched_entry_id(self.uid)

  end

  def get_city_info

    return City.find_by_uid(self.city_id)

  end

  def get_area_info

      return PricelineArea.find_by_uid(self.area_id)

  end

  def get_region_info

    if self.region_id.integer?

      return PricelineRegion.find_by_uid(self.region_id)

    end

    return false

  end

end
