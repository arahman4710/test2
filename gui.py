# -*- coding: cp1252 -*-
from Tkinter import *
from PIL import Image
import ImageChops
import math
import numpy
import copy
import string
import ImageTk
from tkFileDialog import askopenfilename

import ocrByAnik as ocr

global root
ocr.data.bg = "#A3A3A3"
root = Tk()
root.resizable(width=FALSE,height=FALSE)
root.configure(background=ocr.data.bg)
root.configure(width=2)
root.title("Optical Character Recognition by Anik")
global root2
root2 = Tk()
root2.resizable(width=FALSE,height=FALSE)
root2.title("Instructions for OCR")


#image = Image.open("testPicture4.png")
#image2 = Image.open("firstLine.png")
#image3 = Image.open("testPicture8.png")
#image4 = Image.open("testPicture7.png")
#image5 = Image.open("MicrosoftSansSerifCapitalSet.png")

##Button click functions
def doItButtonPressed():
    try:
        ocr.data.progressBar=0
        timerFired()
        outputTextBox.config(state=NORMAL)
        outputTextBox.delete(1.0,END)
        function = functionsTextBox.get(1.0,END) #What is in the function box
        function = "ocr." + function
        Image = getImage(ocr.data.filename)
        outputTextBox.insert(END,eval(function))
        canvasHeight = 325
        canvasWidth = 378
        (width,height) = Image.size
        if (width > canvasWidth):
            Image = Image.resize((canvasWidth,height))
        elif (height > canvasHeight):
            Image = Image.resize((width,canvasHeight))
        photImage = ImageTk.PhotoImage(Image)
        canvas.create_image(0,30,image=photImage,anchor=NW)
        canvas.image = photImage
        ocr.data.guessFontInput = ocr.data.guessFont
        ocr.data.progressBar = ocr.data.lastPixel
    #im1 = PhotoImage(file=ocr.data.filename)
    #ocr.runOcr(image,"microsoftSansSerif"))
    except:
        outputTextBox.insert(END,"""The function could not be executed on \nthe image.
        \nPlease make sure that the file is an \nimage and that the function is valid.""")
    finally:
        #functionsTextBox.delete(1.0,END)
        #functionsTextBox.insert(END,
        outputTextBox.config(state=DISABLED)

def browseButtonPressed():
    filename = askopenfilename(filetypes=[("allfiles","*"),
                                          ("pythonfiles","*.py")])
    ocr.data.filename = filename
    fileBox.config(state=NORMAL)
    fileBox.delete(1.0,END)
    fileBox.insert(END,ocr.data.filename)
    fileBox.config(state=DISABLED)
    #outputTextBox.insert(END,eval(function))
    canvasHeight = 325
    canvasWidth = 378
    try:
        Image = getImage(ocr.data.filename)
        (width,height) = Image.size
        if (width > canvasWidth):
            Image = Image.resize((canvasWidth,height))
        elif (height > canvasHeight-30):
            Image = Image.resize((width,canvasHeight))
        photImage = ImageTk.PhotoImage(Image)
        canvas.create_image(0,30,image=photImage,anchor=NW)
        canvas.image = photImage
        textInOutputTextBox = outputTextBox.get(1.0,END)
        if "Image could not be recognized" in textInOutputTextBox:
            outputTextBox.config(state=NORMAL)
            outputTextBox.delete(1.0,END)
            outputTextBox.config(state=DISABLED)
    except:
        outputTextBox.config(state=NORMAL)
        outputTextBox.delete(1.0,END)
        #canvas.delete(all)
        if fileBox.get(1.0,END) == "\n":        #nothing in fileBox
            outputTextBox.config(state=NORMAL)
            outputTextBox.delete(1.0,END)
            outputTextBox.config(state=DISABLED)
        else:
            outputTextBox.insert(END,"""Image could not be recognized.
            \nPlease make sure that the file is an \nimage.""")
        outputTextBox.config(state=DISABLED)


def getImage(path):
    #path = path[path.rfind("/")+1:]
    image = Image.open(path)
    return image

def callback():
    #if tkMessageBox.askokcancel("Quit", "Do you really wish to quit?"):
    functionsTextBox.config(state=NORMAL)
    functionsTextBox.delete(1.0,END)
    functionsTextBox.insert(END,ocr.data.functionChoice.get())
    functionsBox.destroy()


