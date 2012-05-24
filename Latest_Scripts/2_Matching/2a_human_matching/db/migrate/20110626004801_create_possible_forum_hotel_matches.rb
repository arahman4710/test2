class CreatePossibleForumHotelMatches < ActiveRecord::Migration
  '''
  def self.up
    create_table :possible_forum_hotel_matches do |t|

      t.timestamps
    end
  end

  def self.down
    drop_table :possible_forum_hotel_matches
  end
  '''
end
