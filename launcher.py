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

import sys,os
import wx

import main		# ts4 starter

NAME=main.NAME+" Launcher"
VERSION="0.0.1-rc2"

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
		# MANNAGGIA AL COLLAPSIBLE!!! MORTACCI SUA CE FOSSE UN MODO PER FALLO FUNZIONA'!!!!
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
		self.Bind(wx.EVT_END_PROCESS, self.OnProcessEnded)
		self.Bind(wx.EVT_IDLE, self.OnIdle)

		self.process = None
		self.pid = 0
		self.exiting = False
		self.output = ''
		self.killed = False
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
		self.stdout = wx.TextCtrl(panel, wx.ID_ANY, style=wx.TE_MULTILINE, size=(-1,100))
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

		# linea 3: checkbox "autochat"
		line3 = wx.BoxSizer(wx.HORIZONTAL)

		# checkbox "autochat"
		self.autochat = wx.CheckBox(panel, wx.ID_ANY, "Chat automatica (sperimentale)")
		line3.Add(self.autochat,1,wx.ALIGN_TOP|wx.LEFT,10)

		self.client_frame.Add(line3,0,wx.EXPAND|wx.ALL-wx.BOTTOM,10)

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
		self.sizer.Fit(self)

		# focus su address
		self.address.SetFocus()

	def cb_wrap(self,event=None):
		event.GetEventObject().Wrap(event.GetSize()[0])

	def cb_close(self,event=None):
		# stoppa il server se necessario
		if self.button_start.GetLabel() == "Stop":
			self.cb_start(None)

		self.exiting = True
		if self.process == None:
			self.Destroy()
			self.app.ExitMainLoop()

	def cb_standalone(self, event=None):
		for c in self.client_labels:
			c.Enable(not self.standalone.GetValue())
		self.address.Enable(not self.standalone.GetValue())
		self.name.Enable(not self.standalone.GetValue())
		self.autochat.Enable(not self.standalone.GetValue())
		self.cb_connect_text()

	def OnIdle(self, event=None):
		if self.process != None:
			out, err = self._read_process()

			self.output = self.output + out + err
			if self.standalone.GetValue():
				self.stdout.AppendText(out+err)

	def cb_connect_text(self, event=None):
		self.bind_port.Enable(len(self.address.GetValue().strip()) == 0 or self.standalone.GetValue())
		self.bind_label.Enable(self.bind_port.IsEnabled())

	def __del__(self):
		if self.process != None:
			self.process.Detach()
			self._kill()

	def _read_process(self):
		out = err = ''

		stream = self.process.GetInputStream()
		stream2 = self.process.GetErrorStream()

		if stream.CanRead():
			out = stream.read()

		if stream2.CanRead():
			err = stream2.read()

		# mischiamo stdout e stderr, mettiamo newline se necessario
		try:
			if out[-1] != '\n' and err[-1] != '\n':
				out = out + '\n'
		except:
			pass

		return out,err

	def _kill(self):
		if self.pid > 0:
			print "Killing process",self.pid
			if os.name == 'nt':
				import ctypes
				# PROCESS_TERMINATE = 1
				handle = ctypes.windll.kernel32.OpenProcess(1, False, self.pid)
				ctypes.windll.kernel32.TerminateProcess(handle, -1)
				ctypes.windll.kernel32.CloseHandle(handle)

			else:
				self.process.Kill(self.pid,wx.SIGTERM)

			self.pid = 0
			self.killed = True

	def cb_start(self, event=None):
		if self.button_start.GetLabel() == "Stop":
			self.button_start.SetLabel("Termino il server...")
			self.button_start.Enable(False)
			self._kill()

		else:
			argv = []
			if self.standalone.GetValue():
				# avvia solo server -- niente altro
				argv.extend( ('standalone', 'bind='+str(self.bind_port.GetValue())) )
				self.button_start.SetLabel("Stop")
				self.standalone.Enable(False)
				self.bind_port.Enable(False)
				self.stdout.Clear()

			else:
				addr = self.address.GetValue().strip()
				if len(addr) > 0:
					argv.append('server='+addr)

				name = self.name.GetValue().strip()
				if len(name) > 0:
					newname = ''
					for i in range(0,len(name)):
						if name[i] == ' ':
							# inserisci spazio prima
							newname = newname + '\\'
						newname += name[i]

					argv.append('name='+newname)

				if(not self.autochat.GetValue()):
					argv.append('chat=manual')

				self.Show(False)

			self.output = ''
			self.killed = False
			self.process = wx.Process(self)
			self.process.Redirect()

			args = ["python", "-u", "\"" + main.__file__ + "\"", "launcher"]
			args.extend(argv)

			print "Executing \""+' '.join(args)+"\""
			self.pid = wx.Execute(' '.join(args), wx.EXEC_ASYNC, self.process)

	def OnProcessEnded(self, event):
		retcode = event.GetExitCode()
		print "Pid",event.GetPid(),"returned with exit code",retcode

		out,err = self._read_process()
		if self.standalone.GetValue():
			self.stdout.AppendText(out+err)
		self.output = self.output + out + err

		if retcode != main.EXIT_SUCCESS:

			showdlg = True
			text = main.NAME+" terminato per motivi sconosciuti."

			# analizza l'output
			cause = ''
			lines = self.output.splitlines()
			for abc in lines:
				# estrai linea status
				if abc.startswith('__STATUS__'):
					ext = abc.split(":")

					try:
						cause = ext[2]

						# rimuovi lo stato dall'output
						self.output = self.output.replace(abc,"")

					except:
						print "Launcher: Oops..."

			# il trucco del minore di zero dovrebbe funzionare anche per windows
			if retcode < main.EXIT_SUCCESS:
				if os.name == 'nt':
					# chissa cosa sara' stato...
					text = main.NAME+" terminato inaspettatamente."
				else:
					# segnale di uscita
					text = main.NAME+" terminato a causa del segnale "+str(-retcode)+"."

				if self.killed: showdlg = False

			else:
				if cause == 'CONNECTION-CLOSED':
					text = u"La connessione al server di gioco è stata chiusa."

				elif cause == 'CONNECTION-REFUSED':
					text = u"La connessione al server di gioco è stata rifiutata."

				elif cause == 'CONNECT-ERROR':
					text = "Errore di connessione al server di gioco."

				elif cause == 'CONNECT-TIMEOUT':
					text = u"Il tempo di connessione al server di gioco è scaduto."

				elif cause == 'SYS-ERROR':
					text = main.NAME+" terminato per un errore di sistema o un errore non gestito.\n\nMaggiori informazioni nei dettagli."

				elif cause == 'BAD-ARGUMENT':
					text = "Argomenti di avvio non validi."

				elif cause == 'BIND-ERROR':
					text = "Impossibile avviare il server. Controlla che non ci sia un altro server attivo."

			if showdlg:
				d = ReturnDialog(self, text,main.NAME + " terminato",self.output)
				d.Centre()
				d.ShowModal()
				d.Destroy()

		self.process.Destroy()
		self.process = None

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

	def cb_version(self, event=None):
		d = wx.MessageDialog(self, "Launcher versione "+VERSION+"\n\n"+main.NAME+" versione "+main.VERSION, "Versione", wx.OK|wx.ICON_INFORMATION)
		d.ShowModal()
		d.Destroy()

class TS4Launcher(wx.App):
	def __init__(self,argv):
		self.name = NAME+" v"+VERSION

		wx.App.__init__(self, redirect = False)
		wx.App.SetAppName(self,NAME)

	def OnInit(self):
		window = LauncherWindow(None, wx.ID_ANY, self.name, size=(400, 400))
		window.Centre()
		window.Show(True)
		window.app = self

		self.window = window
		self.SetTopWindow(self.window)
		return True

def _main():
	app = TS4Launcher(sys.argv)
	app.MainLoop()

if __name__ == '__main__':
	_main()
