
#pixels of images are stored as number in arrays
from Tkinter import *
from PIL import Image
import ImageChops
import math
import numpy
import time
import copy
import string
import ImageTk
from tkFileDialog import askopenfilename


def init():
    data.level = 164
    data.guessFontCounter = 0
    data.guessFontScore = 10000
    data.guessFont = "timesNewRoman"
    data.lastPixel = 1
    data.progressBar = 0
    data.allFonts = ["timesNewRoman","microsoftSansSerif"] 
    data.allLetters = dict()
    data.image = Image.open("testPicture4.png")
    data.image2 = Image.open("firstLine.png")
    data.image3 = Image.open("testPicture8.png")
    data.image4 = Image.open("testPicture7.png")
    data.image5 = Image.open("savedI.png")
    data.image6 = Image.open("guessFontChecker.png")

def run():
    global root
    class Struct: pass
    global data
    data = Struct()
    init()

run()

def convertImageTo2Bit(image,level = data.level):
    image = image.convert("L")      #converts to 255 bits
    (width,height) = image.size
    bwImage = Image.new("L",(width,height))   #new image in black and white
    allWhitePixel = 255 
    middleNumberPixel = level  #default is 164
    for i in xrange(len(image.getdata())):
        x = i%width
        y = i/width
        pixel = image.getdata()[i]
        if pixel/middleNumberPixel == 0: #pixel is closer to black
            newPixel = 0
        else:       
            newPixel = allWhitePixel
        bwImage.putpixel((x,y),newPixel)
    #bwImage.show()
    return bwImage



def fontLoad(font="timesNewRoman",letters=data.allLetters):
    upperLetters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ."
    lowerLetters = "abcdefghijklmnopqrstuvwxyz1234567890"
    #try:
    for letter in upperLetters:
        currentImage = convertImageTo2Bit(Image.open(font+"-upper-"+letter+".png"))
        data.allLetters[letter] = currentImage
    for letter in lowerLetters:
        currentImage = convertImageTo2Bit(Image.open(font+"-lower-"+letter+".png"))
        data.allLetters[letter] = currentImage
    return 0

def findBestRatio(letter=data.allLetters):
    fontLoad("timesNewRoman")
    for letter in data.allLetters:
        print "letter",letter
        print "ratio:", 1.0*data.allLetters[letter].size[0]/data.allLetters[letter].size[1]

def compareImageToLetters(image,font,level=data.level,letters=data.allLetters):
    font1 = font
    try:
        image1 = convertImageTo2Bit(image,level)
        bestFitLetter = ""    
        letterscopy = copy.copy(letters)
        bestFitCount = 10000000000
        thresholdLevel = 1
        (width,height) = image1.size
        if "Sans" in font:      #special cases
            if (containsNoWhite(image1) and (height>5)):
                return "I"
            elif (width<=1 and height>5):
                return "i"
        for letter in letterscopy:  #for every letter
            letterFitCount = 0
            letterscopy[letter] = letters[letter].resize((width,height))
            letterFitCount = imageCompare(image1,letterscopy[letter])
            if (letterFitCount < thresholdLevel):
                bestFitLetter = letter
                break
            elif (letterFitCount < bestFitCount):
                bestFitCount = letterFitCount
                bestFitLetter = letter
        return bestFitLetter
    except:
        return ""

def imageCompare(im1, im2):
    #Obtained from http://code.activestate.com/recipes/577630-comparing-two-images/
    "Calculate the root-mean-square difference between two images"
    diff = ImageChops.difference(im1, im2)
    h = diff.histogram()
    sq = (value*(idx**2) for idx, value in enumerate(h))
    sum_of_squares = sum(sq)
    rms = math.sqrt(sum_of_squares/float(im1.size[0] * im1.size[1]))
    return rms


def containsNoWhite(image):
    pixels = image.getdata()
    for pixel in pixels:
        if pixel == 255:
            return False
    return True

def fontTypes():
    for fonts in data.allFonts:
        print fonts

