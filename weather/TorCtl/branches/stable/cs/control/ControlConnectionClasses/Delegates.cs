/*
 * File Delegates.cs
 * 
 * Copyright (C) 2005 Oliver Rau (olra0001@student-zw.fh-kl.de)
 * 
 * See LICENSE file for copying information 
 * 
 * Created on 08.08.2005 20:37
 * 
 * $Id: Delegates.cs 6862 2005-11-09 21:47:04Z nickm $
 */

using System;
using System.Collections;

namespace Tor.Control
{
	#region Delegates
	/// <summary>
	/// Represents the method that will handle the CiruitStatus event.
	/// </summary>
	/// <param name="sender">The source of the event.</param>
	/// <param name="e">An <see cref="CircuitStatusEventArgs">CircuitStatusEventArgs</see> that contains
	/// the event data.
	/// </param>
	public delegate void CircuitStatusEventHandler (object sender, CircuitStatusEventArgs  e);
	/// <summary>
	/// Represents the method that will handle the StreamStatus event.
	/// </summary>
	/// <param name="sender">The source of the event.</param>
	/// <param name="e">An <see cref="StreamStatusEventArgs">StreamStatusEventArgs</see> that contains
	/// the event data.</param>
	public delegate void StreamStatusEventHandler  (object sender, StreamStatusEventArgs   e);
	/// <summary>
	/// Represents the method that will handle the OrConnStatus event.
	/// </summary>
	/// <param name="sender">The source of the event.</param>
	/// <param name="e">An <see cref="OrConnStatusEventArgs">OrConnStatusEventArgs</see> that contains
	/// the event data.</param>
	public delegate void OrConnStatusEventHandler  (object sender, OrConnStatusEventArgs   e);
	/// <summary>
	/// Represents the method that will handle the BandwidthUsed event.
	/// </summary>
	/// <param name="sender">The source of the event.</param>
	/// <param name="e">An <see cref="BandwidthUsedEventArgs">BandwidthUsedEventArgs</see> that contains
	/// the event data.</param>
	public delegate void BandwidthUsedEventHandler (object sender, BandwidthUsedEventArgs  e);
	/// <summary>
	/// Represents the method that will handle the NewDescriptors event.
	/// </summary>
	/// <param name="sender">The source of the event.</param>
	/// <param name="e">An <see cref="NewDescriptorsEventArgs">NewDescriptorsEventArgs</see> that contains
	/// the event data.</param>
	public delegate void NewDescriptorsEventHandler(object sender, NewDescriptorsEventArgs e);
	/// <summary>
	/// Represents the method that will handle the Message event.
	/// </summary>
	/// <param name="sender">The source of the event.</param>
	/// <param name="e">An <see cref="MessageEventArgs">MessageEventArgs</see> that contains
	/// the event data.</param>
	public delegate void MessageEventHandler       (object sender, MessageEventArgs        e);
	/// <summary>
	/// Represents the method that will handle the Unrecognized  event.
	/// </summary>
	/// <param name="sender">The source of the event.</param>
	/// <param name="e">An <see cref="UnrecognizedEventArgs">UnrecognizedEventArgs</see> that contains
	/// the event data.</param>
	public delegate void UnrecognizedEventHandler  (object sender, UnrecognizedEventArgs   e);
	#endregion Delegates
	
	/// <summary>
	/// Provides data for the <b>CircuitStatus</b> event.
	/// </summary>
	public class CircuitStatusEventArgs : EventArgs
	{
		string status;
		string circID;
		string path;
		
		#region Getter
		/// <summary>
		/// Gets the circuit ID.
		/// </summary>
		public string CircID {
			get {
				return circID;
			}
		}
		/// <summary>
		/// Gets the circuit path.
		/// </summary>
		public string Path {
			get {
				return path;
			}
		}
		/// <summary>
		/// Gets the circuit status.
		/// </summary>
		public string Status {
			get {
				return status;
			}
		}
		#endregion Getter
		
		/// <summary>
		/// Initializes a new instance of the <see cref="CircuitStatusEventArgs">CircuitStatusEventArgs</see> class.
		/// </summary>
		/// <param name="status">The status of the circuit.</param>
		/// <param name="circID">The ID of the circuit.</param>
		/// <param name="path">The path of the circuit.</param>
		public CircuitStatusEventArgs(string status, string circID, string path)
		{
			this.status = status;
			this.circID = circID;
			this.path   = path;
		}
	}
	
	/// <summary>
	/// Provides data for the <b>StreamStatus</b> event.
	/// </summary>
	public class StreamStatusEventArgs : EventArgs
	{
		string status;
		string streamID;
		string target;
		
		#region Getter
		/// <summary>
		/// Gets the stream ID.
		/// </summary>
		public string StreamID {
			get {
				return streamID;
			}
		}
		/// <summary>
		/// Gets the stream target.
		/// </summary>
		public string Target {
			get {
				return target;
			}
		}
		/// <summary>
		/// Gets the stream status.
		/// </summary>
		public string Status {
			get {
				return status;
			}
		}
		#endregion Getter
		
