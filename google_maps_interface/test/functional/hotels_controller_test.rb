require 'test_helper'

class HotelsControllerTest < ActionController::TestCase
  def test_index
    get :index
    assert_template 'index'
  end
  
  def test_show
    get :show, :id => Hotel.first
    assert_template 'show'
  end
  
  def test_new
    get :new
    assert_template 'new'
  end
  
  def test_create_invalid
    Hotel.any_instance.stubs(:valid?).returns(false)
    post :create
    assert_template 'new'
  end

  def test_create_valid
    Hotel.any_instance.stubs(:valid?).returns(true)
    post :create
    assert_redirected_to hotel_url(assigns(:hotel))
  end
  
  def test_edit
    get :edit, :id => Hotel.first
    assert_template 'edit'
  end
  
  def test_update_invalid
    Hotel.any_instance.stubs(:valid?).returns(false)
    put :update, :id => Hotel.first
    assert_template 'edit'
  end

  def test_update_valid
    Hotel.any_instance.stubs(:valid?).returns(true)
    put :update, :id => Hotel.first
    assert_redirected_to hotel_url(assigns(:hotel))
  end
  
  def test_destroy
    hotel = Hotel.first
    delete :destroy, :id => hotel
    assert_redirected_to hotels_url
    assert !Hotel.exists?(hotel.id)
  end
end