def guessFont(image,fonts=data.allFonts,letters=data.allLetters):
    data.guessFontScore = 10000
    data.guessFont = ""
    for currentFont in fonts:    #for every font
        fontLoad(currentFont,data.allLetters)
        #for letter in letters: #for every letter in this font
        image = convertImageTo2Bit(image)
        bestFitLetter = ""    
        letterscopy = copy.copy(letters)
        bestFitCount = 10000000000
        thresholdLevel = 1
        (width,height) = image.size
        for letter in letterscopy:  #for every letter
            letterFitCount = 0
            letterscopy[letter] = letters[letter].resize((width,height))
            letterFitCount = imageCompare(image,letterscopy[letter])
            if (letterFitCount < bestFitCount):
                bestFitCount = letterFitCount
        if bestFitCount < data.guessFontScore:
            bestGuessFont = currentFont
            data.guessFontScore = bestFitCount
        fontLoad(bestGuessFont,data.allLetters)
    return bestGuessFont
            

def runOcr(image,font="not guessed"):
    #main ocr function
    data.guessFontCounter = 0
    if font == "not guessed":
        words = addLettersGuess(image,data.guessFont)
    elif "Sans" in font:
        data.level = 150
        words = addLettersSans(image,font)
    else:
        words = addLetters(image,font)
    return words

def addLettersSansGuess(image,font="microsoftSansSerif"):
    #guessing the font of the letter then running the ocr (Sans fonts)
    if fontLoad(data.guessFont) == None:
        print "Try again!"
        return
    image1 = image.convert("L")
    BitImage = convertImageTo2Bit(image1)
    boundedImage = initialBoxItIn(BitImage)
    boundedImage.save("savedImage2.png")
    #boundedImage.show()
    yDimensions = lineHorizontally(boundedImage)
    newSentence = ""
    #print "y:", yDimensions
    maxLetterSpace = 4
    (width,height) = boundedImage.size
    (data.fullWidth,data.fullHeight) = boundedImage.size
    data.lastPixel = 1
    data.progressBar = 0
    data.lastPixel = data.fullHeight*data.fullWidth
    #print data.lastPixel
    for iy in xrange(0,len(yDimensions),2):
        topHorizontal = yDimensions[iy]
        bottomHorizontal= yDimensions[iy+1]
        seperateLine = boundedImage.crop((0,topHorizontal,
                                          width,bottomHorizontal))
        #First horizontal cut for line
        xDimensions = lineVertically(seperateLine)
        if (iy != 0): # if not first line
            newSentence += "\n"
#        print "x:", xDimensions
        for ix in xrange(0,len(xDimensions),2):
#           4 bordering lines of letter
            leftVertical = xDimensions[ix]
            rightVertical = xDimensions[ix+1]
            if ix == 0:     #first letter of line
                oldRightVertical = leftVertical
            letterImage = boundedImage.crop((leftVertical,topHorizontal,
                                             rightVertical,bottomHorizontal))
            #Vertical cut for letter
            if abs(oldRightVertical - leftVertical) >= maxLetterSpace:
                newSentence += " "      #space
            oldRightVertical = xDimensions[ix+1] #right vertical of old letter
            #letterImage.show()
            letteryDimensions = lineHorizontally(letterImage)
            #print letteryDimensions
            letterTopHorizontal = letteryDimensions[0]
            letterBottomHorizontal = letteryDimensions[-1]
            letterImage = boundedImage.crop((leftVertical,
                                             topHorizontal+letterTopHorizontal,
                                            rightVertical,
                                             topHorizontal+letterBottomHorizontal))
            #Second horizontal cut for letter
            if data.guessFontCounter == 0:
                data.guessFont = guessFont(letterImage)
                #print data.guessFont
                data.guessFontCounter += 1
                letterImage.save("guessFontChecker.png")
                if "Sans" in data.guessFont:
                    data.level = 150
                    words = addLettersSans(image,data.guessFont)
                else:
                    words = addLetters(image,data.guessFont)
                return words

