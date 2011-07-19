class DropTables < ActiveRecord::Migration
  def self.up
    drop_table "cities_users"
    drop_table "users_cities"
  end

  def self.down
  end
end
