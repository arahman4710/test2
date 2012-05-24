# This file is auto-generated from the current state of the database. Instead of editing this file, 
# please use the migrations feature of Active Record to incrementally modify your database, and
# then regenerate this schema definition.
#
# Note that this schema.rb definition is the authoritative source for your database schema. If you need
# to create the application database on another system, you should be using db:schema:load, not running
# all the migrations from scratch. The latter is a flawed and unsustainable approach (the more migrations
# you'll amass, the slower it'll run and the greater likelihood for issues).
#
# It's strongly recommended to check this file into your version control system.

ActiveRecord::Schema.define(:version => 20110714213807) do

  create_table "city", :id => false, :force => true do |t|
    t.integer "uid",                    :null => false
    t.string  "name",    :limit => 500
    t.string  "state",   :limit => 500
    t.string  "country", :limit => 500
  end

  create_table "hotels", :id => false, :force => true do |t|
    t.integer "hotel_id",           :null => false
    t.string  "name"
    t.string  "address"
    t.integer "city_id"
    t.float   "latitude"
    t.float   "longitude"
    t.string  "rating"
    t.string  "hotels_combined_id"
    t.string  "filename"
  end

  create_table "mark_to_add_hotels", :force => true do |t|
    t.integer  "forum_hotel_id"

  end

  create_table "matched_forum_hotel_table", :id => false, :force => true do |t|
    t.integer "uid",            :null => false
    t.integer "forum_hotel_id"
    t.integer "hotel_id"
    t.float   "match_ratio"
  end

  create_table "possible_forum_hotel_match_table", :id => false, :force => true do |t|
    t.integer "uid",                :null => false
    t.integer "unmatched_entry_id"
    t.integer "hotel_id"
    t.float   "percentage_match"
  end

  create_table "priceline_area_city_table", :id => false, :force => true do |t|
    t.integer "uid",               :null => false
    t.integer "priceline_area_id"
    t.integer "city_id"
  end

  create_table "priceline_area_table", :id => false, :force => true do |t|
    t.integer "uid",                 :null => false
    t.string  "name", :limit => 500
  end

  create_table "priceline_region_hotel_mapping", :id => false, :force => true do |t|
    t.integer "uid",                 :null => false
    t.integer "hotel_id"
    t.integer "priceline_region_id"
  end

  create_table "priceline_region_point_table", :id => false, :force => true do |t|
    t.integer "uid",                 :null => false
    t.integer "priceline_region_id"
    t.integer "order_id"
    t.float   "latitude"
    t.float   "longitude"
  end

  create_table "priceline_region_table", :id => false, :force => true do |t|
    t.integer "uid",                              :null => false
    t.string  "priceline_id",      :limit => 100
    t.string  "name",              :limit => 500
    t.float   "latitude"
    t.float   "longitude"
    t.integer "active"
    t.string  "star_availability", :limit => 500
  end

  create_table "priceline_regions_cities_mapping", :id => false, :force => true do |t|
    t.integer "uid",                                :null => false
    t.integer "city_id"
    t.string  "priceline_region_id", :limit => 100
  end

  create_table "processed_raw_forum_data", :id => false, :force => true do |t|
    t.integer "uid",                         :null => false
    t.string  "hotel_name",   :limit => 500
    t.string  "city_area",    :limit => 500
    t.string  "region",       :limit => 500
    t.string  "star",         :limit => 500
    t.string  "state",        :limit => 500
    t.string  "url",          :limit => 500
    t.string  "target_site",  :limit => 500
    t.string  "source_forum", :limit => 500
  end

  create_table "unmatched_forum_hotel_table", :id => false, :force => true do |t|
    t.integer "uid",                           :null => false
    t.integer "forum_hotel_id"
    t.integer "city_id"
    t.integer "area_id"
    t.integer "region_id"
    t.string  "source_forum",   :limit => 500
    t.string  "target_site",    :limit => 500
    t.string  "source_url",     :limit => 500
    t.integer "matched"
  end

end