def addLettersGuess(image,font="timesNewRoman"):
    #guessing the font of the letter first then running the ocr
    if fontLoad(data.guessFont) == None:
        print "Try again"
        return
    image = image.convert("L")
    BitImage = convertImageTo2Bit(image)
    boundedImage = initialBoxItIn(BitImage)
    boundedImage.save("savedImage.png")
    yDimensions = lineHorizontally(boundedImage)
    newSentence = ""
    #print "y:", yDimensions
    maxLetterSpace = 3
    (width,height) = boundedImage.size
    (data.fullWidth2,data.fullHeight2) = boundedImage.size
    data.lastPixel2 = 1
    data.progressBar = 0
    data.lastPixel2 = data.fullHeight2*data.fullWidth2
    #print data.lastPixel
    for iy in xrange(0,len(yDimensions),2):
        topHorizontal = yDimensions[iy]
        bottomHorizontal= yDimensions[iy+1]
        seperateLine = boundedImage.crop((0,topHorizontal,
                                          width,bottomHorizontal))
        #First horizontal cut for line
        xDimensions = lineVertically(seperateLine)
        if (iy != 0): # if not first line
            newSentence += "\n"
#        print "x:", xDimensions
        for ix in xrange(0,len(xDimensions),2):
#           4 bordering lines of letter
            leftVertical = xDimensions[ix]
            rightVertical = xDimensions[ix+1]
            if ix == 0:     #first letter of line
                oldRightVertical = leftVertical
            letterImage = boundedImage.crop((leftVertical,topHorizontal,
                                             rightVertical,bottomHorizontal))
            #Vertical cut for letter
            if abs(oldRightVertical - leftVertical) >= maxLetterSpace:
                newSentence += " "      #space
            oldRightVertical = xDimensions[ix+1] #right vertical of old letter
            #letterImage.show()
            letteryDimensions = lineHorizontally(letterImage)
            #print letteryDimensions
            letterTopHorizontal = letteryDimensions[0]
            letterBottomHorizontal = letteryDimensions[-1]
            letterImage = boundedImage.crop((leftVertical,
                                             topHorizontal+letterTopHorizontal,
                                            rightVertical,
                                             topHorizontal+letterBottomHorizontal))
            #Second horizontal cut for letter
            if data.guessFontCounter == 0:
                data.guessFont = guessFont(letterImage)
                #print data.guessFont
                data.guessFontCounter += 1
                letterImage.save("guessFontChecker.png")
                if "Sans" in data.guessFont:
                    data.level = 150
                    words = addLettersSans(image,data.guessFont)
                else:
                    words = addLetters(image,data.guessFont)
                return words

def addLetters(image,font="timesNewRoman"):
    if fontLoad(font) == None:
        print "Try again"
        return
    image = image.convert("L")
    BitImage = convertImageTo2Bit(image)
    boundedImage = initialBoxItIn(BitImage)
    boundedImage.save("savedImage.png")
    yDimensions = lineHorizontally(boundedImage)
    newSentence = ""
    #print "y:", yDimensions
    maxLetterSpace = 3
    (width,height) = boundedImage.size
    (data.fullWidth2,data.fullHeight2) = boundedImage.size
    data.lastPixel2 = 1
    data.progressBar = 0
    data.lastPixel2 = data.fullHeight2*data.fullWidth2
    #print data.lastPixel
    for iy in xrange(0,len(yDimensions),2):
        topHorizontal = yDimensions[iy]
        bottomHorizontal= yDimensions[iy+1]
        seperateLine = boundedImage.crop((0,topHorizontal,
                                          width,bottomHorizontal))
        #First horizontal cut for line
        xDimensions = lineVertically(seperateLine)
        if (iy != 0): # if not first line
            newSentence += "\n"
#        print "x:", xDimensions
        for ix in xrange(0,len(xDimensions),2):
