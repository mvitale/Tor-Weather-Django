/*
 * File TorControlConnectionBase.cs
 * 
 * Copyright (C) 2005 Oliver Rau (olra0001@student-zw.fh-kl.de)
 * 
 * See LICENSE file for copying information 
 * 
 * Created on 08.08.2005 20:37
 * 
 * $Id: TorControlConnectionBase.cs 6862 2005-11-09 21:47:04Z nickm $
 */

using System;
using System.Collections;
using System.IO;
using System.Threading;

namespace Tor.Control
{
	/// <summary>
	/// This is a basic implementation to the ITorControllConnection interface, which holds
	/// the basic methods needed by the TorControllConnection.
	/// This class may be use to write future classes according to newer revision of the
	/// TorControlConnectionProtocol.
	/// </summary>
	public abstract class TorControlConnectionBase : ITorControlConnection
	{
		#region Events
		public abstract event CircuitStatusEventHandler  CircuitStatus;
		public abstract event StreamStatusEventHandler   StreamStatus;
		public abstract event OrConnStatusEventHandler   OrConnStatus;
		public abstract event BandwidthUsedEventHandler  BandwidthUsed;
		public abstract event NewDescriptorsEventHandler NewDescriptors;
		public abstract event MessageEventHandler        Message;
		public abstract event UnrecognizedEventHandler   Unrecognized;
		#endregion
		
		protected Queue  waiters;
		protected Thread thread;
		
		protected bool         debug = false;
		protected StreamWriter debugStream;
		
		protected TorControlConnectionBase()
		{
			this.waiters = Queue.Synchronized(new Queue());
		}
		
		#region Debugging methods
		public void EnableDebug()
		{
			debug = true;
			this.debugStream = null;
		}
		
		public void EnableDebug(Stream debugStream)
		{
			debug = true;
			
			this.debugStream = new StreamWriter(debugStream);
			
		}
		
		public void DisableDebug()
		{
			debug = false;
			this.debugStream = null;
		}
		
		public void WriteDebug(string message)
		{
			if (!debug)
				return;
			
			if (this.debugStream == null)
				Console.WriteLine(message);
			else
				this.debugStream.WriteLine(message);
				
		}
		#endregion Debugging methods
		
		protected void Run()
		{
			try {
				React();
				
				//TODO: specify the Exception more exactly
			} catch (Exception ex) {
				throw new ApplicationException();
			}
		}
		
		/// <summary>
		/// Start a thread to react to Tor's responses in the background.
		/// This is necessary to handle asynchronous events and synchronous
		/// responses that arrive independantly over the same socket.
		/// </summary>
		/// <param name="daemon">If the thread should be run in the background.</param>
		/// <returns>The new thread.</returns>
		public Thread LaunchThread(bool daemon)
		{
			Thread th = new Thread(new ThreadStart(Run));
			th.Name = "TorConnectionWorker";
			
			th.IsBackground = daemon;
			th.Start();
			this.thread = th;
			return th;
		}
		
		protected void CheckThread()
		{
			if (thread == null)
				LaunchThread(true);
		}
		
		protected abstract void React();
		
		/// <summary>
		/// Change the value of the configuration option 'key' to 'val'.
		/// </summary>
		/// <param name="key"></param>
		/// <param name="value"></param>
		public void SetConf(string key, string value)
		{
			IList lst = new ArrayList();
			lst.Add(key + " " + value);
			SetConf(lst);
		}
		
		public void SetConf(Hashtable kvHt)
		{
			IList lst = new ArrayList();
			
			foreach (string key in kvHt.Keys) {
				lst.Add(key + " " + kvHt[key] + "\n");
			}
			SetConf(lst);
		}
		
		public abstract void SetConf(IList kvList);
		
		public IList GetConf(string key)
		{
			IList lst = new ArrayList();
			lst.Add(key);
			return GetConf(lst);
		}
		
		public abstract IList GetConf(IList keys);
		
		public abstract void SetEvents(IList events);
		
		public abstract void Authenticate(byte[] auth);
		public abstract void SaveConf();
		public abstract void Signal(string signal);
		
		public abstract Hashtable MapAddresses(IList kvLines);
		
		public Hashtable MapAddresses(Hashtable addresses)
		{
			IList kvList = new ArrayList();
			
			foreach (string key in addresses.Keys) {
				kvList.Add(key + " " + addresses[key]);
			}
			
			return MapAddresses(kvList);
		}
		
		public abstract Hashtable GetInfo(IList keys);
		
		public string GetInfo(string key)
		{
			IList lst = new ArrayList();
			lst.Add(key);
			Hashtable m = GetInfo(lst);
			return (string) m[key];
		}
		
    public abstract string ExtendCircuit(string circID, string path);

    public abstract void AttachStream(string streamID, string circID);

    public abstract string PostDescriptor(string desc);

    public abstract void RedirectStream(string streamID, string address);

    public abstract void CloseStream(string streamID, byte reason);

    public abstract void CloseCircuit(string circID, bool ifUnused);
	}
}
