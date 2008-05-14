# -*- coding: utf-8 -*-
'''Launcher grafico per TressetteNetwork4.'''
# * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *
#
#    TressetteNetwork4 - copyright (C) daniele_athome
#
#    TressetteNetwork4 is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    TressetteNetwork4 is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with TressetteNetwork4; if not, write to the Free Software
#    Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
#
# * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *

import sys,os,subprocess,time
from threading import Thread
import wx

import main		# ts4 starter

PACKAGE=main.PACKAGE+" Launcher"
VERSION="0.0.1"

EVT_RETURN_ID = wx.NewId()

def EVT_RETURN(win, func):
	win.Connect(-1, -1, EVT_RETURN_ID, func)

class ReturnEvent(wx.PyEvent):
	def __init__(self, data):
		wx.PyEvent.__init__(self)
		self.SetEventType(EVT_RETURN_ID)
		self.data = data

class ReturnDialog(wx.Dialog):
	def __init__(self, parent, text, title, output):
		wx.Dialog.__init__(self, parent, wx.ID_ANY, title)

		panel = wx.Panel(self, wx.ID_ANY)

		message = wx.BoxSizer(wx.HORIZONTAL)

		# icona stock
		image = wx.ArtProvider.GetBitmap(wx.ART_ERROR, wx.ART_MESSAGE_BOX, wx.DefaultSize)
		message.Add(wx.StaticBitmap(panel,wx.ID_ANY,image),0,wx.ALIGN_LEFT|wx.LEFT,10)

		# message label
		text = wx.StaticText(panel,wx.ID_ANY,text)
		text.Bind(wx.EVT_SIZE, self.cb_wrap)
		message.Add(text,1,wx.EXPAND|wx.ALL,10)

		detail = wx.BoxSizer(wx.HORIZONTAL)
		#detail = wx.CollapsiblePane(panel, wx.ID_ANY, "Dettagli", style=wx.CP_DEFAULT_STYLE)
		#detail.SetMinSize((-1,-1))
		#self.Bind(wx.EVT_COLLAPSIBLEPANE_CHANGED, self.OnPaneChanged, detail)

		# pannello con sizer del collapsible
		#detail_panel = detail.GetPane()
		#detail_sizer = wx.BoxSizer(wx.VERTICAL)

		output = wx.TextCtrl(panel, wx.ID_ANY, output, style=wx.TE_MULTILINE)
		output.SetEditable(False)
		detail.Add(output,1,wx.EXPAND)

		self.sizer2 = wx.StdDialogButtonSizer()

		button_ok = wx.Button(panel, wx.ID_OK)
		button_ok.SetDefault()
		button_ok.Bind(wx.EVT_BUTTON,self.OnButton)

		self.sizer2.AddButton(button_ok)
		self.sizer2.SetAffirmativeButton(button_ok)
		self.sizer2.Realize()

		self.sizer=wx.BoxSizer(wx.VERTICAL)

		# aggiungi i frame
		self.sizer.Add(message,0,wx.EXPAND|wx.ALL,10)
		self.sizer.Add(wx.StaticText(panel,wx.ID_ANY,"Dettagli:"),0,wx.LEFT,10)
		self.sizer.AddSpacer(5)
		self.sizer.Add(detail,0,wx.EXPAND|wx.LEFT|wx.RIGHT,10)
		self.sizer.Add(wx.StaticLine(panel,wx.ID_ANY),0,wx.EXPAND|wx.ALL,10)

		# aggiungi i pulsanti
		self.sizer.Add(self.sizer2,1,wx.ALIGN_BOTTOM|wx.BOTTOM,10)

		panel.SetSizer(self.sizer)
		panel.SetAutoLayout(True)
		self.sizer.SetSizeHints(output)
		self.sizer.Fit(self)

	def OnButton(self,event=None):
		self.Close()

	def cb_wrap(self,event=None):
		event.GetEventObject().Wrap(event.GetSize()[0])

