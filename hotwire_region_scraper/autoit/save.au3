AutoItSetOption("WinTitleMatchMode", 2)
WinActivate("Wireshark")
MouseClick("left", 10, 30)
MouseClick("left", 10, 220)
MouseClick("left", 250, 220)
MouseClick("left", 250, 390)
Send("C:\programs\hotwire\output\parse.txt")
ControlClick("Wireshark", "", "[ID:1054]", "left")
ControlClick("Wireshark", "", "[ID:1051]", "left")
ControlClick("Wireshark", "", "[ID:1052]", "left")
MouseClick("left", 500, 400)