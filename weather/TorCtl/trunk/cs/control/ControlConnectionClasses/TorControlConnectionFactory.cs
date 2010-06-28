/*
 * File TorControlConnectionFactory.cs
 * 
 * Copyright (C) 2005 Oliver Rau (olra0001@student-zw.fh-kl.de)
 * 
 * See LICENSE file for copying information 
 * 
 * Created on 08.08.2005 20:37
 * 
 * $Id: TorControlConnectionFactory.cs 6862 2005-11-09 21:47:04Z nickm $
 */

using System;
using System.IO;
using System.Net.Sockets;

namespace Tor.Control
{
	/// <summary>
	/// This is the factory class for the TorConnection, which checks the version for you
	/// and then loads the corresponding TorControlConnection.
	/// </summary>
	public class TorControlConnectionFactory
	{
		protected static int DetectVersion(Stream stream)
		{
			byte[] buffer = {0, 0, 13, 10};
			
			stream.Write(buffer, 0, 4);
			
			BinaryReader br = new BinaryReader(stream);
			
			int len = br.ReadUInt16();
			int tp  = br.ReadUInt16();
			
			if (tp == 0) {
				byte[] err = new byte[len];
				br.Read(err, 0, err.Length);
				return 0;
			} else if ((len & 0xff00) != 0x0a00 &&
			           (len & 0x00ff) != 0x000a &&
			           (tp  & 0xff00) != 0x0a00 &&
			           (tp  & 0x00ff) != 0x000a) {
				while (br.Read() != '\n');
			}
			
			return 1;
		}
		
		public static ITorControlConnection GetConnection(TcpClient client)
		{
			int version = DetectVersion(client.GetStream());
			
			// TODO: Checkin future versions here
			if (version == 0)
				return new TorControlConnection0(client);
			else
				return new TorControlConnection1(client);
		}

	}
}
