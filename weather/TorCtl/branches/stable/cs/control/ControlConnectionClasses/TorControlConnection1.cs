/*
 * File TorControlConnection1.cs
 * 
 * Copyright (C) 2005 Oliver Rau (olra0001@student-zw.fh-kl.de)
 * 
 * See LICENSE file for copying information 
 * 
 * Created on 08.08.2005 20:37
 * 
 * $Id: TorControlConnection1.cs 6862 2005-11-09 21:47:04Z nickm $
 */

using System;
using System.Collections;
using System.IO;
using System.Net.Sockets;
using System.Text;

namespace Tor.Control
{
	/// <summary>
	/// Description of TorControlConnection1.
	/// </summary>
	public class TorControlConnection1 : TorControlConnectionBase
	{
		#region Events
		public override event CircuitStatusEventHandler  CircuitStatus;
		public override event StreamStatusEventHandler   StreamStatus;
		public override event OrConnStatusEventHandler   OrConnStatus;
		public override event BandwidthUsedEventHandler  BandwidthUsed;
		public override event NewDescriptorsEventHandler NewDescriptors;
		public override event MessageEventHandler        Message;
		public override event UnrecognizedEventHandler   Unrecognized;
		#endregion
		
		StreamReader input;
		StreamWriter output;
		
		public TorControlConnection1(TcpClient connection) : this(connection.GetStream())
		{}
		
		public TorControlConnection1(Stream s) : this(new StreamReader(s), 
		                                              new StreamWriter(s))
		{}
		
		public TorControlConnection1(StreamReader i, StreamWriter o)
		{
			this.output = o;
			this.input  = i;
			
			// Synchronize the internal queue by default
			this.waiters = Queue.Synchronized(new Queue());
		}
		
		protected void WriteEscaped(string s)
		{
			string[] tokens = s.Split('\n');
			
			string temp;
			foreach (string line in tokens) {
				if (line.StartsWith("."))
					temp = "." + line;
				
				if (line.EndsWith("\r"))
					temp = line + "\n";
				else
					temp = line + "\r\n";
				
				WriteDebug(">> "+temp);
				
				output.Write(temp);
			}
			
			output.Write(".\r\n");
			
			WriteDebug(">> .\n");
		}
		
		public static string Quote(string s)
		{
			StringBuilder sb = new StringBuilder('\"');
			for (int i=0; i < s.Length; ++i) {
				char c = s.ToCharArray()[i];
				switch (c) {
					case '\r':
					case '\n':
					case '\\':
					case '\"':
						sb.Append('\\');
						break;
				}
			}
			
			sb.Append('\"');
			return sb.ToString();
		}
		
		protected ArrayList ReadReply()
		{
			ArrayList reply = new ArrayList();
			
			string c;
			
			do {
				string line = input.ReadLine();
				WriteDebug("<< "+line);
				
				// TODO: maybe fetch if line is null
				if (line.Length < 4)
					throw new TorControlSyntaxException("Line (\"" + line + "\") too short");
				
				string status = line.Substring(0, 3);
				
				c = line.Substring(3,1);
				string msg = line.Substring(4);
				string rest = null;
				
				if (c == "+") {
					StringBuilder data = new StringBuilder();
					
					while (true) {
						line = input.ReadLine();
						
						WriteDebug("<< "+line);
						if (line.Equals("."))
							break;
						else if (line.StartsWith("."))
							line = line.Substring(2);
						
						data.Append(line).Append("\n");
					}
					
					rest = data.ToString();
				}
				reply.Add(new ReplyLine(status, msg, rest));
				
			} while (c != " ");
			
			return reply;
		}
		
		protected override void React()
		{
			while (true) {
				ArrayList lst = ReadReply();
				
				if (((ReplyLine)lst[0]).Status.StartsWith("6"))
					HandleEvent(lst);
				else {
					Waiter w;
					
					lock (waiters.SyncRoot) {
						w = (Waiter) waiters.Dequeue();
						WriteDebug("fetched waiter: " + w.Id);
					}
					
					w.Response = lst;
				}
			}
		}
		
