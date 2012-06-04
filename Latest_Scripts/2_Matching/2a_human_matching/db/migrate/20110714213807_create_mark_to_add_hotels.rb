class CreateMarkToAddHotels < ActiveRecord::Migration
  def self.up
    create_table :mark_to_add_hotels do |t|
      t.integer :forum_hotel_id
    end
  end

  def self.down
    drop_table :mark_to_add_hotels
  end
end
