#!/usr/bin/env python3
## file-path: /home/riscure/chipwhisperer/jupyter/user/sca101/cw_funcs.md
## call from ipython:  run cw_funcs.py


import os
import sys
import chipwhisperer as cw
from pathlib import Path
import loguru
def get_settings():
	"""returns sane defaults if PLATFORM is not set"""
	ret = dict()
	default_SCOPETYPE = 'OPENADC'
	default_PLATFORM = 'CW308_SAM4S'
	default_CRYPTO_TARGET=None
	default_PROGRAMMER=cw.programmers.SAM4SProgrammer

   
	ret['platform']= os.getenv('PLATFORM',  default_PLATFORM)
	ret['scopetype']=os.getenv('SCOPETYPE', default_SCOPETYPE)
	ret['programmer']=default_PROGRAMMER
	fw_path_str=f"../../../hardware/victims/firmware/simpleserial-base-lab2/simpleserial-base-%s.hex" % (ret['platform'])
	ret['fw_path']=Path(fw_path_str)
	return ret

def flash_target(S, scope):
	fw_str_fname = str(S['fw_path'].absolute())
	print("##Flashing target with firmware:(%s)" % fw_str_fname)
	cw.program_target(scope, S['programmer'], fw_str_fname)

def get_default_scope(S):
	scope = cw.scope()
	scope.default_setup()
	return scope

def powercycle_target(scope):

	if PLATFORM == "CW308_SAM4S" or PLATFORM == "CWHUSKY":
		scope.io.target_pwr = 0
		time.sleep(0.2)
		scope.io.target_pwr = 1
		time.sleep(0.2)
		
def hard_reset_target(scope):
	if PLATFORM == "CW308_SAM4S" or PLATFORM == "CWHUSKY":
		# The SAM4S datasheet says reset is active low, so:
		scope.io.nrst = 'low'
		time.sleep(0.25) # Set the pin to low for 0.25s,
		scope.io.nrst = 'high_z' 
		time.sleep(0.25) #And then set it to 'disconnected'

	if PLATFORM == "CW303" or PLATFORM == "CWLITEXMEGA":
		scope.io.pdic = 'low' # XMEGA target: use `pdic` pin active low
		time.sleep(0.1)       # hold for .1s 
		scope.io.pdic = 'high_z' # and then set it to `disconnected`
		time.sleep(0.1) # ..and then let it boot for another .1s

	else:
		# TODO: emit a warning when using the default case
		scope.io.nrst = 'low'
		time.sleep(0.05)
		scope.io.nrst = 'high_z'
		time.sleep(0.05)

def print_settings(S):
	"""summarize settings in human form"""
	ret = f"## Settings scopetype: {S['scopetype']}\n   Current target platform: {S['platform']}"
	return ret
	
def my_capture_trace(S, scope, target, traceid):
    ktp = cw.ktp.Basic()
    key, text = ktp.next()
    #print("##My_capture_tracee")
    #print("##Trace:(%3d)" % (traceid))
    #print(f"##key: {key}")
    #print(f"##text: {text}")
	
    trace = cw.capture_trace(scope, target, text)
    return trace


def my_capture_loop(S, scope, target, n=100):
	print("Performing loop %d times" % (n))
	ret=[]
	for i in range(1, n):
		if (scope.errors):
			print("##Error detected! %s" % (scope.errors))
		ret.append(my_capture_trace(S,scope,target,i))
	return ret
def setup_defaults():
	S=get_settings()
	scope  = get_default_scope(S)
	target = cw.target(scope)

	if (S['programmer'] != None and S['fw_path'].exists() and  S['fw_path'].is_file() and S['fw_path'].stat().st_size > 0):
		print("Firmware: %s  %d bytes" % (S['fw_path'].absolute, S['fw_path'].stat().st_size))
		print("Programming...")
		flash_target(S,scope)
		print("Programming...complete!")
	return S, scope, target
if __name__ == '__main__':

	S,scope,target = setup_defaults()
	#TODO it would be smart to run through some simple known chosen key plaintext to see if we get what we expect.

	
	if (not scope.con):
		print("Scope dis-connected. Exiting.")
		sys.exit(0)
	print("Scope connected. Fw rev: %s. Gain: %d" % (scope.fw_version_str,  scope.gain.gain))
	print("Here is a sample Traces:")
	i=101
	T = my_capture_trace(S,scope,target,i)
	print(T)
	#print(f"##Traces[0]{Traces[0]}")

	if scope.errors:
		print("##!!Warning scope detected the following errors.")
		print(scope.errors)
		input("Press enter to clear errors.")
		scope.errors.clear()
	else:
		print("Congrats! no errors detected during capture")

	## Cleanup time
	##scope.dis()
	##target.dis()
	
