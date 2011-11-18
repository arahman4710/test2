class Removeregionpointstable < ActiveRecord::Migration
  def self.up
    drop_table "region"
    drop_table "point"
  end

  def self.down
  end
end
