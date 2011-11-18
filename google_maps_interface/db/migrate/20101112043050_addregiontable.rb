class Addregiontable < ActiveRecord::Migration
  def self.up
    create_table :region do |t|
      t.string :name
      t.integer :city_id
      t.float :latitude
      t.float :longitude
      t.integer :active
    end
  end

  def self.down
  end
end
