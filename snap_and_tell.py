#!/usr/local/bin/python -u

import sys,os,logging,re,traceback
sys.path.append("/usr/local/bin/pymodules")
from genutil import EXENAME,EXEPATH,GeneralError
import genutil

# Import the modules we'll need
import RPi.GPIO as GPIO
import time
import picamera,datetime
#------------------------------------------------------------------------------
# GLOBALS
#------------------------------------------------------------------------------

logger=logging.getLogger(EXENAME)

#------------------------------------------------------------------------------
# USAGE
#------------------------------------------------------------------------------

def usage():
   from string import Template
   usagetext = """

 $EXENAME

 Function: Whatever

 Syntax  : $EXENAME {--debug #}

 Note    : Parm       Description
           ---------- --------------------------------------------------------
           --debug    optionally specifies debug option
                      0=off 1=STDERR 2=FILE

 Examples: $EXENAME

 Change History:
  em  XX/XX/2016  first written
.
"""
   template = Template(usagetext)
   return(template.substitute({'EXENAME':EXENAME}))


#------------------------------------------------------------------------------
# Subroutine: main
# Function  : Main routine
# Parms     : none (in sys.argv)
# Returns   : nothing
# Assumes   : sys.argv has parms, if any
#------------------------------------------------------------------------------
def main():

   ##############################################################################
   #
   # Main - initialize
   #
   ##############################################################################

   initialize()

   ##############################################################################
   #
   # Logic
   #
   ##############################################################################

   try:

      # We only want 1 instance of this running.  So attempt to get the "lock".
      genutil.getLock(EXENAME)

      recordingFileName_h264 = "/tmp/%s.h264" % EXENAME
      recordingFileName_mp4  = "/tmp/%s.mp4" % EXENAME
      photoFileName          = "/tmp/%s.jpg" % EXENAME

      with picamera.PiCamera() as camera:
         if genutil.G_options.captureType.lower() == 'video':
            print("Taking some video...")
            camera.start_recording(recordingFileName_h264)
            time.sleep(5)
            camera.stop_recording()
            binaryFilename = recordingFileName_mp4
         else:
            print("Taking a photo...")
            camera.capture(photoFileName)
            binaryFilename = photoFileName

      if genutil.G_options.captureType.lower() == 'video':
         # Convert the H264 video file to MP4
         print("Converting video to mp4...")
         os.system("/usr/bin/MP4Box -fps 30 -add %s %s >/tmp/MP4Box.out 2>&1" % (recordingFileName_h264, recordingFileName_mp4))

      print("Sending the %s to %s..." % (genutil.G_options.captureType, genutil.G_options.emailTo))
      subject = 'Just Snapped a %s at %s!' % (genutil.G_options.captureType, datetime.datetime.now().strftime("%Y-%m-%d_%H.%M.%S"))
      bodyText = 'Please see the attached file.'
      genutil.sendEmail(genutil.G_options.emailTo, subject, bodyText, binaryFilepath=binaryFilename)

      # cleanup and reset
      if genutil.G_options.captureType.lower() == 'video':
         os.remove(recordingFileName_h264)
         os.remove(recordingFileName_mp4)
      else:
         os.remove(photoFileName)

   except GeneralError as e:
      if genutil.G_options.debug:
         # Fuller display of the Exception type and where the exception occured in the code
         (eType, eValue, eTraceback) = sys.exc_info()
         tbprintable = ''.join(traceback.format_tb(eTraceback))
         genutil.exitWithErrorMessage("%s Exception: %s\n%s" % (eType.__name__, eValue, tbprintable), errorCode=e.errorCode)
      else:
         genutil.exitWithErrorMessage(e.message, errorCode=e.errorCode)

   except Exception as e:
      if genutil.G_options.debug:
         # Fuller display of the Exception type and where the exception occured in the code
         (eType, eValue, eTraceback) = sys.exc_info()
         tbprintable = ''.join(traceback.format_tb(eTraceback))
         genutil.exitWithErrorMessage("%s Exception: %s\n%s" % (eType.__name__, eValue, tbprintable))
      else:
         genutil.exitWithErrorMessage(str(e))

   ##############################################################################
   #
   # Finish up
   #
   ##############################################################################

   logger.info(EXENAME+" exiting")
   logging.shutdown()

   exit()


#------------------------------------------------------------------------------
# Subroutine: initialize
# Function  : performs initialization of variable, CONSTANTS, other
# Parms     : none
# Returns   : nothing
# Assumes   : ARGV has parms, if any
#------------------------------------------------------------------------------
def initialize():

   # PROCESS COMMAND LINE PARAMETERS

   import argparse  # http://www.pythonforbeginners.com/modules-in-python/argparse-tutorial/

   parser = argparse.ArgumentParser(usage=usage())
   parser.add_argument('captureType')                    # positional, required.  photo or video
   parser.add_argument('emailTo')                        # positional, required
   parser.add_argument('--debug', dest="debug", type=int, help='0=no debug, 1=STDERR, 2=log file')

   genutil.G_options = parser.parse_args()

   if genutil.G_options.debug == None or genutil.G_options.debug == 0:
      logging.disable(logging.CRITICAL)  # effectively disable all logging
   else:
      if genutil.G_options.debug == 9:
         genutil.configureLogging(loglevel='DEBUG')
      else:
         genutil.configureLogging()

   #global G_config
   #G_config = genutil.processConfigFile()

   logger.info(EXENAME+" starting:"+__name__+" with these args:"+str(sys.argv))

# Standard boilerplate to call the main() function to begin the program.
if __name__ == "__main__":
   main()

#               print("1st Picture")
#               # image capture here: fswebcam -r 1280x720 image.jpg
#               camera.capture('/tmp/image1.jpg')
#               #os.system("/usr/bin/fswebcam -r 1280x720 /tmp/image1.jpg 2>/dev/null")
#               time.sleep(3)
#               print("2nd Picture")
#               # image capture here
#               camera.capture('/tmp/image2.jpg')
#               #os.system("/usr/bin/fswebcam -r 1280x720 /tmp/image2.jpg 2>/dev/null")
#               time.sleep(3)
#               print("3rd Picture")
#               # image capture here
#               camera.capture('/tmp/image3.jpg')
#               #os.system("/usr/bin/fswebcam -r 1280x720 /tmp/image3.jpg 2>/dev/null")
