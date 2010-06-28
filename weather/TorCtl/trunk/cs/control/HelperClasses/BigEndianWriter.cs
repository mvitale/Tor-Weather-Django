/*
 * File BigEndianWriter.cs
 * 
 * Copyright (C) 2005 Oliver Rau (olra0001@student-zw.fh-kl.de)
 * 
 * See LICENSE file for copying information 
 * 
 * Created on 19.09.2005 23:12
 * 
 * $Id: BigEndianWriter.cs 6862 2005-11-09 21:47:04Z nickm $
 */

using System;
using System.IO;

namespace Tor.Control
{
	/// <summary>
	/// Implements a <see cref="BinaryWriter">BinaryWriter</see> which writes in big-endian order 
	/// instead of little-endian.
	/// </summary>
	/// <remarks>
	/// This class is not fully implemented, it's just implemented so far, that it will handle
	/// the operations needed by tor.<br />
	/// All the other operations are still the one's implemented by the <b>BinaryWriter</b>.
	/// </remarks>
	public class BigEndianWriter : BinaryWriter
	{
		public BigEndianWriter(Stream s) : base(s) {}
		
		
		public void WriteShort(int value)
		{
			byte a = (byte) (0xff & (value >> 8));
			byte b = (byte) (0xff & value);
			
			base.Write(a);
			base.Write(b);
		}
		
		public void WriteInt(int value)
		{
			// first we need to swap all bytes
			value = Convert.ToInt32(((value & 0xFF000000) >> 24) | (( value & 0x000000FF) << 24) |
			                        ((value & 0x00FF0000) >> 16) | (( value & 0x0000FF00) << 16));
			
			base.Write(value);
		}
	}
}
