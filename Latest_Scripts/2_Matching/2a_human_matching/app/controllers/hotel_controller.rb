class HotelController < ApplicationController



  def index

    @unmatched_hotel = UnmatchedForumHotel.find(:all)

  end

  def add_index

    @marked_for_add = MarkToAddHotels.find(:all)

  end

  def detail

    current_id = params[:id].to_i

    @unmatched_hotel = UnmatchedForumHotel.find_by_uid(current_id)

    @data = nil
    @matched = nil
    @next = current_id.to_i + 1
    @prev = current_id.to_i - 1
    @current = current_id
    @total = UnmatchedForumHotel.count()

    if not params[:usr_input].nil?

        @data = params[:usr_input]

        usr_input = @data.to_i

        if usr_input == @unmatched_hotel.get_possible_hotel_matches.length

          mark_for_add = MarkToAddHotels.new
          mark_for_add.forum_hotel_id = @unmatched_hotel.forum_hotel_id
          mark_for_add.save()

          return

        end

        if usr_input == @unmatched_hotel.get_possible_hotel_matches.length + 1

          redirect_to :action => 'detail', :id => @next

          return
        end

        possible_htl_mtch = @unmatched_hotel.get_possible_hotel_matches[usr_input]

        matched_htl = possible_htl_mtch.get_hotel_info

        @usrchoice = matched_htl.name

        new_match = MatchedForumHotel.new
        new_match.uid = MatchedForumHotel.count() + 1
        new_match.hotel_id = matched_htl.hotel_id
        new_match.forum_hotel_id = @unmatched_hotel.forum_hotel_id
        new_match.match_ratio = possible_htl_mtch.percentage_match
        @unmatched_hotel.matched = matched_htl.hotel_id

        new_match.save()
        @unmatched_hotel.save()

   end

   if @unmatched_hotel.matched != 0
        @matched = @unmatched_hotel.get_matched_hotel_info
   end




    return

  end

  def add
    @unmatched_hotel = MarkToAddHotels.find_by_id(params[:id]).get_forum_hotel_info
    @hotel = Hotel.new

    return

  end

  def create
    @hotel = Hotel.new(params[:hotel])

    respond_to do |format|
      if @hotel.save
        flash[:notice] = 'Hotel was successfully created.'
        format.html { redirect_to(@hotel) }
        format.xml  { render :xml => @hotel, :status => :created, :location => @hotel }
      else
        format.html { render :action => "new" }
        format.xml  { render :xml => @hotel.errors, :status => :unprocessable_entity }
      end
    end
  end
  
end
