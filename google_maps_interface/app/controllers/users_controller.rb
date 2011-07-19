class UsersController < ApplicationController
  def new
    @user = User.new
    @paid_city=current_user.Cities
 #   @cities_user=Cities_users.new
    @City=City.find(:all)
    respond_to do |format|
      format.html # new.html.erb
      format.xml  { render :xml => @user }
    end

  end
    def check_authentication
    @auth=0
    @paid_c=[]
    if current_user
      @auth=1
      if current_user.cities
          for paid_cities in current_user.cities
            @paid_c<<paid_cities.id
          end
      end
      @return_obj = [@auth,@paid_c].to_json
    render :text => @return_obj
    else
      @auth=0
    @return_obj = [@auth].to_json
    render :text => @return_obj
    end
  end

  def create
  @user = User.new
 # params[:cities_users].each_value do |task|
  #  @user.cities.build(task) unless task.values.all?(&:blank?)
 # end
    if @user.signup!(params)
      @user.deliver_activation_instructions!
      flash[:notice] = "Your account has been created. Please check your e-mail for your account activation instructions!"
      #redirect_to root_url
   respond_to do |format|
      format.html { redirect_to root_url }
        format.xml  { render :xml => @user, :status => :created, :location => @user }
   end
    else
      respond_to do |format|
        format.html { render :action => "new" }
        format.xml  { render :xml => @user.errors, :status => :unprocessable_entity }

      end
      #render :action => 'new'
    end
  end
  def add_city
  @task = Cities.new
end
  def edit
    @user = current_user
  end
  
  def update
    @user = current_user
    
    if @user.update_attributes(params[:user])
      flash[:notice] = "Successfully Updated."
    #  redirect_to root_url
    respond_to do |format|
      format.html { redirect_to root_url }
        format.xml  { head :ok }
      end
    else
    #  render :action => 'edit'
    respond_to do |format|
      format.html { render :action => "edit" }
        format.xml  { render :xml => @user.errors, :status => :unprocessable_entity }
    end
    end
  end

 
end
