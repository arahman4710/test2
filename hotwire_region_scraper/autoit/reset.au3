AutoItSetOption("WinTitleMatchMode", 2)
WinActivate("Wireshark")

Send("^r")

MouseClick("left", 540, 90)
MouseClick("left", 200, 100)
Send("http contains javascript")
MouseClick("left", 578, 90)