class LauncherWindow(wx.Dialog):
	def __init__(self, parent, ID, title, position = wx.DefaultPosition, size = wx.DefaultSize):
		wx.Dialog.__init__(self, parent, wx.ID_ANY, title, position, size)
		self.Bind(wx.EVT_CLOSE, self.cb_close)
		EVT_RETURN(self,self.return_event)

		self.exiting = False
		panel = wx.Panel(self, wx.ID_ANY)

		# info server
		self.server_frame = wx.StaticBoxSizer(wx.StaticBox(panel, wx.ID_ANY, 'Server'),wx.VERTICAL)

		# size verticale per contenere le linee di input widget

		# linea 1: label "port", spin (number)
		line1 = wx.BoxSizer(wx.HORIZONTAL)

		# label "port"
		self.bind_label = wx.StaticText(panel,wx.ID_ANY,"Porta del server:")
		line1.Add(self.bind_label,0,wx.EXPAND|wx.TOP,5)

		# spin "port"
		self.bind_port = wx.SpinCtrl(panel, wx.ID_ANY, min=1, max=65536, size=(100,-1), initial=main.PORT)
		line1.Add(self.bind_port,0,wx.ALIGN_TOP|wx.LEFT,10)

		self.server_frame.Add(line1,0,wx.ALL-wx.BOTTOM,10)

		# linea 2: checkbox "standalone"
		self.standalone = wx.CheckBox(panel, wx.ID_ANY, "Avvia solo server")
		wx.EVT_CHECKBOX(panel,self.standalone.GetId(), self.cb_standalone)

		self.server_frame.Add(self.standalone,0,wx.ALIGN_TOP|wx.ALL,10)

		# linea 3: multiline text "server stdout"
		self.stdout = wx.TextCtrl(panel, wx.ID_ANY, style=wx.TE_MULTILINE)
		self.stdout.SetEditable(False)

		self.server_frame.Add(self.stdout,1,wx.EXPAND|wx.ALL-wx.TOP,5)

		# info client
		self.client_frame = wx.StaticBoxSizer(wx.StaticBox(panel, wx.ID_ANY, 'Client'),wx.VERTICAL)
		self.client_labels = []

		# linea 1: label "server", entry "host:port"
		line1 = wx.BoxSizer(wx.HORIZONTAL)

		# label "server"
		self.client_labels.append(wx.StaticText(panel,wx.ID_ANY,"Connetti a:"))
		line1.Add(self.client_labels[-1],0,wx.EXPAND|wx.TOP,5)

		# entry "host:port"
		self.address = wx.TextCtrl(panel, wx.ID_ANY)
		wx.EVT_TEXT(self.address, self.address.GetId(), self.cb_connect_text)
		line1.Add(self.address,1,wx.ALIGN_TOP|wx.LEFT,10)

		self.client_frame.Add(line1,0,wx.EXPAND|wx.ALL-wx.BOTTOM,10)

		# linea 2: label "name", entry "name"
		line2 = wx.BoxSizer(wx.HORIZONTAL)

		# label "name"
		self.client_labels.append(wx.StaticText(panel,wx.ID_ANY,"Nome:"))
		line2.Add(self.client_labels[-1],0,wx.EXPAND|wx.TOP,5)

		# entry "name"
		self.name = wx.TextCtrl(panel, wx.ID_ANY)
		line2.Add(self.name,1,wx.ALIGN_TOP|wx.LEFT,10)

		self.client_frame.Add(line2,0,wx.EXPAND|wx.ALL-wx.BOTTOM,10)

		# linea 3: label "server notes"
		text_notes = wx.StaticText(panel,wx.ID_ANY,u"Lasciando vuoto il campo \"Connetti a\", verrà avviato un nuovo server in locale ed il client si connetterà a questo.")
		text_notes.Bind(wx.EVT_SIZE, self.cb_wrap)
		self.client_labels.append(text_notes)
		self.client_frame.Add(self.client_labels[-1],0,wx.EXPAND|wx.ALL,10)

		# pulsanti
		self.sizer2 = wx.BoxSizer(wx.HORIZONTAL)
		self.button_start = wx.Button(panel, wx.ID_ANY, "Avvia")
		self.button_start.SetDefault()
		self.button_version = wx.Button(panel, wx.ID_ANY, "Versione")
		wx.EVT_BUTTON(self.button_start,self.button_start.GetId(), self.cb_start)
		wx.EVT_BUTTON(self.button_version,self.button_version.GetId(), self.cb_version)
		self.sizer2.Add(self.button_start,1,wx.EXPAND|wx.ALL,10)
		self.sizer2.Add(self.button_version,1,wx.EXPAND|wx.ALL,10)

		self.sizer=wx.BoxSizer(wx.VERTICAL)

		# aggiungi i frame
		self.sizer.Add(self.server_frame,1,wx.EXPAND|wx.ALL-wx.BOTTOM,10)
		self.sizer.Add(self.client_frame,1,wx.EXPAND|wx.ALL,10)

		# aggiungi i pulsanti
		self.sizer.Add(self.sizer2,0,wx.EXPAND)

		panel.SetSizer(self.sizer)
		panel.SetAutoLayout(True)

		# focus su address
		self.address.SetFocus()

	def cb_wrap(self,event=None):
		event.GetEventObject().Wrap(event.GetSize()[0])

	def cb_close(self,event=None):
		# stoppa il server se necessario
		if self.button_start.GetLabel() == "Stop":
			self.cb_start(None)

		self.exiting = True
		if not hasattr(self,'thread'):
			self.Destroy()
			self.app.ExitMainLoop()

	def cb_standalone(self, event=None):
		for c in self.client_labels:
			c.Enable(not self.standalone.GetValue())
		self.address.Enable(not self.standalone.GetValue())
		self.name.Enable(not self.standalone.GetValue())
		self.cb_connect_text()

	def cb_connect_text(self, event=None):
		self.bind_port.Enable(len(self.address.GetValue().strip()) == 0 or self.standalone.GetValue())
		self.bind_label.Enable(self.bind_port.IsEnabled())

	def cb_start(self, event=None):
		if self.button_start.GetLabel() == "Stop":
			self.button_start.SetLabel("Termino il server...")
			self.button_start.Enable(False)
			self.thread.kill()

		else:
			argv = []
			if self.standalone.GetValue():
				# avvia solo server -- niente altro
				argv.extend( ('standalone', 'bind='+str(self.bind_port.GetValue())) )
				self.button_start.SetLabel("Stop")
				self.standalone.Enable(False)
				self.bind_port.Enable(False)

			else:
				addr = self.address.GetValue().strip()
				if len(addr) > 0:
					argv.append('server='+addr)

				name = self.name.GetValue().strip()
				if len(name) > 0:
					argv.append('name='+name)

				self.Show(False)

			self.output = []
			self.thread = LauncherThread(argv,self.cb_child,self.cb_child)
			self.thread.start()

	def cb_child(self, retcode):
		wx.PostEvent(self, ReturnEvent(retcode))

	def return_event(self, event):
		retcode = event.data

		if isinstance(retcode,int):

			del self.thread
			if retcode != main.EXIT_SUCCESS:

				text = main.PACKAGE+" terminato per motivi sconosciuti."
				if retcode < main.EXIT_SUCCESS:
					# segnale di uscita
					text = main.PACKAGE+" terminato a causa del segnale "+str(-retcode)+"."

				elif retcode == main.EXIT_CONN_CLOSED:
					text = u"La connessione al server di gioco è stata chiusa."

				elif retcode == main.EXIT_CONN_REFUSED:
					text = u"La connessione al server di gioco è stata rifiutata."

				elif retcode == main.EXIT_CONN_ERROR:
					text = "Errore di connessione al server di gioco."

				elif retcode == main.EXIT_SYS_ERROR:
					text = main.PACKAGE+" terminato per un errore di sistema o un errore non gestito.\n\nMaggiori informazioni nei dettagli."

				elif retcode == main.EXIT_ARGV:
					text = "Argomenti di avvio non validi."

				text2 = ''
				for line in self.output:
					text2 = text2 + line

				d = ReturnDialog(self, text,main.PACKAGE + " terminato",text2)
				d.ShowModal()
				d.Destroy()

			if self.IsShown():
				self.button_start.SetLabel("Avvia")
				self.button_start.Enable(True)
				self.standalone.Enable(True)
				self.bind_port.Enable(True)

			else:
				self.Close()

			if self.exiting:
				self.Destroy()
				self.app.ExitMainLoop()

		else:
			# solo una linea di misero output...
			self.output.append(retcode)

			# standalone?
			if self.standalone.GetValue():
				self.stdout.AppendText(retcode)

	def cb_version(self, event=None):
		d = wx.MessageDialog(self, "Launcher versione "+VERSION+"\n\n"+main.PACKAGE+" versione "+main.VERSION, "Versione", wx.OK)
		d.ShowModal()
		d.Destroy()

