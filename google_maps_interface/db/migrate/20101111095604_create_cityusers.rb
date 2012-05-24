class CreateCityusers < ActiveRecord::Migration
  def self.up
    create_table :cityusers do |t|
      t.integer :city_id
      t.integer :user_id

      t.timestamps
    end
  end

  def self.down
    drop_table :cityusers
  end
end
