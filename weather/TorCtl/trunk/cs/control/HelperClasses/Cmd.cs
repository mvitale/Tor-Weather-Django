/*
 * File Cmd.cs
 * 
 * Copyright (C) 2005 Oliver Rau (olra0001@student-zw.fh-kl.de)
 * 
 * See LICENSE file for copying information 
 * 
 * Created on 16.09.2005 20:57
 * 
 * $Id: Cmd.cs 6862 2005-11-09 21:47:04Z nickm $
 */

using System;

namespace Tor.Control
{
	/// <summary>
	/// Description of Cmd.
	/// </summary>
	public class Cmd
	{
		TorControl.Commands type;
		byte[] body;
		
		#region Getter
		public byte[] Body {
			get {
				return body;
			}
		}
		public TorControl.Commands Type {
			get {
				return type;
			}
		}
		#endregion Getter
		
		public Cmd(TorControl.Commands t, byte[] b) { type = t; body = b; }
		public Cmd(TorControl.Commands t, int l) { type = t; body = new byte[l]; }
	}
}
