class CreatePoints < ActiveRecord::Migration
  def self.up
    create_table :points do |t|
      t.integer :region_id
      t.integer :order_id
      t.float :latitude
      t.float :longitude
    end
  end

  def self.down
    drop_table :points
  end
end
