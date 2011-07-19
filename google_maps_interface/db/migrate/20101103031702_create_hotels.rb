class CreateHotels < ActiveRecord::Migration
  def self.up
    create_table :hotels do |t|
      t.string :name
      t.float :rating
      t.integer :city_id
      t.string :state
      t.string :country
      t.string :address
      t.float :minimumrate
      t.string :currency
      t.float :latitude
      t.float :longitude
      t.integer :ratingcount
      t.float :userrating
      t.integer :property
      t.timestamps
    end
  end

  def self.down
    drop_table :hotels
  end
end
