# -*- coding: utf-8 -*-

from Base.Core import FchatPrv
from Gui.MainWindow import Application
import sys

app = Application()
app.fchat_prv = FchatPrv()

app.run(sys.argv)