class LauncherThread(Thread):
	def __init__(self,argv,callback,output_callback):
		Thread.__init__(self)

		self.argv = argv
		self.callback = callback
		self.output_callback = output_callback
		self.killed = False

	def run(self):

		executable = "python"
		if os.name == 'nt':
			executable = "pythonw"
		args = [executable, main.__file__]
		args.extend(self.argv)

		# inizia processo spawnato
		print "Arguments:",args

		try:
			self.process = subprocess.Popen(args,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
			# TODO ---------------------------------- porting to Windows
			import fcntl
			fcntl.fcntl(self.process.stderr.fileno(), fcntl.F_SETFL, os.O_NONBLOCK)
			# TODO ---------------------------------- porting to Windows

			while(self.process.poll() == None):

				line = ''
				try:
					line = self.process.stdout.readline()
				except:
					pass
				if len(line) > 0:
					self.output_callback(line)

				line2 = ''
				try:
					line2 = self.process.stderr.readline()
				except:
					pass
				if len(line2) > 0:
					self.output_callback(line2)

			print "Returned:",self.process.returncode
			if self.process.returncode < 0 and self.killed:
				self.callback(0)
			else:
				self.callback(self.process.returncode)

			return

		except OSError,detail:
			print "OSError",detail

		self.callback(-100)

	def kill(self):
		if not hasattr(os,'kill') or os.name == 'nt':
			import ctypes
			PROCESS_TERMINATE = 1
			handle = ctypes.windll.kernel32.OpenProcess(PROCESS_TERMINATE, False, self.process.pid)
			ctypes.windll.kernel32.TerminateProcess(handle, -1)
			ctypes.windll.kernel32.CloseHandle(handle)

		else:
			os.kill(self.process.pid,15)

		self.killed = True

class TS4Launcher(wx.App):
	def __init__(self,argv):
		self.name = PACKAGE+" v"+VERSION

		wx.App.__init__(self, redirect = False)
		wx.App.SetAppName(self,PACKAGE)

	def OnInit(self):
		window = LauncherWindow(None, wx.ID_ANY, self.name, size=(400, 400))
		window.Centre()
		window.Show(True)
		window.app = self

		self.window = window
		self.SetTopWindow(self.window)
		return True

if __name__ == '__main__':
	app = TS4Launcher(sys.argv)
	app.MainLoop()
