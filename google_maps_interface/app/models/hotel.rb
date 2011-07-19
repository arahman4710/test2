class Hotel < ActiveRecord::Base
  attr_accessible :name, :rating, :city_id, :state, :country, :address, :minimumrate, :currency, :latitude, :longitude, :ratingcount, :userrating, :property
belongs_to :city

end
