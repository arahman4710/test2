require 'test_helper'

class HotelTest < ActiveSupport::TestCase
  def test_should_be_valid
    assert Hotel.new.valid?
  end
end
