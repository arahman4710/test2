class Addpointstable < ActiveRecord::Migration
  def self.up
    create_table :point do |t|
      t.integer :region_id
      t.integer :order_id
      t.float :latitude
      t.float :longitude
    end
  end

  def self.down
  end
end
