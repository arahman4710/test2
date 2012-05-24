count = 0

until $? == 1 do
	`ruby pl.rb`

	if count < 20 then
		count += 1
	else
		break
	end
end