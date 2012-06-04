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

ActiveRecord::Schema.define(:version => 20101114045116) do

  create_table "cities", :force => true do |t|
    t.string   "name"
    t.integer  "numberofhotels"
    t.float    "latitude"
    t.float    "longitude"
    t.datetime "created_at"
    t.datetime "updated_at"
  end

  create_table "cityuser", :force => true do |t|
    t.integer "city_id"
    t.integer "user_id"
  end

  create_table "cityusers", :force => true do |t|
    t.integer  "city_id"
    t.integer  "user_id"
    t.datetime "created_at"
    t.datetime "updated_at"
  end

  create_table "hotels", :force => true do |t|
    t.string   "name"
    t.float    "rating"
    t.integer  "city_id"
    t.string   "state"
    t.string   "country"
    t.string   "address"
    t.float    "minimumrate"
    t.string   "currency"
    t.float    "latitude"
    t.float    "longitude"
    t.integer  "ratingcount"
    t.float    "userrating"
    t.integer  "property"
    t.datetime "created_at"
    t.datetime "updated_at"
  end

  create_table "points", :force => true do |t|
    t.integer "region_id"
    t.integer "order_id"
    t.float   "latitude"
    t.float   "longitude"
  end

  create_table "regions", :force => true do |t|
    t.string  "name"
    t.integer "city_id"
    t.float   "latitude"
    t.float   "longitude"
    t.integer "active"
  end

  create_table "states", :force => true do |t|
    t.string "name"
    t.string "code"
    t.float  "latitude"
    t.float  "longitude"
  end

  create_table "user_sessions", :force => true do |t|
    t.string   "username"
    t.string   "password"
    t.datetime "created_at"
    t.datetime "updated_at"
  end

  create_table "users", :force => true do |t|
    t.string   "username"
    t.string   "email"
    t.string   "password"
    t.string   "crypted_password"
    t.string   "password_salt"
    t.string   "persistence_token"
    t.string   "perishable_token"
    t.boolean  "active",            :default => false
    t.datetime "created_at"
    t.datetime "updated_at"
    t.integer  "state_id"
    t.integer  "city_id"
  end

end