		/// <summary>
		/// Initializes a new instance of the <see cref="StreamStatusEventArgs">StreamStatusEventArgs</see> class.
		/// </summary>
		/// <param name="status">The status of the stream.</param>
		/// <param name="streamID">The ID of the stream.</param>
		/// <param name="target">The target of the stream.</param>
		public StreamStatusEventArgs(string status, string streamID, string target)
		{
			this.status   = status;
			this.streamID = streamID;
			this.target   = target;
		}
	}
	
	/// <summary>
	/// Provides data for the <b>OrConnStatus</b> event.
	/// </summary>
	public class OrConnStatusEventArgs : EventArgs
	{
		string status;
		string orName;
		
		#region Getter
		/// <summary>
		/// Gets the or name.
		/// </summary>
		public string OrName {
			get {
				return orName;
			}
		}
		/// <summary>
		/// Gets the or status.
		/// </summary>
		public string Status {
			get {
				return status;
			}
		}
		#endregion Getter
		
		/// <summary>
		/// Initializes a new instance of the <see cref="OrConnStatusEventArgs">OrConnStatusEventArgs</see> class.
		/// </summary>
		/// <param name="status">The status of the or.</param>
		/// <param name="orName">The name of the or.</param>
		public OrConnStatusEventArgs(string status, string orName)
		{
			this.status = status;
			this.orName = orName;
		}
	}
	
	/// <summary>
	/// Provides data for the <b>BandwidthUsed</b> event.
	/// </summary>
	public class BandwidthUsedEventArgs : EventArgs
	{
		long read;
		long written;
		
		#region Getter / Setter
		/// <summary>
		/// Gets the bytes read.
		/// </summary>
		public long Read {
			get {
				return read;
			}
		}
		/// <summary>
		/// Gets the bytes written.
		/// </summary>
		public long Written {
			get {
				return written;
			}
		}
		#endregion Getter
		
		/// <summary>
		/// Initializes a new instance of the <see cref="BandwidthUsedEventArgs">BandwidthUsedEventArgs</see> class.
		/// </summary>
		/// <param name="read">The bytes read.</param>
		/// <param name="written">The bytes written.</param>
		public BandwidthUsedEventArgs(long read, long written)
		{
			this.read    = read;
			this.written = written;
		}
	}
	
	/// <summary>
	/// Provides data for the <b>NewDescriptors</b> event.
	/// </summary>
	public class NewDescriptorsEventArgs : EventArgs
	{
		IList orList;
		
		/// <summary>
		/// Gets the list of or's.
		/// </summary>
		public IList OrList {
			get {
				return orList;
			}
		}
		
		/// <summary>
		/// Initializes a new instance of the <see cref="NewDescriptorsEventArgs">NewDescriptorsEventArgs</see> class.
		/// </summary>
		/// <param name="orList">The list of or's.</param>
		public NewDescriptorsEventArgs(IList orList)
		{
			this.orList = orList;
		}
	}
	
	/// <summary>
	/// Provides data for the <b>Message</b> event.
	/// </summary>
	public class MessageEventArgs : EventArgs
	{
		string severity;
		string msg;
		
		#region Getter
		/// <summary>
		/// Gets the message.
		/// </summary>
		public string Msg {
			get {
				return msg;
			}
		}
		/// <summary>
		/// Gets the severity of the message.
		/// </summary>
		public string Severity {
			get {
				return severity;
			}
			set {
				severity = value;
			}
		}
		#endregion Getter
		
		/// <summary>
		/// Initializes a new instance of the <see cref="MessageEventArgs">MessageEventArgs</see> class.
		/// </summary>
		/// <param name="severity">The severity of the message.</param>
		/// <param name="msg">The message.</param>
		public MessageEventArgs(string severity, string msg)
		{
			this.severity = severity;
			this.msg      = msg;
		}
	}
	
	/// <summary>
	/// Provides data for the <b>Unrecognized</b> event.
	/// </summary>
	public class UnrecognizedEventArgs : EventArgs
	{
		string type;
		string msg;
		
		#region Getter
		/// <summary>
		/// Gets the message of the event.
		/// </summary>
		public string Msg {
			get {
				return msg;
			}
		}
		
		/// <summary>
		/// Gets the type of the event.
		/// </summary>
		public string Type {
			get {
				return type;
			}
		}
		#endregion Getter
		
		/// <summary>
		/// Initializes a new instance of the <see cref="UnrecognizedEventArgs">UnrecognizedEventArgs</see> class.
		/// </summary>
		/// <param name="type">The type of the event.</param>
		/// <param name="msg">The message of the event.</param>
		public UnrecognizedEventArgs(string type, string msg)
		{
			this.msg = msg;
			this.type = type;
		}
		
	}
	
}
