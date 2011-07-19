class HotelsController < ApplicationController
  def index
    @cities = City.all
  end

def get_regions
  request_city=current_user.cities
  @regionlist=[]
  @ri=0
  request_city.each { |i|
   if i
    @allregions=Region.all(:conditions => ["city_id = ?",i])
  for tempregion in @allregions
    @regionlist[@ri]=[]
    for points in tempregion.points
        @pointlist={:clt => tempregion.latitude,:clg => tempregion.longitude, :id => tempregion.id, :lat => points.latitude, :lng => points.longitude, :name => tempregion.name}
        @regionlist[@ri]<<@pointlist
    end
    @ri+=1
  end
   end
  }
   @return_obj = [@regionlist].to_json
    render :text => @return_obj
end
  
def get_states
  @allstate=State.all
  @statelist=[]
  for tempstate in @allstate
    @SL={:name => tempstate.name, :lat => tempstate.latitude.to_f, :lng => tempstate.longitude.to_f, :code => tempstate.code, :id => tempstate.id}
    @statelist<<@SL
  end
    @return_obj = [@statelist].to_json
    render :text => @return_obj
end
 
  def get_hotels
    var=params[:cityid].to_i
    @selectedCity=City.find_by_id(var)
    @Chotels=@selectedCity.hotels
    @HotelList = []
    if current_user.cities.find_by_id(var)
      for temphotel in @Chotels
      @TH={:lat => temphotel.latitude.to_f, :lng => temphotel.longitude.to_f}

      @HotelList<<@TH
      end
    end
    @return_obj = [@HotelList].to_json
    render :text => @return_obj
    
  end

    def loadmarker
    minlt=params[:minlat].to_f
    maxlt=params[:maxlat].to_f
    minlg=params[:minlng].to_f
    maxlg=params[:maxlng].to_f
    @selectedCity=City.all(:conditions =>["latitude >= ? AND latitude <= ? AND longitude >= ? AND longitude <= ?",minlt,maxlt,minlg,maxlg])
    @HotelList = []
      if current_user
        @cur_user=current_user.cities
      #@Chotels=@selectedCity.Hotels
    
    for temphotel in @selectedCity
      if @cur_user.find_by_id(temphotel.id.to_i)
      @TH={:lat => temphotel.latitude.to_f, :lng => temphotel.longitude.to_f, :name => temphotel.name, :sum => temphotel.numberofhotels, :id => temphotel.id, :paid_for => '1'}
      else
      @TH={:lat => temphotel.latitude.to_f, :lng => temphotel.longitude.to_f, :name => temphotel.name, :sum => temphotel.numberofhotels, :id => temphotel.id, :paid_for => '0'}
      end
      @HotelList<<@TH
    end
      else
        for temphotel in @selectedCity
          @TH={:lat => temphotel.latitude.to_f, :lng => temphotel.longitude.to_f, :name => temphotel.name, :sum => temphotel.numberofhotels, :id => temphotel.id, :paid_for => '0'}
          @HotelList<<@TH
        end
      end

    @return_obj = [@HotelList].to_json
    render :text => @return_obj
  end

  def show
    @hotel = Hotel.find(params[:id])
  end
  
  def new
    @hotel = Hotel.new
  end
  
  def create
    @hotel = Hotel.new(params[:hotel])
    if @hotel.save
      flash[:notice] = "Successfully created hotel."
      redirect_to @hotel
    else
      render :action => 'new'
    end
  end
  
  def edit
    @hotel = Hotel.find(params[:id])
  end
  
  def update
    @hotel = Hotel.find(params[:id])
    if @hotel.update_attributes(params[:hotel])
      flash[:notice] = "Successfully updated hotel."
      redirect_to @hotel
    else
      render :action => 'edit'
    end
  end
  
  def destroy
    @hotel = Hotel.find(params[:id])
    @hotel.destroy
    flash[:notice] = "Successfully destroyed hotel."
    redirect_to hotels_url
  end

end