		protected IList SendAndWaitForResponse(string s, string rest)
		{
			CheckThread();
			
			Waiter w = new Waiter();
			
			WriteDebug(">> " + s);
			
			lock (waiters.SyncRoot) {
				output.Write(s);
				output.Flush();
				
				if (rest != null)
					WriteEscaped(rest);
				
				
				waiters.Enqueue(w);
				WriteDebug("added waiter: " + w.Id);
			}
			
			ArrayList lst = (ArrayList) w.Response;
			
			foreach (ReplyLine c in lst) {
				if (! c.Status.StartsWith("2"))
					throw new TorControlException("Error reply: " + c.Msg);
			}
			
			return lst;
		}
		
		protected void HandleEvent(ArrayList events)
		{
			foreach (ReplyLine line in events) {
				int idx = line.Msg.IndexOf(" ");
				string tp = line.Msg.Substring(0, idx).ToUpper();
				
				string rest = line.Msg.Substring(idx+1);
				
				if (tp == "CIRC") {
					if (this.CircuitStatus != null) {
						string[] pars = rest.Split(' ');
						CircuitStatusEventArgs args = new CircuitStatusEventArgs(pars[1], 
						                                                         pars[0], 
						                                                         pars[2]);
						
						CircuitStatus(this, args);
					}
				} else if (tp == "STREAM") {
					if (this.StreamStatus != null) {
						string[] pars = rest.Split(' ');
						StreamStatusEventArgs args = new StreamStatusEventArgs(pars[1], 
						                                                       pars[0],
						                                                       pars[3]);
						
						StreamStatus(this, args);
					}
				} else if (tp == "ORCONN") {
					if (this.OrConnStatus != null) {
						string[] pars = rest.Split(' ');
						OrConnStatusEventArgs args = new OrConnStatusEventArgs(pars[1], 
						                                                       pars[0]);
						
						OrConnStatus(this, args);
					}
				} else if (tp == "BW") {
					if (this.BandwidthUsed != null) {
						string[] pars = rest.Split(' ');
						BandwidthUsedEventArgs args = new BandwidthUsedEventArgs(long.Parse(pars[0]),
						                                                         long.Parse(pars[1]));
						
						BandwidthUsed(this, args);
					}
				} else if (tp == "NEWDESC") {
					if (this.NewDescriptors != null) {
						IList lst = Bytes.SplitStr(null, rest);
						NewDescriptorsEventArgs args = new NewDescriptorsEventArgs(lst);
						
						NewDescriptors(this, args);
					}
				} else if (tp == "DEBUG"  ||
				           tp == "INFO"   ||
				           tp == "NOTICE" ||
				           tp == "WARN"   ||
				           tp == "ERR") {
					if (this.Message != null) {
						MessageEventArgs args = new MessageEventArgs(tp, rest);
						
						Message(this, args);
					}
				} else {
					if (this.Unrecognized != null) {
						UnrecognizedEventArgs args = new UnrecognizedEventArgs(tp, rest);
						
						Unrecognized(this, args);
					}
				}
			}
		}
		
		public override void SetConf(IList kvList)
		{
			if (kvList.Count == 0)
				return;
			
			StringBuilder sb = new StringBuilder("SETCONF");
			foreach (string kv in kvList) {
				int i = kv.IndexOf(" ");
				if (i == -1)
					sb.Append(" ").Append(kv);
				
				sb.Append(" ").Append(kv.Substring(0, i)).Append("=").Append(Quote(kv.Substring(i+1)));
			}
			
			sb.Append("\r\n");
			
			SendAndWaitForResponse(sb.ToString(), null);
		}
		
		public override IList GetConf(IList keys)
		{
			StringBuilder sb = new StringBuilder("GETCONF");
			
			foreach (string key in keys) {
				sb.Append(" ").Append(key);
			}
			
			sb.Append("\r\n");
			ArrayList lst = (ArrayList) SendAndWaitForResponse(sb.ToString(), null);
			ArrayList result = new ArrayList();
			
			foreach (ReplyLine rl in lst) {
				string kv = rl.Msg;
				int idx = kv.IndexOf("=");
				result.Add(new ConfigEntry(kv.Substring(0, idx), kv.Substring(idx+1)));
			}
			
			return result;
		}
		
