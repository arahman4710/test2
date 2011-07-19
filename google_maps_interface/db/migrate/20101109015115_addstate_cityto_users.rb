class AddstateCitytoUsers < ActiveRecord::Migration
  def self.up
    add_column :users, :state_id, :integer
    add_column :users, :city_id, :integer

  end

  def self.down
    remove_column :users, :state_id
    remove_column :users, :city_id
  end
end
