class CreateCitiesUsers < ActiveRecord::Migration
  def self.up
    create_table :cities_users do |t|
      t.integer :city_id
      t.integer :user_id

      t.timestamps
    end
  end

  def self.down
    drop_table :cities_users
  end
end
