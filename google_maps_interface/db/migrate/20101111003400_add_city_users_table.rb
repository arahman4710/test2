class AddCityUsersTable < ActiveRecord::Migration
  def self.up
      create_table :cities_users, :id => false do |t|
  t.column :city_id, :integer
  t.column :user_id, :integer
  end
  end

  def self.down
  end
end
