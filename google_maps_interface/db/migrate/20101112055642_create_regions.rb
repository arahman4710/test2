class CreateRegions < ActiveRecord::Migration
  def self.up
    create_table :regions do |t|
      t.string :name
      t.integer :city_id
      t.float :latitude
      t.float :longitude
      t.integer :active
    end
  end

  def self.down
    drop_table :regions
  end
end
