SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='TRADITIONAL';

CREATE SCHEMA IF NOT EXISTS `acuity` DEFAULT CHARACTER SET latin1 COLLATE latin1_swedish_ci ;
USE `acuity` ;

-- -----------------------------------------------------
-- Table `acuity`.`Cities`
-- -----------------------------------------------------
CREATE  TABLE IF NOT EXISTS `acuity`.`Cities` (
  `CityId` INT NOT NULL AUTO_INCREMENT ,
  `City` VARCHAR(255) NOT NULL ,
  `State` VARCHAR(255) NULL ,
  `Country` VARCHAR(255) NOT NULL ,

  PRIMARY KEY (`CityId`) )
ENGINE = Innodb ;


-- -----------------------------------------------------
-- Table `acuity`.`Hotels`
-- -----------------------------------------------------
CREATE  TABLE IF NOT EXISTS `acuity`.`Hotels` (
  `HotelId` INT NOT NULL AUTO_INCREMENT ,
  `HotelName` VARCHAR(255) NOT NULL ,
  `HotelAddress` VARCHAR(255) NOT NULL ,
  `Cities_CityId` INT NOT NULL ,
  `Latitude` DOUBLE NULL ,
  `Longitude` DOUBLE NULL ,
  `Rating` VARCHAR(255) NULL ,
  `HotelsCombinedId` INT NULL ,
  `HotelFileName` VARCHAR(255) NULL ,
  `URL` VARCHAR(255),   -- hotel website if we know it. 

  PRIMARY KEY (`HotelId`) ,

  INDEX `fk_Hotels_Cities1` (`Cities_CityId` ASC) ,

  CONSTRAINT `fk_Hotels_Cities1`
    FOREIGN KEY (`Cities_CityId` )
    REFERENCES `acuity`.`Cities` (`CityId` )
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = Innodb ;


-- -----------------------------------------------------
-- Table `acuity`.`KayakHotels`
-- -----------------------------------------------------
CREATE  TABLE IF NOT EXISTS `acuity`.`KayakHotels` (
  `KayakId` INT NOT NULL AUTO_INCREMENT ,
  `Hotels_HotelId` INT NOT NULL ,
  `KayakName` VARCHAR(255) NOT NULL ,

  PRIMARY KEY (`KayakId`) ,

  INDEX `fk_KayakId_Hotels` (`Hotels_HotelId` ASC) ,

  CONSTRAINT `fk_KayakId_Hotels`
    FOREIGN KEY (`Hotels_HotelId` )
    REFERENCES `acuity`.`Hotels` (`HotelId` )
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = Innodb ;


-- -----------------------------------------------------
-- Table `acuity`.`PricelineRegions`
-- -----------------------------------------------------
CREATE  TABLE IF NOT EXISTS `acuity`.`PricelineRegions` (
  `PricelineRegionId` INT NOT NULL AUTO_INCREMENT ,
  `RegionName` VARCHAR(255) NOT NULL ,
  `Cities_CityId` INT NOT NULL ,
  `Latitude` DOUBLE NOT NULL ,
  `Longitude` DOUBLE NOT NULL ,
  `Active` INT NOT NULL ,

  PRIMARY KEY (`PricelineRegionId`) ,

  INDEX `fk_PricelineRegions_Cities1` (`Cities_CityId` ASC) ,

  CONSTRAINT `fk_PricelineRegions_Cities1`
    FOREIGN KEY (`Cities_CityId` )
    REFERENCES `acuity`.`Cities` (`CityId` )
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = Innodb ;


-- -----------------------------------------------------
-- Table `acuity`.`PricelineId`
-- -----------------------------------------------------
CREATE  TABLE IF NOT EXISTS `acuity`.`PricelineId` (
  `PricelineId` INT NOT NULL AUTO_INCREMENT ,
  `Hotels_HotelId` INT NOT NULL ,
  `PricelineRegions_PricelineRegionId` INT NOT NULL ,
  `Active` INT NOT NULL ,

  PRIMARY KEY (`PricelineId`) ,

  INDEX `fk_PricelineId_Hotels1` (`Hotels_HotelId` ASC) ,
  INDEX `fk_PricelineId_PricelineRegions1` (`PricelineRegions_PricelineRegionId` ASC) ,

  CONSTRAINT `fk_PricelineId_Hotels1`
    FOREIGN KEY (`Hotels_HotelId` )
    REFERENCES `acuity`.`Hotels` (`HotelId` )
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_PricelineId_PricelineRegions1`
    FOREIGN KEY (`PricelineRegions_PricelineRegionId` )
    REFERENCES `acuity`.`PricelineRegions` (`PricelineRegionId` )
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = Innodb ;


-- -----------------------------------------------------
-- Table `acuity`.`HotwireRegions`
-- -----------------------------------------------------
CREATE  TABLE IF NOT EXISTS `acuity`.`HotwireRegions` (
  `HotwireRegionId` INT NOT NULL AUTO_INCREMENT ,
  `RegionName` VARCHAR(255) NOT NULL ,
  `Cities_CityId` INT NOT NULL ,
  `Latitude` DOUBLE NOT NULL ,
  `Longitude` DOUBLE NOT NULL ,
  `Active` INT NOT NULL ,

  PRIMARY KEY (`HotwireRegionId`) ,

  INDEX `fk_HotwireRegions_Cities1` (`Cities_CityId` ASC) ,

  CONSTRAINT `fk_HotwireRegions_Cities1`
    FOREIGN KEY (`Cities_CityId` )
    REFERENCES `acuity`.`Cities` (`CityId` )
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = Innodb ;


-- -----------------------------------------------------
-- Table `acuity`.`HotwireId`
-- -----------------------------------------------------
CREATE  TABLE IF NOT EXISTS `acuity`.`HotwireId` (
  `HotwireId` INT NOT NULL AUTO_INCREMENT ,
  `Hotels_HotelId` INT NOT NULL ,
  `HotwireRegions_HotwireRegionId` INT NOT NULL ,
  `Active` INT NOT NULL ,

  PRIMARY KEY (`HotwireId`) ,

  INDEX `fk_HotwireId_Hotels1` (`Hotels_HotelId` ASC) ,
  INDEX `fk_HotwireId_HotwireRegions1` (`HotwireRegions_HotwireRegionId` ASC) ,

  CONSTRAINT `fk_HotwireId_Hotels1`
    FOREIGN KEY (`Hotels_HotelId` )
    REFERENCES `acuity`.`Hotels` (`HotelId` )
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_HotwireId_HotwireRegions1`
    FOREIGN KEY (`HotwireRegions_HotwireRegionId` )
    REFERENCES `acuity`.`HotwireRegions` (`HotwireRegionId` )
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = Innodb ;


-- -----------------------------------------------------
-- Table `acuity`.`PricelinePoints`
-- -----------------------------------------------------
CREATE  TABLE IF NOT EXISTS `acuity`.`PricelinePoints` (
  `PointId` INT NOT NULL AUTO_INCREMENT ,
  `PricelineRegions_PricelineRegionId` INT NOT NULL ,
  `OrderId` INT NOT NULL ,
  `Latitude` DOUBLE NOT NULL ,
  `Longitude` DOUBLE NOT NULL ,

  PRIMARY KEY (`PointId`) ,

  INDEX `fk_PricelinePoints_PricelineRegions1` (`PricelineRegions_PricelineRegionId` ASC) ,

  CONSTRAINT `fk_PricelinePoints_PricelineRegions1`
    FOREIGN KEY (`PricelineRegions_PricelineRegionId` )
    REFERENCES `acuity`.`PricelineRegions` (`PricelineRegionId` )
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = Innodb ;


-- -----------------------------------------------------
-- Table `acuity`.`HotwirePoints`
-- -----------------------------------------------------
CREATE  TABLE IF NOT EXISTS `acuity`.`HotwirePoints` (
  `PointId` INT NOT NULL AUTO_INCREMENT ,
  `HotwireRegions_HotwireRegionId` INT NOT NULL ,
  `OrderId` INT NOT NULL ,
  `Latitude` DOUBLE NOT NULL ,
  `Longitude` DOUBLE NOT NULL ,

  PRIMARY KEY (`PointId`) ,

  INDEX `fk_HotwirePoints_HotwireRegions1` (`HotwireRegions_HotwireRegionId` ASC) ,

  CONSTRAINT `fk_HotwirePoints_HotwireRegions1`
    FOREIGN KEY (`HotwireRegions_HotwireRegionId` )
    REFERENCES `acuity`.`HotwireRegions` (`HotwireRegionId` )
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = Innodb ;


-- -----------------------------------------------------
-- Table `acuity`.`BftPosts`
-- -----------------------------------------------------
CREATE  TABLE IF NOT EXISTS `acuity`.`BftPosts` (
  `BftPostId` INT NOT NULL AUTO_INCREMENT ,
  `PricelineId_PricelineId` INT NOT NULL ,
  `TopicNumber` INT NULL ,
  `Replies` INT NULL ,
  `HotelName` VARCHAR(255) NOT NULL ,
  `CheckInDate` DATE NOT NULL ,
  `Nights` INT NULL ,
  `Price` INT NULL ,
  `Rating` INT NOT NULL ,

  PRIMARY KEY (`BftPostId`) ,

  INDEX `fk_BftPosts_PricelineId1` (`PricelineId_PricelineId` ASC) ,

  CONSTRAINT `fk_BftPosts_PricelineId1`
    FOREIGN KEY (`PricelineId_PricelineId` )
    REFERENCES `acuity`.`PricelineId` (`PricelineId` )
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = Innodb ;


-- -----------------------------------------------------
-- Table `acuity`.`BbPricelinePosts`
-- -----------------------------------------------------
CREATE  TABLE IF NOT EXISTS `acuity`.`BbPricelinePosts` (
  `BbPricelinePostId` INT NOT NULL AUTO_INCREMENT ,
  `PricelineId_PricelineId` INT NOT NULL ,
  `TopicNumber` INT NULL ,
  `Replies` INT NULL ,
  `HotelName` VARCHAR(255) NOT NULL ,
  `CheckInDate` DATE NOT NULL ,
  `Nights` INT NULL ,
  `Price` INT NULL ,
  `Rating` INT NOT NULL ,

  PRIMARY KEY (`BbPricelinePostId`) ,

  INDEX `fk_BbPricelinePosts_PricelineId1` (`PricelineId_PricelineId` ASC) ,

  CONSTRAINT `fk_BbPricelinePosts_PricelineId1`
    FOREIGN KEY (`PricelineId_PricelineId` )
    REFERENCES `acuity`.`PricelineId` (`PricelineId` )
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = Innodb ;


-- -----------------------------------------------------
-- Table `acuity`.`BbHotwirePosts`
-- -----------------------------------------------------
CREATE  TABLE IF NOT EXISTS `acuity`.`BbHotwirePosts` (
  `BbHotwirePostId` INT NOT NULL AUTO_INCREMENT ,
  `HotwireId_HotwireId` INT NOT NULL ,
  `TopicNumber` INT NULL ,
  `Replies` INT NULL ,
  `HotelName` VARCHAR(255) NOT NULL ,
  `CheckInDate` DATE NOT NULL ,
  `Nights` INT NULL ,
  `Price` INT NULL ,
  `Rating` INT NOT NULL ,

  PRIMARY KEY (`BbHotwirePostId`) ,

  INDEX `fk_BbHotwirePosts_HotwireId1` (`HotwireId_HotwireId` ASC) ,

  CONSTRAINT `fk_BbHotwirePosts_HotwireId1`
    FOREIGN KEY (`HotwireId_HotwireId` )
    REFERENCES `acuity`.`HotwireId` (`HotwireId` )
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = Innodb ;


-- -----------------------------------------------------
-- Table `acuity`.`HotelNames`
-- -----------------------------------------------------
CREATE  TABLE IF NOT EXISTS `acuity`.`HotelNames` (
  `Id` INT NOT NULL AUTO_INCREMENT ,
  `PricelineId_PricelineId` INT NOT NULL ,
  `HotelName` VARCHAR(255) NOT NULL ,
  `Rating` INT NOT NULL ,
  `WinRate` INT NOT NULL ,

  PRIMARY KEY (`Id`) ,

  INDEX `fk_HotelNames_PricelineId1` (`PricelineId_PricelineId` ASC) ,

  CONSTRAINT `fk_HotelNames_PricelineId1`
    FOREIGN KEY (`PricelineId_PricelineId` )
    REFERENCES `acuity`.`PricelineId` (`PricelineId` )
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = Innodb ;


-- -----------------------------------------------------
-- Table `acuity`.`PricelineBids`
-- -----------------------------------------------------
CREATE  TABLE IF NOT EXISTS `acuity`.`PricelineBids` (
  `PricelineBidId` INT NOT NULL AUTO_INCREMENT ,
  `PricelineId_PricelineId` INT NOT NULL ,
  `BidDate` DATETIME NOT NULL, 
  `CheckIn` DATE NOT NULL ,
  `Nights` INT NOT NULL ,
  `Rooms` INT NOT NULL ,
  `RoomCost` DOUBLE NOT NULL ,
  `Subtotal` DOUBLE NOT NULL ,
  `TaxesFees` DOUBLE NOT NULL ,
  `Total` DOUBLE NOT NULL ,

  PRIMARY KEY (`PricelineBidId`) ,

  INDEX `fk_PricelineBids_PricelineId1` (`PricelineId_PricelineId` ASC) ,

  CONSTRAINT `fk_PricelineBids_PricelineId1`
    FOREIGN KEY (`PricelineId_PricelineId` )
    REFERENCES `acuity`.`PricelineId` (`PricelineId` )
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = Innodb ;


-- -----------------------------------------------------
-- Table `acuity`.`HotwireBids`
-- -----------------------------------------------------
CREATE  TABLE IF NOT EXISTS `acuity`.`HotwireBids` (
  `HotwireBidId` INT NOT NULL AUTO_INCREMENT ,
  `HotwireId_HotwireId` INT NOT NULL ,
  `DateFetched` DATETIME NOT NULL, 
  `CheckIn` DATE NOT NULL ,
  `Nights` INT NOT NULL ,
  `Rooms` INT NOT NULL ,
  `RoomCost` DOUBLE NOT NULL ,
  `Subtotal` DOUBLE NOT NULL ,
  `TaxesFees` DOUBLE NOT NULL ,
  `Total` DOUBLE NOT NULL ,

  PRIMARY KEY (`HotwireBidId`) ,

  INDEX `fk_HotwireBids_HotwireId1` (`HotwireId_HotwireId` ASC) ,

  CONSTRAINT `fk_HotwireBids_HotwireId1`
    FOREIGN KEY (`HotwireId_HotwireId` )
    REFERENCES `acuity`.`HotwireId` (`HotwireId` )
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = Innodb ;


-- -----------------------------------------------------
-- Table `acuity`.`Amenities`
-- -----------------------------------------------------
CREATE  TABLE IF NOT EXISTS `acuity`.`Amenities` (
  `AmenityId` INT NOT NULL AUTO_INCREMENT ,
  `AmenityName` VARCHAR(45) NOT NULL , -- long name 
  `HWAmenityAbbreviation` CHAR(2),     -- hotwire 2 char abbreviation 

  PRIMARY KEY (`AmenityId`) )
ENGINE = Innodb ;


-- -----------------------------------------------------
-- Table `acuity`.`HotelAmenities`
-- -----------------------------------------------------
CREATE  TABLE IF NOT EXISTS `acuity`.`HotelAmenities` (
  `HotelAmenityId` INT NOT NULL AUTO_INCREMENT ,
  `Hotels_HotelId` INT NOT NULL ,
  `Amenities_AmenityId` INT NOT NULL ,
  `CreatedAt` DATETIME NOT NULL ,
  `UpdatedAt` DATETIME NOT NULL ,

  PRIMARY KEY (`HotelAmenityId`) ,

  INDEX `fk_Amenities_Hotels1` (`Hotels_HotelId` ASC) ,
  INDEX `fk_HotelAmenities_Amenities1` (`Amenities_AmenityId` ASC) ,

  CONSTRAINT `fk_Amenities_Hotels1`
    FOREIGN KEY (`Hotels_HotelId` )
    REFERENCES `acuity`.`Hotels` (`HotelId` )
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_HotelAmenities_Amenities1`
    FOREIGN KEY (`Amenities_AmenityId` )
    REFERENCES `acuity`.`Amenities` (`AmenityId` )
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = Innodb ;



SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;