#           4 bordering lines of letter
            leftVertical = xDimensions[ix]
            rightVertical = xDimensions[ix+1]
            if ix == 0:     #first letter of line
                oldRightVertical = leftVertical
            letterImage = boundedImage.crop((leftVertical,topHorizontal,
                                             rightVertical,bottomHorizontal))
            #Vertical cut for letter
            if abs(oldRightVertical - leftVertical) >= maxLetterSpace:
                newSentence += " "      #space
            oldRightVertical = xDimensions[ix+1] #right vertical of old letter
            #letterImage.show()
            letteryDimensions = lineHorizontally(letterImage)
            #print letteryDimensions
            letterTopHorizontal = letteryDimensions[0]
            letterBottomHorizontal = letteryDimensions[-1]
            letterImage = boundedImage.crop((leftVertical,
                                             topHorizontal+letterTopHorizontal,
                                            rightVertical,
                                             topHorizontal+letterBottomHorizontal))
            #Second horizontal cut for letter
            data.progressBar = (rightVertical+
                    (topHorizontal+letterBottomHorizontal-1)*data.fullWidth2)
            #print data.progressBar2
            (width1,height1) = letterImage.size
            lastCutCol = -1
            changedLetterImage = False
            ratio = 1.0*width1/height1
            maxRatio = 1.23 #W is the letter
            if ratio > maxRatio:
                for col in xrange(width1/4,3*width1/4+1):
                    #splits letters that aren't near each other or that are stuck
                    #together by only one pixel in a column
                    if (col == 3*width1/4) and (changedLetterImage == True):
                        cutLetterImage = letterImage.crop((lastCutCol+1,0,
                                                           width1,height1))
                        currentLetter = compareImageToLetters(cutLetterImage,
                                                              font)
                        newSentence += str(currentLetter)
                        #cutLetterImage.show()
                    elif hasNoPixelsToRight(letterImage,col):
                        cutLetterImage = letterImage.crop((lastCutCol+1,0,
                                                           col,height1))
                        lastCutCol = col
                        #cutLetterImage.show()
                        currentLetter = compareImageToLetters(cutLetterImage,
                                                              font)
                        newSentence += str(currentLetter)
                        changedLetterImage = True
                    elif (hasOneBlackPixel(letterImage,col) and (3*width1/4 > 1)
                    and (not hasOneBlackPixel(letterImage,col+1))):
                        #if col with one black and next col with more black
                        #then you know there is more than one letter stuck
                        #print column
                        #letterImage.show()
                        cutLetterImage = letterImage.crop((lastCutCol+1,0,
                                                           col,height1))
                        lastCutCol = col
                        currentLetter = compareImageToLetters(cutLetterImage,
                                                              font)
                        #cutLetterImage.show()
                        newSentence += str(currentLetter)
                        changedLetterImage = True
                if changedLetterImage == False:     #if not altered
                        #letterImage.show()
                        currentLetter = compareImageToLetters(letterImage,
                                                              font)
                    #letterImage.show()
    #               letterImage.save("savedLetter.png")  
    #               print currentLetter
                        newSentence += str(currentLetter)
            else:
                currentLetter = compareImageToLetters(letterImage,data.guessFont)
                newSentence += str(currentLetter)
            newSentence = applySpecialCases(letterImage,newSentence)
            changedLetterImage = False #set it back to default value
    #print "new:",newSentence
    return newSentence

def addLettersSans(image,font="microsoftSansSerif"):
    #For images where the font is already guessed
    if fontLoad(font) == None:
        print "Try again!"
        return
    image = image.convert("L")
    BitImage = convertImageTo2Bit(image,150)
    boundedImage = initialBoxItIn(BitImage)
    boundedImage.save("savedImage2.png")
    #boundedImage.show()
    yDimensions = lineHorizontally(boundedImage)
    newSentence = ""
    #print "y:", yDimensions
    maxLetterSpace = 4
    (width,height) = boundedImage.size
    (data.fullWidth,data.fullHeight) = boundedImage.size
    data.lastPixel = 1
    data.progressBar = 0
    data.lastPixel = data.fullHeight*data.fullWidth
    #print data.lastPixel
    for iy in xrange(0,len(yDimensions),2):
        topHorizontal = yDimensions[iy]
        bottomHorizontal= yDimensions[iy+1]
        seperateLine = boundedImage.crop((0,topHorizontal,
                                          width,bottomHorizontal))
        #First horizontal cut for line
        xDimensions = lineVertically(seperateLine)
        if (iy != 0): # if not first line
            newSentence += "\n"
