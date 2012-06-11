
from PIL import Image
import ImageChops
import math
import numpy
import time
import copy
import string



def convertImageTo2Bit(image,level = 150):
    image = image.convert("L")      #converts to 255 bits
    (width,height) = image.size
    bwImage = Image.new("L",(width,height))   #new image in black and white
    allWhitePixel = 255 
    middleNumberPixel = level
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


def initialBoxItIn(image):     #bounds the image
    image = image.convert("L")      #converts to 255 bits
    dimensions = image.getbbox()
    bwImage = convertImageTo2Bit(image)     #turns into black and white image
    boundedImage = bwImage.crop(dimensions)
    (width,height) = boundedImage.size
    yDimensions = lineHorizontally(boundedImage)
    boundedImage = boundedImage.crop((0,0,width,yDimensions[-1]))
    (width,height) = boundedImage.size
    xDimensions = lineVertically(boundedImage)
    boundedImage = boundedImage.crop((0,0,xDimensions[-1],height))
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
    #checks if col doesn't have color
    heightUntilEnd = height 
    for index in xrange(heightUntilEnd):
        pixel = i + index*width
        if boundedImage.getdata()[pixel] == color:
            return False
    return True

def twoTupleConvert(lst):
    #Converts list into a tuple.
    #Used in the font maker to convert the two bordering vertical lines of
    #a letter to be stored in a tuple
    rightLeftTupleBox = []
    for i in xrange(0,len(lst),2):
        rightLeftTupleBox.append((lst[i],lst[i+1]))
    return rightLeftTupleBox
            
def saveChars(key, img, tag):
    #saves images containing letters of a certain font
    img = convertImageTo2Bit(img)
    data = twoTupleConvert(lineVertically(img))

    _ , lower = img.size

    for i in xrange(len(key)):
        start, stop = data[i]
        charImg = img.crop((start,0,stop,lower))
        charUp, charLow = lineHorizontally(charImg)[0],lineHorizontally(charImg)[1]
        charW, charH = charImg.size
        charImg = charImg.crop((0,charUp,charW,charLow))
        charImg.save(tag + str(key[i]) + ".png", "png")



key = "ABCDEFGHIJKLMNOPQRSTUVWXYZ."
keyLower = "abcdefghijklmnopqrstuvwxyz1234567890"

imgUpper = Image.open("MicrosoftSansSerifCapitalSet.png")
imgLow = Image.open("MicrosoftSansSerifLowerSet.png")

saveChars(keyLower,imgLow, "microsoftSansSerif-lower-")
saveChars(key,imgUpper, "microsoftSansSerif-upper-")
