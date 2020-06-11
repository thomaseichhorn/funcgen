import sys, os, glob, serial
import curses
import time
from jds6600 import jds6600
from math import *

def draw_menu ( stdscr, theport ) :

	# Require minimum terminal size
	height, width = stdscr.getmaxyx ( )
	if ( height < 24 or width < 80 ) :
		curses.endwin ( )
		print ( "The required minimum terminal size is 80 columns by 24 rows!\nYour terminal is {} by {}!" .format ( width, height ) )
		return -1

	j = jds6600 ( theport )

	# User input key
	k = 0

	# Clear and refresh the screen for a blank canvas
	stdscr.clear ( )
	stdscr.refresh ( )

	# Start colors in curses
	curses.start_color ( )
	curses.init_pair ( 1, curses.COLOR_YELLOW, curses.COLOR_BLACK )
	curses.init_pair ( 2, curses.COLOR_CYAN, curses.COLOR_BLACK )
	curses.init_pair ( 3, curses.COLOR_RED, curses.COLOR_BLACK )
	curses.init_pair ( 4, curses.COLOR_BLACK, curses.COLOR_WHITE )
	curses.init_pair ( 5, curses.COLOR_WHITE, curses.COLOR_BLACK )

	# Refresh time in 1/10 sec
	curses.halfdelay ( 1 )

	# The channel we are editing
	activechan = 1
	# Loop where k is the last character pressed
	while ( k != ord ( 'q' ) ) :

		# Initialization
		stdscr.clear ( )

		# Select SW active chan
		if ( k == ord ( '1' ) ) :
			activechan = 1
		if ( k == ord ( '2' ) ) :
			activechan = 2

		# Read device
		status_ch1 = "Indef"
		status_ch2 = "Indef"
		bool_ch1, bool_ch2 = j.getchannelenable ( )

		# Chan on/off
		if ( k == ord ( 'o' ) or k == ord ( 'O' ) ) :
			if ( activechan == 1 ) :
				j.setchannelenable ( not bool_ch1, bool_ch2 )
			if ( activechan == 2 ) :
				j.setchannelenable ( bool_ch1, not bool_ch2 )
			stdscr.refresh ( )

		if ( bool_ch1 == True ) :
			status_ch1 = "ON"
		else :
			status_ch1 = "OFF"
		if ( bool_ch2 == True ) :
			status_ch2 = "ON"
		else :
			status_ch2 = "OFF"

		#User input box position
		size_y_box = 6
		size_x_box = 24
		start_y_box = 17
		if ( activechan == 1 ) :
			start_x_box = 4
		else :
			start_x_box = 34

		# Wave
		status_wave1 = j.getwaveform ( 1 )
		status_wave2 = j.getwaveform ( 2 )
		if ( k == ord ( 'w' ) or k == ord ( 'W' ) ) :
			waves = [ "Sine","Square","Pulse","Triangle","Partial Sine","CMOS","DC","Half-Wave","Full-Wave","Pos-Ladder","Neg-Ladder", "Noise", "Exp-Rise","Exp-Decay","Multi-Tone","Sinc","Lorenz" ]
			help_win = stdscr.subwin ( 21, 19, 2, 61 )
			help_win.bkgd ( curses.color_pair ( 5 ) )
			help_win.box ( )
			help_win.addstr ( 1, 2, "Waveforms:" )
			for i in range ( 0, 17, 1 ) :
				help_win.addstr ( i + 3, 2, "{}: {}". format ( i, waves[i] ) )
			curses.echo ( )
			help_win.refresh ( )
			wave_win = stdscr.subwin ( size_y_box, size_x_box, start_y_box, start_x_box )
			wave_win.bkgd ( curses.color_pair ( activechan ) )
			wave_win.box ( )
			wave_win.addstr ( 1, 2, "Waveform Channel {}:" .format ( activechan ) )
			curses.echo ( )
			wave_win.addstr ( 3, 2, "[#] : " )
			wave_win.refresh ( )
			waveinput = -1
			input = wave_win.getstr ( 3, 8, 10 )
			try :
				waveinput = int ( input )
			except ValueError :
				wave_win.addstr ( 4, 2, "Invalid! W=[0..16]" )
				wave_win.refresh ( )
			if ( waveinput < 0 or waveinput > 16 ) :
				wave_win.addstr ( 4, 2, "Invalid! W=[0..16]" )
				wave_win.refresh ( )
				curses.napms ( 2500 )
				del wave_win
				del help_win
				stdscr.refresh ( )
				curses.halfdelay ( 1 )
			else :
				j.setwaveform ( activechan, waveinput )
				del wave_win
				del help_win
				stdscr.refresh ( )
				curses.halfdelay ( 1 )

		# Frequency
		status_freq1 = j.getfrequency ( 1 )
		status_freq2 = j.getfrequency ( 2 )
		freq_ch1_unit = "Hz"
		freq_ch2_unit = "Hz"
		if status_freq1 >= 10000.0 :
			status_freq1 = status_freq1 / 1000.0
			freq_ch1_unit = "KHz"
			if status_freq1 >= 10000.0 :
				status_freq1 = status_freq1 / 1000.0
				freq_ch1_unit = "MHz"
		if status_freq2 >= 10000.0 :
			status_freq2 = status_freq2 / 1000.0
			freq_ch2_unit = "KHz"
			if status_freq2 >= 10000.0 :
				status_freq2 = status_freq2 / 1000.0
				freq_ch2_unit = "MHz"
		if ( k == ord ( 'f' ) or k == ord ( 'F' ) ) :
			freq_win = stdscr.subwin ( size_y_box, size_x_box, start_y_box, start_x_box )
			freq_win.bkgd ( curses.color_pair ( activechan ) )
			freq_win.box ( )
			freq_win.addstr ( 1, 2, "Frequency Channel {}:" .format ( activechan ) )
			curses.echo ( )
			freq_win.addstr ( 3, 2, "[Hz] : " )
			freq_win.refresh ( )
			freqinput = -1
			input = freq_win.getstr ( 3, 9, 10 )
			try :
				freqinput = float ( input )
			except ValueError :
				freq_win.addstr ( 4, 2, "Invalid! F=[0..1.5e7]" )
				freq_win.refresh ( )
			# TODO: Check range!
			if ( freqinput < 0.0 or freqinput > 15000000 ) :
				freq_win.addstr ( 4, 2, "Invalid! F=[0..1.5e7]" )
				freq_win.refresh ( )
				curses.napms ( 2500 )
				del freq_win
				stdscr.refresh ( )
				curses.halfdelay ( 1 )
			else :
				j.setfrequency ( activechan, freqinput, 0 )
				del freq_win
				stdscr.refresh ( )
				curses.halfdelay ( 1 )

		# Amplitude
		status_amp1 = j.getamplitude ( 1 )
		status_amp2 = j.getamplitude ( 2 )
		if ( k == ord ( 'a' ) or k == ord ( 'A' ) ) :
			amp_win = stdscr.subwin ( size_y_box, size_x_box, start_y_box, start_x_box )
			amp_win.bkgd ( curses.color_pair ( activechan ) )
			amp_win.box ( )
			amp_win.addstr ( 1, 2, "Amplitude Channel {}:" .format ( activechan ) )
			curses.echo ( )
			amp_win.addstr ( 3, 2, "[V] : " )
			amp_win.refresh ( )
			ampinput = -1
			input = amp_win.getstr ( 3, 8, 10 )
			try :
				ampinput = float ( input )
			except ValueError :
				amp_win.addstr ( 4, 2, "Invalid! V=[0..20]" )
				amp_win.refresh ( )
			if ( ampinput < 0.0 or ampinput > 20.0 ) :
				amp_win.addstr ( 4, 2, "Invalid! V=[0..20]" )
				amp_win.refresh ( )
				curses.napms ( 2500 )
				del amp_win
				stdscr.refresh ( )
				curses.halfdelay ( 1 )
			else :
				j.setamplitude ( activechan, ampinput )
				del amp_win
				stdscr.refresh ( )
				curses.halfdelay ( 1 )

		# Offset
		status_offs1 = j.getoffset ( 1 )
		status_offs2 = j.getoffset ( 2 )
		if ( k == ord ( 's' ) or k == ord ( 'S' ) ) :
			offs_win = stdscr.subwin ( size_y_box, size_x_box, start_y_box, start_x_box )
			offs_win.bkgd ( curses.color_pair ( activechan ) )
			offs_win.box ( )
			offs_win.addstr ( 1, 2, "Offset Channel {}:" .format ( activechan ) )
			curses.echo ( )
			offs_win.addstr ( 3, 2, "[V] : " )
			offs_win.refresh ( )
			offsinput = 0
			input = offs_win.getstr ( 3, 8, 10 )
			try :
				offsinput = float ( input )
			except ValueError :
				offs_win.addstr ( 4, 2, "Invalid! V=[-9.99..9.99]" )
				offs_win.refresh ( )
			if ( offsinput < -9.99 or offsinput > 9.99 ) :
				offs_win.addstr ( 4, 2, "Invalid! V=[-9.99..9.99]" )
				offs_win.refresh ( )
				curses.napms ( 2500 )
				del offs_win
				stdscr.refresh ( )
				curses.halfdelay ( 1 )
			else :
				j.setoffset ( activechan, offsinput )
				del offs_win
				stdscr.refresh ( )
				curses.halfdelay ( 1 )

		# Duty cycle
		status_duty1 = j.getdutycycle ( 1 )
		status_duty2 = j.getdutycycle ( 2 )
		if ( k == ord ( 'd' ) or k == ord ( 'D' ) ) :
			duty_win = stdscr.subwin ( size_y_box, size_x_box, start_y_box, start_x_box )
			duty_win.bkgd ( curses.color_pair ( activechan ) )
			duty_win.box ( )
			duty_win.addstr ( 1, 2, "Duty Cycle Channel {}:" .format ( activechan ) )
			curses.echo ( )
			duty_win.addstr ( 3, 2, "[%] : " )
			duty_win.refresh ( )
			dutyinput = 0
			input = duty_win.getstr ( 3, 8, 10 )
			try :
				dutyinput = float ( input )
			except ValueError :
				duty_win.addstr ( 4, 2, "Invalid! %=[0..99.9]" )
				duty_win.refresh ( )
			if ( dutyinput < 0.9 or dutyinput > 99.9 ) :
				duty_win.addstr ( 4, 2, "Invalid! %=[0..99.9]" )
				duty_win.refresh ( )
				curses.napms ( 2500 )
				del duty_win
				stdscr.refresh ( )
				curses.halfdelay ( 1 )
			else :
				j.setdutycycle ( activechan, dutyinput )
				del duty_win
				stdscr.refresh ( )
				curses.halfdelay ( 1 )

		# Phase
		status_phase = j.getphase ( )
		if ( k == ord ( 'p' ) or k == ord ( 'P' ) ) :
			# only on right side
			start_x_box = 34
			phase_win = stdscr.subwin ( size_y_box, size_x_box, start_y_box, start_x_box )
			phase_win.bkgd ( curses.color_pair ( 2 ) )
			phase_win.box ( )
			phase_win.addstr ( 1, 2, "Phase:" )
			curses.echo ( )
			phase_win.addstr ( 3, 2, "[Deg] : " )
			phase_win.refresh ( )
			phaseinput = 0
			input = phase_win.getstr ( 3, 10, 10 )
			try :
				phaseinput = float ( input )
			except ValueError :
				phase_win.addstr ( 4, 2, "Invalid! P=[0..360]" )
				phase_win.refresh ( )
			if ( phaseinput < 0.0 or phaseinput > 360.0 ) :
				phase_win.addstr ( 4, 2, "Invalid! P=[0..360]" )
				phase_win.refresh ( )
				curses.napms ( 2500 )
				del phase_win
				stdscr.refresh ( )
				curses.halfdelay ( 1 )
			else :
				j.setphase ( phaseinput )
				del phase_win
				stdscr.refresh ( )
				curses.halfdelay ( 1 )

		# Common box strings
		title_str1 = "Channel"
		title_str3 = "utput"
		wave_str2 = "ave:"
		freq_str2 = "requency:"
		amp_str2 = "mplitude:"
		offset_str2 = "Off"
		offset_str3 = "et:"
		duty_str2 = "uty Cycle:"
		phase_str2= "hase:"

		# Chan 1 Box
		start_x_ch1 = 1
		start_y_ch1 = 2
		size_x_ch1 = 30
		size_y_ch1 = 15

		# Chan 2 Box
		start_x_ch2 = 31
		start_y_ch2 = 2
		size_x_ch2 = 30
		size_y_ch2 = 15

		# Draw Box 1
		win_ch1 = stdscr.subwin ( size_y_ch1, size_x_ch1, start_y_ch1, start_x_ch1 )
		win_ch1.bkgd ( curses.color_pair ( 1 ) )
		win_ch1.box ( )
		win_ch1.addstr ( 1, 2, title_str1 )
		win_ch1.addstr ( 1, 10, "1", curses.A_UNDERLINE )
		win_ch1.addstr ( 1, 11, ":" )
		win_ch1.addstr ( 1, 16, "O", curses.A_UNDERLINE )
		win_ch1.addstr ( 1, 17, title_str3 )
		win_ch1.addstr ( 1, 24, status_ch1, curses.color_pair ( 3 ) )

		win_ch1.addstr ( 3, 2, "W", curses.A_UNDERLINE )
		win_ch1.addstr ( 3, 3, wave_str2 )
		win_ch1.addstr ( 3, 16, "{} ".format ( status_wave1[1] ), curses.color_pair ( 3 ) )

		win_ch1.addstr ( 5, 2, "F", curses.A_UNDERLINE )
		win_ch1.addstr ( 5, 3, freq_str2 )
		win_ch1.addstr ( 5, 16, "{0:.3f} ".format ( status_freq1 ), curses.color_pair ( 3 ) )
		win_ch1.addstr ( 5, 25, freq_ch1_unit )

		win_ch1.addstr ( 7, 2, "A", curses.A_UNDERLINE )
		win_ch1.addstr ( 7, 3, amp_str2 )
		win_ch1.addstr ( 7, 16, "{0:.3f} ".format ( status_amp1 ), curses.color_pair ( 3 ) )
		win_ch1.addstr ( 7, 25, "V" )

		win_ch1.addstr ( 9, 2, offset_str2 )
		win_ch1.addstr ( 9, 5, "s", curses.A_UNDERLINE )
		win_ch1.addstr ( 9, 6, offset_str3 )
		win_ch1.addstr ( 9, 16, "{0:.2f} ".format ( status_offs1 ), curses.color_pair ( 3 ) )
		win_ch1.addstr ( 9, 25, "V" )

		win_ch1.addstr ( 11, 2, "D", curses.A_UNDERLINE )
		win_ch1.addstr ( 11, 3, duty_str2 )
		win_ch1.addstr ( 11, 16, "{0:.1f} ".format ( status_duty1 ), curses.color_pair ( 3 ) )
		win_ch1.addstr ( 11, 25, "%" )

		# Draw Box 2
		win_ch2 = stdscr.subwin ( size_y_ch2, size_x_ch2, start_y_ch2, start_x_ch2 )
		win_ch2.bkgd ( curses.color_pair ( 2 ) )
		win_ch2.box ( )
		win_ch2.addstr ( 1, 2, title_str1 )
		win_ch2.addstr ( 1, 10, "2", curses.A_UNDERLINE )
		win_ch2.addstr ( 1, 11, ":" )
		win_ch2.addstr ( 1, 16, "O", curses.A_UNDERLINE )
		win_ch2.addstr ( 1, 17, title_str3 )
		win_ch2.addstr ( 1, 24, status_ch2, curses.color_pair ( 3 ) )

		win_ch2.addstr ( 3, 2, "W", curses.A_UNDERLINE )
		win_ch2.addstr ( 3, 3, wave_str2 )
		win_ch2.addstr ( 3, 16, "{} ".format ( status_wave2[1] ), curses.color_pair ( 3 ) )

		win_ch2.addstr ( 5, 2, "F", curses.A_UNDERLINE )
		win_ch2.addstr ( 5, 3, freq_str2 )
		win_ch2.addstr ( 5, 16, "{0:.3f} ".format ( status_freq2 ), curses.color_pair ( 3 ) )
		win_ch2.addstr ( 5, 25, freq_ch2_unit )

		win_ch2.addstr ( 7, 2, "A", curses.A_UNDERLINE )
		win_ch2.addstr ( 7, 3, amp_str2 )
		win_ch2.addstr ( 7, 16, "{0:.3f} ".format ( status_amp2 ), curses.color_pair ( 3 ) )
		win_ch2.addstr ( 7, 25, "V" )

		win_ch2.addstr ( 9, 2, offset_str2 )
		win_ch2.addstr ( 9, 5, "s", curses.A_UNDERLINE )
		win_ch2.addstr ( 9, 6, offset_str3 )
		win_ch2.addstr ( 9, 16, "{0:.2f} ".format ( status_offs2 ), curses.color_pair ( 3 ) )
		win_ch2.addstr ( 9, 25, "V" )

		win_ch2.addstr ( 11, 2, "D", curses.A_UNDERLINE )
		win_ch2.addstr ( 11, 3, duty_str2 )
		win_ch2.addstr ( 11, 16, "{0:.1f} ".format ( status_duty2 ), curses.color_pair ( 3 ) )
		win_ch2.addstr ( 11, 25, "%" )

		win_ch2.addstr ( 13, 2, "P", curses.A_UNDERLINE )
		win_ch2.addstr ( 13, 3, phase_str2 )
		win_ch2.addstr ( 13, 16, "{0:.1f} ".format ( status_phase ), curses.color_pair ( 3 ) )
		win_ch2.addstr ( 13, 25, "Deg" )

		## Declaration of strings
		topstatusstr = "Selected Channel: {}            Connected to: {}" .format ( activechan, theport )
		statusbarstr = "Press 'q' to exit | '1' or '2' selects channel"

		# Render top and status bar
		stdscr.attron ( curses.color_pair ( 4 ) )
		stdscr.addstr ( 0, 0, topstatusstr )
		stdscr.addstr ( 0, len ( topstatusstr ), " " * ( width - len ( topstatusstr ) - 1 ) )
		stdscr.attroff ( curses.color_pair ( 4 ) )

		stdscr.attron ( curses.color_pair ( 4 ) )
		stdscr.addstr ( height - 1, 0, statusbarstr )
		stdscr.addstr ( height - 1, len ( statusbarstr ), " " * ( width - len ( statusbarstr ) - 1 ) )
		stdscr.attroff ( curses.color_pair ( 4 ) )

		# Refresh the screen
		stdscr.refresh ( )

		# Wait for next input
		k = stdscr.getch ( )
		# Catch capital Q
		if k == ord ( 'Q' ) :
			k = ord ( 'q' )


def main ( ) :

	# Find available ports
	if sys.platform.startswith ( 'win' ) :
		ports = ['COM%s' % ( i + 1 ) for i in range ( 256 ) ]
	elif sys.platform.startswith ( 'linux' ) or sys.platform.startswith ( 'cygwin' ) :
		# Assume that we are connected via USB, for 'real' serial remove USB
		ports = glob.glob ( '/dev/ttyUSB*' )
	elif sys.platform.startswith ( 'darwin' ) :
		# Dito
		ports = glob.glob ( '/dev/tty.usb*' )
	else :
		raise EnvironmentError ( 'Unsupported platform!' )

	# Check if port is a serial port
	result = []
	for port in ports :
		try :
			s = serial.Serial ( port )
			s.close ( )
			result.append ( port )
		except ( OSError, serial.SerialException ) :
			pass

	# If none found
	if not result :
		print ( "No device found!" )
		return -1

	# Find our device
	for res in result :
		print ( "Trying {}" .format ( res ) )
		try:
			j = jds6600 ( res )
			theport = res
		except :
			pass

	# Start curses
	curses.wrapper ( draw_menu, theport )


if __name__ == "__main__" :
    main ( )


#
