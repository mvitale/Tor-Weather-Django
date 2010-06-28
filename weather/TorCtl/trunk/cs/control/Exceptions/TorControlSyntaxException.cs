/*
 * File TorControlSyntaxException.cs
 * 
 * Copyright (C) 2005 Oliver Rau (olra0001@student-zw.fh-kl.de)
 * 
 * See LICENSE file for copying information 
 * 
 * Created on 08.08.2005 20:37
 * 
 * $Id: TorControlSyntaxException.cs 6862 2005-11-09 21:47:04Z nickm $
 */

using System;

namespace Tor.Control
{
	/// <summary>
	/// Description of TorControlSyntaxException.
	/// </summary>
	public class TorControlSyntaxException : Exception
	{
		public TorControlSyntaxException(string s) : base(s)
		{}
	}
}
