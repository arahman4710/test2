class Addremovetable2 < ActiveRecord::Migration
  def self.up
    drop_table "cities_users"
    create_table :cityuser do |t|
      t.integer :city_id
      t.integer :user_id
    end
  end
  def self.down
  end
end