def functionsButtonPressed():
    # new window with functions
    global functionsBox
    functionsBox = Toplevel(root)
    functionsBox.title("List of Functions")
    MODES = [
    ("run OCR (font not known)", "runOcr(Image)"),
    ("run OCR with Microsoft Sans Serif", "runOcr(Image,'microsoftSansSerif')"),
    ("run OCR with Times New Roman", "runOcr(Image,'timesNewRoman')"),
    ("Count words", "wordCount(Image)"),
    ("Make Uppercase", "upper(Image)"),
    ("Make Lowercase", "lower(Image)"),
    ("Capitalize only first letter", "capitalize(Image)"),
    ("Capitalize every word", "capitalizeEveryWord(Image)"),
    ]
    ocr.data.functionChoice = StringVar()
    ocr.data.functionChoice.set("runOcr(Image)") # initialize
    for text, mode in MODES:
        button = Radiobutton(functionsBox, text=text,
                        variable=ocr.data.functionChoice, value=mode)
        button.pack(anchor=W)
    functionsBox.protocol("WM_DELETE_WINDOW", callback)
    #destroys all boxes at once
    mainloop()

##    s1Var = StringVar(root)
##    s2Var = StringVar(root)
##    s1Var.set("s1")
##    s2Var.set("s2")
##    square1Label = Label(board,textvariable=s1Var)
##    square1Label.grid(row=0, column=7)
##    square2Label = Label(board,textvariable=s2Var)
##    square2Label.grid(row=0, column=6)

#canvas = Canvas(root,width=300,height=300)
#canvas.create_rectangle(0,0,300,300,fill="green")
#canvas.grid(row=0,column=0,sticky=NW)


#title at top
title = Label(root,font = "Helvetica 24 bold underline",bg=ocr.data.bg,
              text = "Optical Character Recognition")
title.grid(row=0,column=0,columnspan=3,sticky=N)

#Canvas for image
canvas = Canvas(root,height=325)
canvas.config(bg = "#FF7A00",highlightthickness=0)
canvas.grid(row=1,column=2,columnspan=2,sticky=NW)
canvas.create_text(200,0,text = "Current Image:",anchor=N,
                   font="Ariel 15 underline")

#Instructions canvas
instructions = Canvas(root2,width=400,height=600)
instructions.config(highlightthickness=0)
#instructions.create_rectangle(0,0,100,100,fill="blue")
instructions.create_text(100,0,anchor=N,font = "Ariel 12 underline",
                         text = "Instructions")
instructions.create_text(0,25,anchor = NW, font = 'Ariel 8',text = """
 To understand how this program works, follow these instructions:

\t The program contains two buttons The buttons included a "Do it"
 button and a "Browse" button. The "Do it" button runs whatever
 function is listed and the "Browse" button allows the user to pick any
 file. The function text area is one where you can type because it
 allows the users to type in whatever functions he/she wishes to
 execute. However, the other two text areas, the output text area and
 the file text area are both read-only. The file text area only
 displays the file that the function will be run on and will only
 change when the browse button is used to select a new file. The output
 text area displays the output of the function on the file that is
 listed in the function text area box. If undesired output is given,
 the output text area box prints an error message that tells the user
 to try again. Under the text "List of Functions", there is a button
 that allows the user to choose any function that the program provides.
 After pressing the button, a pop-up box appears that shows the user
 what kinds of functions exist. The listed functions in the pop-up box
 are explained clearly so the user does not have to read through the
 syntax of the program. Lastly, there is a canvas with instruction
 (this one) that clearly explains how to use the program.

\tTo use the functions, the user must first "Run Ocr" on it. Once this
 has been done, other functions like "Word Count" and "Capitalize
 letters" can be used.

\tOnce an image has been uploaded, the image appears on the orange
 canvas. The images also fit on the orange canvas. If the image is
 smaller than the canvas, it will remain that way. However, if the
 image is bigger than the orange canvas, the image will be squeezed
 into the orange canvas.

\t The user can also choose to input the font if he wishes. If not,
 the program goes through the list of fonts and picks the best matching
 font based on the first boxed-in image and then redoes the OCR program
 with the guessed font. However, if the user does know the font and
 decides to put it in, the program will run faster, as it does need to
 go to the first boxed-in letter and figure out the font.""")

