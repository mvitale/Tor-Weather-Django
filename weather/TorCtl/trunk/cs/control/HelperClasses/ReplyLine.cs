/*
 * File ReplyLine.cs
 * 
 * Copyright (C) 2005 Oliver Rau (olra0001@student-zw.fh-kl.de)
 * 
 * See LICENSE file for copying information 
 * 
 * Created on 08.08.2005 20:37
 * 
 * $Id: ReplyLine.cs 6862 2005-11-09 21:47:04Z nickm $
 */

using System;

namespace Tor.Control
{
	/// <summary>
	/// This class handles the default reply data of tor
	/// </summary>
	public class ReplyLine
	{
		string status;
		string msg;
		string rest;
		
		#region Getter Methods
		public string Msg {
			get {
				return msg;
			}
		}
		public string Rest {
			get {
				return rest;
			}
		}
		public string Status {
			get {
				return status;
			}
		}
		#endregion Getter Methods
		
		public ReplyLine(string status, string msg, string rest)
		{
			this.status = status;
			this.msg    = msg;
			this.rest   = rest;
		}
	}
}