#        print "x:", xDimensions
        for ix in xrange(0,len(xDimensions),2):
#           4 bordering lines of letter
            leftVertical = xDimensions[ix]
            rightVertical = xDimensions[ix+1]
            if ix == 0:     #first letter of line
                oldRightVertical = leftVertical
            letterImage = boundedImage.crop((leftVertical,topHorizontal,
                                             rightVertical,bottomHorizontal))
            #Vertical cut for letter
            if abs(oldRightVertical - leftVertical) >= maxLetterSpace:
                newSentence += " "      #space
            oldRightVertical = xDimensions[ix+1] #right vertical of old letter
            #letterImage.show()
            letteryDimensions = lineHorizontally(letterImage)
            #print letteryDimensions
            letterTopHorizontal = letteryDimensions[0]
            letterBottomHorizontal = letteryDimensions[-1]
            letterImage = boundedImage.crop((leftVertical,
                                             topHorizontal+letterTopHorizontal,
                                            rightVertical,
                                             topHorizontal+letterBottomHorizontal))
            #Second horizontal cut for letter
            data.progressBar = (rightVertical+
                    (topHorizontal+letterBottomHorizontal-1)*data.fullWidth)
            #print "bar:",data.progressBar
            (width1,height1) = letterImage.size
            ratio = 1.0*width1/height1
            maxRatio = 1.23
            if ratio > maxRatio:
                #print ratio
                currentLetter = addLettersSans2(letterImage,font)
                #letterImage.show()
            #letterImage.show()
            else:
                currentLetter = compareImageToLetters(letterImage,
                                                font,data.level,data.allLetters)
                #letterImage.show()
#            letterImage.save("savedLetter.png")  
#               print currentLetter
            newSentence += str(currentLetter)
            #print newSentence
    return newSentence

def addLettersSans2(image,font="timesNewRoman"):
    #for sans fonts that exceed the ratio of one letter (rare case!)
    if fontLoad(font) == None:
        print "Try again"
        return
    image = image.convert("L")
    BitImage = convertImageTo2Bit(image)
    boundedImage = initialBoxItIn(BitImage)
    #boundedImage.save("savedImage.png")
    yDimensions = lineHorizontally(boundedImage)
    newSentence = ""
    #print "y:", yDimensions
    maxLetterSpace = 3
    (width,height) = boundedImage.size
    (data.fullWidth2,data.fullHeight2) = boundedImage.size
    data.lastPixel2 = 1
    data.progressBar2 = 0
    data.lastPixel2 = data.fullHeight2*data.fullWidth2
    #print data.lastPixel
    for iy in xrange(0,len(yDimensions),2):
        topHorizontal = yDimensions[iy]
        bottomHorizontal= yDimensions[iy+1]
        seperateLine = boundedImage.crop((0,topHorizontal,
                                          width,bottomHorizontal))
        #First horizontal cut for line
        xDimensions = lineVertically(seperateLine)
        if (iy != 0): # if not first line
            newSentence += "\n"
#        print "x:", xDimensions
        for ix in xrange(0,len(xDimensions),2):