instructions.pack()

#Output box
outputTextBox=Text(root,height=20,width=40,background="#03899C",
                   borderwidth=5) 
outputTextBox.insert(INSERT, "")
outputTextBox.config(state=DISABLED)
outputTextBox.grid(row=1,column=0,sticky=NW)

#Progress bar
progressWord = Label(root,font = "Ariel 12 underline",
                     text = "Progress:", bg = ocr.data.bg)
progressWord.grid(row=2,column=0,sticky=E)
progressCanvas = Canvas(root,height=17)
progressCanvas.config(bg=ocr.data.bg,highlightthickness=0)
progressCanvas.grid(row=2,column=2,sticky=W)
progressCanvas.create_rectangle(0,0,375,16,width=5)

#Guesses Font
ocr.data.guessFontInput = "None"
guessFont = Label(root,font = "Ariel 12 underline",
                     text = "Guessed Font: "+str(ocr.data.guessFontInput), bg = ocr.data.bg)
guessFont.grid(row=2,column=0,sticky=W)

#function box
functionsTextBox = Text(root,height=3,width=55,bg="white",
                        borderwidth=5)
ocr.data.function = 'runOcr(Image)'
functionsTextBox.insert(INSERT,ocr.data.function)
functionsTextBox.grid(row=4,column=0,columnspan=3,sticky=W)

#Exectutes function button
runFunctionButtonImage = ImageTk.PhotoImage(file="ocrButton.png")
runFunctionButton = Button(root,image=runFunctionButtonImage,width=50,height=50,bg=ocr.data.bg,
                    text = "do it", command=doItButtonPressed)
runFunctionButton.image = runFunctionButtonImage
runFunctionButton.grid(row=4,column = 3,sticky=NE)

#Function title #1
functionTitle = Label(root,font = "Ariel 12 underline",
                      text = "Type your function here:",
                      bg=ocr.data.bg)
functionTitle.grid(row=3,column=0,sticky=W)

#Function title #2
functionTitle2 = Label(root,font = "Ariel 12 underline",
                      text = "List of Functions:",
                      bg=ocr.data.bg)
functionTitle2.grid(row=3,column=2,sticky=E)

#box that contains file
fileBox = Text(root,height=2,width=55,background="white",bd=5)
fileBox.insert(INSERT,"Insert File Here!")
fileBox.grid(row=5,column=0,columnspan=3,sticky=W)
fileBox.config(state=DISABLED)

#browse box
browseButtonImage = ImageTk.PhotoImage(file="browseButton.png")
browseBox = Button(root, text="Browse",image = browseButtonImage,
                   bg = ocr.data.bg,command=browseButtonPressed)
browseBox.image = browseButtonImage
browseBox.config(bd=1)
browseBox.grid(row=5,column=2,sticky=W,padx=125)

#listOfFunctionsButtonImage = ImageTk.PhotoImage(file="browseButton.png")
listOfFunctionsButton = Button(root, text="Choose function Here!",#image = browseButtonImage,
                   bg = ocr.data.bg,command = functionsButtonPressed)
#browseBox.image = browseButtonImage
listOfFunctionsButton.config(bd=1)
listOfFunctionsButton.grid(row=4,column=2,sticky=NE,padx=5)


def timerFired():
    redrawAll()
    scoreNow = ocr.data.progressBar
    guessFont.config(text = "Guessed Font: "+str(ocr.data.guessFontInput))
    delay = 25 # milliseconds
    scoreLater = ocr.data.progressBar
    if (scoreNow == scoreLater) and (scoreNow > 500):
        ocr.data.progressBar = ocr.data.lastPixel
    progressCanvas.after(delay, timerFired) # pause, then call timerFired again

def redrawAll():
    progressCanvas.delete(ALL)
    lastPixel = ocr.data.lastPixel
    progressBarScore = ocr.data.progressBar
    percent = 1.0*progressBarScore/lastPixel
    #print "perc",progressBarScore
    progressCanvas.create_rectangle(0,0,375,16,width=5)
    progressCanvas.create_rectangle(2,2,percent*373,14,fill="blue")

#def run():
#    # set up events
#    timerFired()
    # and launch the app

    
root.mainloop()  # This call BLOCKS (so your program waits until you close the window!)


