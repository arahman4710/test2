<?php
	
	// PHP5 Implementation - uses MySQLi.
	// mysqli('localhost', 'yourUsername', 'yourPassword', 'yourDatabase');
$mysql_host = "the_web_host";
$mysql_database = "name_of_database";
$mysql_user = "username";
$mysql_password = "password";

	$db = new mysqli($mysql_host, $mysql_user ,$mysql_password, $mysql_database);
	
	if(!$db) {
		// Show error if we cannot connect.
		echo 'ERROR: Could not connect to the database.';
	} else {
		// Is there a posted query string?
		if(isset($_POST['queryString'])) {
			$queryString = $db->real_escape_string($_POST['queryString']);
			
			// Is the string length greater than 0?
			
			if(strlen($queryString) >2) {
				// Run the query: We use LIKE '$queryString%'
				// The percentage sign is a wild-card, in my example of countries it works like this...
				// $queryString = 'Uni';
				// Returned data = 'United States, United Kindom';

                                // First we deal with the cities
                                $city_query = "SELECT cityName,StateName,countryCode FROM CityLocations C WHERE C.StateName LIKE '$queryString%' OR C.cityName LIKE '$queryString%' OR C.countryName LIKE '$queryString%' LIMIT 5";
				$query = $db->query($city_query);
                                $city_count = $query->num_rows;
				if($query) {
                                             while ($result = $query->fetch_array(MYSQLI_ASSOC)) {
						// Format the results, im using <li> for the list
						// The onClick function fills the textbox with the result.
                                                //highlight the query in the display
                                                $display = $result["cityName"].', '.$result["StateName"].' '.$result["countryCode"];
                                                $replace = '<span>'.ucfirst($queryString).'</span>';
                                                $display2 = str_ireplace($queryString, $replace, $display);
                                                echo '<li onClick="fill(\''.$display.'\');">'.$display2.'</li>';
                                                }
	         		}
                                
                                //Next the Hotels
                                $hotel_limit = 10 - $city_count;
                                
				$hotel_query = "SELECT hotelName,cityName,stateName,countryName FROM hotels h WHERE h.hotelName REGEXP '[[:<:]]".$queryString."[[:>:]]' OR h.cityName LIKE '$queryString%' OR h.stateName LIKE '$queryString%' OR h.countryName LIKE '$queryString%' LIMIT ".$hotel_limit;
				$query = $db->query($hotel_query);
				if($query) {
					
                                             while ($result = $query->fetch_array(MYSQLI_ASSOC)) {
                                                if ($result["stateName"]){  //this field is empty for canadian hotels
                                                $display = $result["hotelName"]. ' - '.$result["cityName"].', '.$result["stateName"];
                                                }
                                                else
                                                  $display = $result["hotelName"]. ' - '.$result["cityName"];

                                                //highlight the query in the display
                                                $replace = '<span>'.ucfirst($queryString).'</span>';
                                                $display2 = str_ireplace($queryString, $replace, $display);
                                                echo '<li class="hotels" onClick="fill(\''.$display.'\');">'.$display2.'</li>';
	         		}
				} else {
					echo 'ERROR: There was a problem with the query.';
				}
			} else {
				// Dont do anything.
			} // There is a queryString.
		} else {
			echo 'There should be no direct access to this script!';
		}
	}
?>		