#           4 bordering lines of letter
            leftVertical = xDimensions[ix]
            rightVertical = xDimensions[ix+1]
            if ix == 0:     #first letter of line
                oldRightVertical = leftVertical
            letterImage = boundedImage.crop((leftVertical,topHorizontal,
                                             rightVertical,bottomHorizontal))
            #Vertical cut for letter
            if abs(oldRightVertical - leftVertical) >= maxLetterSpace:
                newSentence += " "      #space
            oldRightVertical = xDimensions[ix+1] #right vertical of old letter
            #letterImage.show()
            letteryDimensions = lineHorizontally(letterImage)
            #print letteryDimensions
            letterTopHorizontal = letteryDimensions[0]
            letterBottomHorizontal = letteryDimensions[-1]
            letterImage = boundedImage.crop((leftVertical,
                                             topHorizontal+letterTopHorizontal,
                                            rightVertical,
                                             topHorizontal+letterBottomHorizontal))
            #Second horizontal cut for letter
            data.progressBar = (rightVertical+
                    (topHorizontal+letterBottomHorizontal-1)*data.fullWidth2)
            #print data.progressBar2
            (width1,height1) = letterImage.size
            lastCutCol = -1
            changedLetterImage = False
            ratio = 1.0*width1/height1
            maxRatio = 1.23 #W is the letter
            for col in xrange(width1/4,3*width1/4+1):
                #splits letters that aren't near each other or that are stuck
                #together by only one pixel in a column
                if (col == 3*width1/4) and (changedLetterImage == True):
                    cutLetterImage = letterImage.crop((lastCutCol+1,0,
                                                       width1,height1))
                    currentLetter = compareImageToLetters(cutLetterImage,
                                                          font)
                    newSentence += str(currentLetter)
                    #cutLetterImage.show()
                elif hasNoPixelsToRight(letterImage,col):
                    cutLetterImage = letterImage.crop((lastCutCol+1,0,
                                                       col,height1))
                    lastCutCol = col
                    #cutLetterImage.show()
                    currentLetter = compareImageToLetters(cutLetterImage,
                                                          font)
                    newSentence += str(currentLetter)
                    changedLetterImage = True
                elif (hasOneBlackPixel(letterImage,col) and (3*width1/4 > 1)
                and (not hasOneBlackPixel(letterImage,col+1))):
                    #if col with one black and next col with more black
                    #then you know there is more than one letter stuck
                    #print column
                    #letterImage.show()
                    cutLetterImage = letterImage.crop((lastCutCol+1,0,
                                                       col,height1))
                    lastCutCol = col
                    currentLetter = compareImageToLetters(cutLetterImage,
                                                          font)

                    newSentence += str(currentLetter)
                    changedLetterImage = True
            if changedLetterImage == False:     #if not altered
                    #letterImage.show()
                    currentLetter = compareImageToLetters(letterImage,
                                                          font)
                    newSentence += str(currentLetter)
            newSentence = applySpecialCases(letterImage,newSentence)
            changedLetterImage = False #set it back to default value
    #print "new:",newSentence
    return newSentence

def applySpecialCases(letterImage,newSentence):
    #special cases that affect algorithm
    (width,height) = letterImage.size
    ratio = 1.0*width/height
    if (ratio > 1.5) and (containsNoWhite(letterImage)):
        newSentence = newSentence[0:-1] + "."
    while "WI" in newSentence:
        index = newSentence.index("WI")
        newSentence = newSentence[:index+1] + newSentence[index+2:]
    return newSentence

def hasOneBlackPixel(letterImage,col):
    pixelList = letterImage.getdata()
    (width,height) = letterImage.size
    count = 0
    try:
        for index in xrange(height):
            pixel = pixelList[index*width+col]
            if (pixel == 0):
                count += 1
                if (count > 1):
                    return False
        if (count == 1):
            return True
        else:
            return False
    except:
        return False
    

def getCol(letterImage,col):    #returns column of image
    pixelList = letterImage.getdata()
    (width,height) = letterImage.size
    #print len(pixelList)
    pixelCol = []
    for index in xrange(0,height):
        pixel = pixelList[index*width+col]
        #print pixel
        pixelCol.append(pixel)
    return pixelCol

def hasNoPixelsToRight(letterImage,col):
    #checks if column has right neighboring black cells
    pixelList = letterImage.getdata()
    (width,height) = letterImage.size
    #print len(pixelList)
    pixelCol = []
    result = False
    for index in xrange(0,height-1):
        pixel = pixelList[index*width+col]
        if (pixel == 0):    #pixel is black
            result = True
            rightPixel = pixelList[index*width+col+1]
            rightUpPixel = pixelList[(index-1)*width+col+1]
            rightDownPixel = pixelList[(index+1)*width+col+1]
            pixels = [rightPixel,rightUpPixel,rightDownPixel]
            if 0 in pixels:
                #if any black
                return False
    return result
    