		public override void SetEvents(IList events)
		{
			StringBuilder sb = new StringBuilder("SETEVENTS");
			
			foreach (object ev in events) {
				if (ev.GetType() == typeof(string)) {
					sb.Append(" ").Append((string) ev);
				} else {
					int i = (int) ev;
					sb.Append(" ").Append(TorControl.EventNames[i]);
				}
			}
			
			sb.Append("\r\n");
			SendAndWaitForResponse(sb.ToString(), null);
		}
		
		public override void Authenticate(byte[] auth)
		{
			string cmd = "AUTHENTICATE " + Bytes.Hex(auth) + "\r\n";
			SendAndWaitForResponse(cmd, null);
			
		}
		
		public override void SaveConf()
		{
			SendAndWaitForResponse("SAVECONF\r\n", null);
		}
		
		public override void Signal(string signal)
		{
			string cmd = "SIGNAL " + signal + "\r\n";
			SendAndWaitForResponse(cmd, null);
		}
		
		public override Hashtable MapAddresses(IList kvLines)
		{
			StringBuilder sb = new StringBuilder("MAPADDRESS");
			
			foreach (string kv in kvLines) {
				int i = kv.IndexOf(" ");
				sb.Append(" ").Append(kv.Substring(0, i)).Append("=").Append(Quote(kv.Substring(i+1)));
			}
			
			sb.Append("\r\n");
			ArrayList lst = (ArrayList) SendAndWaitForResponse(sb.ToString(), null);
			
			Hashtable result = new Hashtable();
			
			foreach (ReplyLine rl in lst) {
				string kv = rl.Msg;
				int idx = kv.IndexOf("=");
				result.Add(kv.Substring(0, idx), kv.Substring(idx+1));
			}
			
			return result;
		}
		
		public override Hashtable GetInfo(IList keys)
		{
			StringBuilder sb = new StringBuilder("GETINFO");
			foreach (string key in keys) {
				sb.Append(" ").Append(key);
			}
			
			sb.Append("\r\n");
			ArrayList lst = (ArrayList) SendAndWaitForResponse(sb.ToString(), null);
			
			Hashtable result = new Hashtable();
			
			foreach (ReplyLine rl in lst) {
				int idx = rl.Msg.IndexOf("=");
				
				if (idx<0)
					break;
				
				string k = rl.Msg.Substring(0, idx);
				
				string v;
				
				if (rl.Rest != null)
					v = rl.Rest;
				else
					v = rl.Msg.Substring(idx+1);
				
				result.Add(k, v);
			}
			
			return result;
		}
		
		public override string ExtendCircuit(string circID, string path)
		{
			ArrayList lst = (ArrayList) SendAndWaitForResponse("EXTENDCIRCUIT " + circID + " " + path + "\r\n", null);
			
			return ((ReplyLine)lst[0]).Msg;
		}
		
		public override void AttachStream(string streamID, string circID)
		{
			SendAndWaitForResponse("ATTACHSTREAM " + streamID + " " + circID + "\r\n", null);
		}
		
		public override string PostDescriptor(string desc)
		{
			ArrayList lst = (ArrayList) SendAndWaitForResponse("+POSTDESCRIPTOR\r\n", desc);
			
			return ((ReplyLine)lst[0]).Msg;
		}
		
		public override void RedirectStream(string streamID, string address)
		{
				SendAndWaitForResponse("REDIRECTSTREAM " + streamID + " " + address + "\r\n", null);
		}
		
		public override void CloseStream(string streamID, byte reason)
		{
			SendAndWaitForResponse("CLOSESTREAM " + streamID + " " + reason + "\r\n", null);
		}
		
		public override void CloseCircuit(string circID, bool ifUnused)
		{
			SendAndWaitForResponse("CLOSECIRCUIT " + circID + (ifUnused? " IFUNUSED":"") + "\r\n", null);
		}
	}
}
