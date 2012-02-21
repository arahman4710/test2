class ProcessedRawForumData < ActiveRecord::Base

  set_table_name :processed_raw_forum_data
  set_primary_key :uid

  has_one :UnmatchedForumHotel

end