def wordCount(image): #Counts number of words in image
    allWords = runOcr(image,data.guessFont).split()
    return len(allWords)
    
def upper(image):   #Converts image to upper-case letters
    currentSentence = runOcr(image,data.guessFont)
    upperSentence = currentSentence.upper()
    return upperSentence

def lower(image):   #Converts image to lower-case letters
    currentSentence = runOcr(image,data.guessFont)
    lowerSentence = currentSentence.lower()
    return lowerSentence

def capitalize(image):  #Capitalizes first letter of sentence
    currentSentence = runOcr(image,data.guessFont)
    capSentence = currentSentence.capitalize()
    return capSentence

def capitalizeEveryWord(image):     #Capitlizes every word in image
    currentWord = runOcr(image,data.guessFont)
    capSentence = ""
    for word in currentWord.split():
        capWord = word.capitalize()
        capSentence += capWord
        if (word != currentWord.split()[len(currentWord.split())-1]):
            capSentence += " "
    return capSentence
    

def initialBoxItIn(image):     #bounds the image
    image = image.convert("L")      #converts to 255 bits
    dimensions = image.getbbox()
    bwImage = convertImageTo2Bit(image)     #turns into black and white image
    boundedImage = bwImage.crop(dimensions)
    (width,height) = boundedImage.size
    yDimensions = lineHorizontally(boundedImage)
    boundedImage = boundedImage.crop((0,yDimensions[0],width,yDimensions[-1]))
    (width,height) = boundedImage.size
    xDimensions = lineVertically(boundedImage)
    boundedImage = boundedImage.crop((xDimensions[0],0,xDimensions[-1],height))
    return boundedImage

def lineHorizontally(boundedImage):
    #seperates image into horizontal lines (for seperate lines)
    (width,height) = boundedImage.size
    yDimensions = []  #for horizontal lines
    lineFirst = 0
    i = 0
    while i < len(boundedImage.getdata()): 
        x = i%width
        y = i/width
        pixel = boundedImage.getdata()[i]
        if (rowNotHasColor(boundedImage,0,width,i) == False) and (lineFirst == 0):
            lineFirst += 1  #Found first black pixel in line
            yDimensions.append(y) #upper horizontal line
        elif (lineFirst == 1) and rowNotHasColor(boundedImage,0,width,i):
            yDimensions.append(y)     #lower horizontal line
            lineFirst = 0
        i = i + width   #go to end of row
    if len(yDimensions)%2 == 1:         #last vertical line
        yDimensions.append(height)
    return yDimensions

def lineVertically(boundedImage):
    #seperates image into vertical lines(for individual letters)
    xDimensions = []    #vertical lines
    (width,height) = boundedImage.size
    lineFirst = 0
    i = 0
    while i < width:
        #i  = x
        if (colNotHasColor(boundedImage,0,width,height,i) == False) and (lineFirst == 0):
            lineFirst += 1  #Found first black pixel in line
            xDimensions.append(i) #upper vertical line
        elif (lineFirst == 1) and colNotHasColor(boundedImage,0,width,height,i):
            xDimensions.append(i)     #lower vertical line
            lineFirst = 0
        i = i + 1   #go to end of row
    if len(xDimensions)%2 == 1:     #last horizontal line
        xDimensions.append(width)
    return xDimensions

def rowNotHasColor(boundedImage,color,width,i):
    #checks if row doesn't have color
    widthUntilEnd = width - (i%width)
    for index in xrange(widthUntilEnd):
        pixel = i + index
        if boundedImage.getdata()[pixel] == color:
            return False
    return True
        
def colNotHasColor(boundedImage,color,width,height,i):
    #checks if column doesn't have color
    heightUntilEnd = height 
    for index in xrange(heightUntilEnd):
        pixel = i + index*width
        if boundedImage.getdata()[pixel] == color:
            return False
    return True
            
           

