class MarkToAddHotels < ActiveRecord::Base

  def get_forum_hotel_info

    return ProcessedRawForumData.find_by_uid(self.forum_hotel_id)

  end

  def get_unmatched_hotel_info

    return UnmatchedForumHotel.find_by_forum_hotel_id(self.forum_hotel_id)

  end
  
end
