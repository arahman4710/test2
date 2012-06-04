class PossibleForumHotelMatch < ActiveRecord::Base

  set_table_name :possible_forum_hotel_match_table
  set_primary_key :uid

 # belongs_to :UnmatchedForumHotel, :through => :unmatched_entry_id

  def get_hotel_info

    return Hotel.find_by_hotel_id(self.hotel_id)

  end
end
