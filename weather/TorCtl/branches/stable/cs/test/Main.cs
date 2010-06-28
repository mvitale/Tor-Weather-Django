/*
 * File Main.cs
 * 
 * Copyright (C) 2005 Oliver Rau (olra0001@student-zw.fh-kl.de)
 * 
 * See LICENSE file for copying information 
 * 
 * Created on 08.08.2005 20:37
 * 
 * $Id: Main.cs 6862 2005-11-09 21:47:04Z nickm $
 */
 
using System;
using System.Collections;
using System.Net.Sockets;

using Tor.Control;

namespace Tor.Test
{
	class MainClass
	{
		public static void Main(string[] args)
		{
			Console.WriteLine("This version will only show Events occuring by tor!");
			
			// Create and open the tcp socket to tor
			TcpClient tcp = new TcpClient("127.0.0.1", 9051);
			
			// let the factory decide which Connection type we use
			
			ITorControlConnection conn = TorControlConnectionFactory.GetConnection(tcp);
			
			if (((object)conn).GetType() == typeof(TorControlConnection0))
				Console.WriteLine("Using Version 0");
			else
				Console.WriteLine("Using Version 1");
			
			// Attach the Handler for Messages
			conn.Message += new MessageEventHandler(MessageTest);
			// attach the handler for bandwith usage
			conn.BandwidthUsed += new BandwidthUsedEventHandler(BandwidthUsage);
			conn.CircuitStatus += new CircuitStatusEventHandler(CircuitStatus);
			conn.OrConnStatus  += new OrConnStatusEventHandler(OrConnStatus);
			
			// authenticate with tor
			conn.Authenticate(new byte[0]);
			
			// register my events
			conn.SetEvents(new ArrayList(new string[] {"ORCONN", "CIRC", "WARN", "ERR", "BW"}));
			
			// get the version
			string version = conn.GetInfo("version");
			
			Console.WriteLine("You are running tor version {0}", version);
			Console.ReadLine();
		}
		
		public static void MessageTest(object sender, MessageEventArgs args)
		{
			Console.WriteLine(":: {0} :: {1}", args.Severity, args.Msg);
		}
		
		public static void BandwidthUsage(object sender, BandwidthUsedEventArgs args)
		{
			Console.WriteLine("in: {0}, out: {1}", args.Read, args.Written);
		}
		
		public static void CircuitStatus(object sender, CircuitStatusEventArgs args)
		{
			Console.WriteLine("circ: {0} ({1}) [{2}]", args.CircID, args.Path, args.Status);
		}
		
		public static void OrConnStatus(object sender, OrConnStatusEventArgs args)
		{
			Console.WriteLine("orconn: {0} [{1}]", args.OrName, args.Status);
		}
	}
}
