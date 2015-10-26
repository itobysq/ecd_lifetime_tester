# The objective of this program is to use a 2401 Keithley to trigger a 7000 Keithley
# When the 7000 receives a trigger, it opens a switch to the target channel
# That switch has connects the Photodetector to the rear 2401 rear port, the device is connected to the 2401 front port
import serial, os
import time
from time import gmtime, strftime
import pytz
import datetime
import ctypes
#This first function calls the 2401 to do an external trigger on DB9 pin 1


def kiethley_readpd(ser):
    print 'reading PD value\r'
    #Take a measurement of the photodetector
    ser.write('*RST\r\n')
    ser.write(':SYSTEM:BEEPER:STATE 0\r\n')
    #ser.write(':ROUT:TERM FRONT\r\n')
    #ser.write(':SOUR:FUNC VOLT\r\n')
    #ser.write(':SOUR:VOLT:MODE FIXED\r\n')
    #ser.write(':SOUR:VOLT:RANG 5\r\n')
    #ser.write(':SOUR:VOLT:LEV 0\r\n')
    ser.write(':SENS:FUNC "CURR"\r\n')
    ser.write('SENS:CURR:PROT 5E-3\r\n')
    ser.write('SENS:CURR:NPLC 1\r\n') #this used to be =10 (10x integration)
    ser.write('SENS:AVER:TCON REP\r\n')
    ser.write('SENS:AVER:COUN 3\r\n') #this used to be 10
    ser.write('SENS:AVER ON\r\n')
    ser.write(':OUTPUT ON\r\n')
    ser.write(':READ?\r\n')
    ser.write(':OUTPUT OFF\r\n')
    while True:
        out = ser.readlines()
        if out != []:
            break
    return out

def store_current(fname, out):
    outstring = out[0]
    kdata=outstring.split(',')
    current = kdata[1]
    print current
    #Toby: now to write the data with a datetimestring
    fmt = '%Y-%m-%d %H:%M:%S'
    d = datetime.datetime.now(pytz.timezone("America/Los_Angeles"))
    d_string = d.strftime(fmt)
    d2 = datetime.datetime.strptime(d_string, fmt)
    line = d2.strftime(fmt)+'\t'+current+'\n'
    f = open(fname, 'ab+')
    f.write(line)
    f.close()

def transition(dev, volt, ser):
# WARNING: voltages must be entered as a floating point decimal for this thing to run


    ser.flushInput()
    ser.flushOutput()

    step = str(volt/20)
    volt = str(volt) 
    ser.write('*RST\r\n')

    ser.write(':SYSTEM:BEEPER:STATE 0\r\n')
    ser.write(':SOUR:FUNC:MODE VOLT\r\n')
    ser.write(':SOUR:VOLT:STAR 0\r\n') 
    if volt.find('.') == -1:
        ser.write(':SOUR:VOLT:STOP '+volt+'\r\n')
    else:
        places = volt.split('.')
        ser.write(':SOUR:VOLT:STOP '+places[0]+'.'+places[1]+'\r\n')
    if step.find('.') == -1:
        ser.write(':SOUR:VOLT:STEP '+step+'\r\n')
    else:
        places = step.split('.')
        ser.write(':SOUR:VOLT:STEP '+places[0]+'.'+places[1]+'\r\n')

    ser.write(':SOUR:CLE:AUTO OFF\r\n') #THIS was originally on enable auto off mode
    ser.write(':SOUR:VOLT:MODE SWE\r\n')
    ser.write(':SOUR:SWE:SPAC LIN\r\n')
    ser.write(':SOUR:DEL:AUTO OFF\r\n') #sets remote source delay to off
    ser.write(':SOUR:DEL 0\r\n') #sets source delay to 0 which doesn't even make sense

    ser.write(':SENS:FUNC "CURR"\r\n')
    ser.write(':SENS:CURR:RANG:AUTO ON\r\n')

    ser.write(':SENS:CURR:PROT:LEV 0.005\r\n')

    ser.write(':FORM:ELEM:SENS CURR,VOLT\r\n')
    ser.write(':TRIG:COUN 21\r\n')
    ser.write(':TRIG:DEL 0.5\r\n')
    ser.write(':OUTP ON\r\n')
    ser.write(':READ?\r\n')

    while True:
        xdata = ser.readlines()
        if xdata != []:
            break


    #ser.write('*RST\r\n')
    #ser.write(':SYSTEM:BEEPER:STATE 0\r\n')

    ser.write(':SOUR:VOLT:MODE FIXED\r\n')
    ser.write(':SOUR:VOLT:RANG 5\r\n')
    ser.write(':SOUR:VOLT:LEV '+str(volt)+'\r\n')

    ser.write(':SENS:CURR:RANG:AUTO ON\r\n')
    ser.write(':SENS:CURR:PROT:LEV 0.005\r\n')
    ser.write(':FORM:ELEM:SENS CURR,VOLT\r\n')
    ser.write(':TRIG:COUN 51\n') #OMG OMG OMG PLEASE CHANGE ME!!!!!!!
    #ser.write(':TRAC:FEED:CONT NEXT\r\n')
    ser.write(':TRIG:SOURCE IMM\r\n') #caused an error
    ser.write(':TRIG:DEL 1\r\n')
    ser.write(':OUTP ON\r\n')
    ser.write(':READ?\r\n')

    #ser.write(':TRAC:DATA?\r\n')
    ser.write(':OUTP OFF\r\n')
    while True:
        holddata = ser.readlines()
        if holddata != []:
            for meas in holddata:
                xdata.append(meas)
            break
    return xdata

def write_xdata(xdata,xname):
    fmt = '%Y-%m-%d %H:%M:%S'
    d = datetime.datetime.now(pytz.timezone("America/Los_Angeles"))
    d_string = d.strftime(fmt)
    d2 = datetime.datetime.strptime(d_string, fmt)
    f = open(xname, 'ab+')
    dateline = d2.strftime(fmt)+'\t'
    f.write(dateline)
    xsdata = xdata
    for x in range(0,len(xsdata)):
        datum = xsdata[x]
        cleaned = datum[2:-3]
       # print cleaned
        xline  = cleaned + '\t'
        f.write(xline)
    f.write('\r')
    f.close()

def timediff(start):
    d2 = datetime.datetime.now(pytz.timezone("America/Los_Angeles"))
    diff = d2 - start
    diff = str(diff)
    ndiff = str.split(diff,'.')
    ndigest = str(ndiff[0])
    ndigest2 = ndigest.replace(':','-')
    timeval = ndigest2
    return timeval


def switch_ch(count):
    chns = ['@1!1', '@1!2', '@1!1', 
        '@1!3', '@1!4', '@1!3',
        '@1!5', '@1!6', '@1!5',  
        '@1!7', '@1!8', '@1!7',
        '@1!9', '@1!10', '@1!9',
        '@1!11', '@1!12', '@1!11',
        '@1!13', '@1!14', '@1!13',
        '@1!15', '@1!16', '@1!15',
        '@1!17', '@1!18', '@1!17',
        '@2!3', '@2!4', '@2!3',
        '@2!5', '@2!6', '@2!5',
        '@2!7', '@2!8', '@2!7',
        '@2!9', '@2!10', '@2!9',
        '@2!11', '@2!12', '@2!11',
        '@2!13', '@2!14', '@2!13',
        '@2!15', '@2!16', '@2!15',
        '@2!19', '@2!20', '@2!19',
        '@2!18', '@2!17', '@2!18',
        ]
    k7 = serial.Serial(7, 9600, timeout=1)
    k7.write('open all\r\n')
    k7.write(':clos (' +chns[count]+')\r\n')    
    k7.close()
    
def release7001():
    k7 = serial.Serial(7, 9600, timeout=1)
    k7.write('open all\r\n') 
    k7.close()

def lqrelease7001():
    if os.path.exists("c:\Program Files (x86)")==True:
        testlib = ctypes.CDLL("C:\Program Files (x86)\LQElectronics\UGSimple\UGSimpleAPI\LQUGSimple_c.dll")
    else:
        testlib = ctypes.CDLL("C:\Program Files\LQElectronics\UGSimple\UGSimpleAPI\LQUGSimple_c.dll")
    testlib.Gwrite(7,'open all\r\n')
    testlib.Gwrite(8,'open all\r\n')
    time.sleep(1)

def lq7switch_ch(count):
    if os.path.exists("c:\Program Files (x86)")==True:
        testlib = ctypes.CDLL("C:\Program Files (x86)\LQElectronics\UGSimple\UGSimpleAPI\LQUGSimple_c.dll")
    else:
        testlib = ctypes.CDLL("C:\Program Files\LQElectronics\UGSimple\UGSimpleAPI\LQUGSimple_c.dll")
    testlib.Gwrite.restype = ctypes.c_int
    testlib.Gread.restype = ctypes.c_char_p
    chns = ['@1!1!1', '@2!1!1', '@1!1!1', 
        '@1!1!2', '@2!1!2', '@1!1!2',
        '@1!1!3', '@2!1!3', '@1!1!3', 
        '@1!1!4', '@2!1!4', '@1!1!4', 
        '@1!1!5', '@2!1!5', '@1!1!5', 
        '@1!1!6', '@2!1!6', '@1!1!6', 
        '@1!1!7', '@2!1!7', '@1!1!7',
        '@1!1!8', '@2!1!8', '@1!1!8',
        '@1!1!9', '@2!1!9', '@1!1!9',
        '@1!2!10', '@2!2!10', '@1!2!10', 
        '@1!3!10', '@2!3!10', '@1!3!10',
        '@1!4!10', '@2!4!10', '@1!4!10',
        ]
    testlib.Gwrite(7,'open all\r\n')
    testlib.Gwrite(7,':clos ('+chns[count] +') \r\n')  

def lq8switch_ch(count):
    if os.path.exists("c:\Program Files (x86)")==True:
        testlib = ctypes.CDLL("C:\Program Files (x86)\LQElectronics\UGSimple\UGSimpleAPI\LQUGSimple_c.dll")
    else:
        testlib = ctypes.CDLL("C:\Program Files\LQElectronics\UGSimple\UGSimpleAPI\LQUGSimple_c.dll")
    testlib.Gwrite.restype = ctypes.c_int
    testlib.Gread.restype = ctypes.c_char_p
    chns = ['@1!1!1', '@1!1!2', '@1!1!1', 
        '@1!1!3', '@1!1!4', '@1!1!3', 
        '@1!1!5', '@1!1!6', '@1!1!5',  
        '@1!1!7', '@1!1!8', '@1!1!7',  
        '@1!1!9', '@1!2!10', '@1!1!9', 
        '@1!3!10', '@1!4!10', '@1!3!10',
        ]
    testlib.Gwrite(8,'open all\r\n')
    testlib.Gwrite(8,':clos ('+chns[count] +') \r\n') 
print ('let us begin')
#Now for the actual code lol========================================
start = datetime.datetime.now(pytz.timezone("America/Los_Angeles"))
volt = 2 #negative to start in oxidation, positive to start in reduction
while(True):
    volt = volt*-1
    k7 = serial.Serial(7, 9600, timeout=1)
    k7.write(':open all\r\n')
    k7.close()
    count = 0
    ser = serial.Serial(5, 9600, timeout=1)

    if os.path.exists("c:\Program Files (x86)")==True:
        testlib = ctypes.CDLL("C:\Program Files (x86)\LQElectronics\UGSimple\UGSimpleAPI\LQUGSimple_c.dll")
    else:
        testlib = ctypes.CDLL("C:\Program Files\LQElectronics\UGSimple\UGSimpleAPI\LQUGSimple_c.dll")
    testlib.Gwrite.restype = ctypes.c_int
    testlib.Gread.restype = ctypes.c_char_p  
    
    #specify the file paths
    prefix = 'C:\\Users\\toby\\Dropbox\\NSF_SBIR_Grant\\AgingData\\AgingCPU\\Oct8\\NicePD'
    xprefix = 'C:\\Users\\toby\\Dropbox\\NSF_SBIR_Grant\\AgingData\\AgingCPU\\Oct8\\Nicetrans'
    
        #8888=========Now to move onto Keithley 70001 #2, gpib address 8========88888
    count = 0 #reset the device counter
    for dev in ['20151007_pedot7c60_tbapf6_pfb_ub_d16','20151007_pedot7_liclo4_pfb_ub_07',
            '20150930_pedot7_liclo4spe_ito_ub_d15','20151007_pedot7c60_liclo4_pfb_ub_d13',
            '20150928_pedot7_liclo4spe_ito_d04','20150221_pedot_liclo4_ito_pet_db2']:
        volts = [[-1.8,1.5],[-2.4,1.5], #first reduction voltage is actually -6
                 [-3.5,1.5],[-2.4,1.5],
                 [-3.5,1.5],[-6.0,0.8],
                 ]
        suffix = dev+'.txt'
        fname = prefix + suffix
        xname = xprefix + suffix
        voltset = volts[count]
        count = count+1
        timeval = timediff(start)
        #1. First read the PD on target device
        print 'the target device is ' + dev
        lq8switch_ch(3*count-3)
        out = kiethley_readpd(ser)
        store_current(fname, out)
        #2. Transition the film and write it to file

        lq8switch_ch(3*count-2)
        if volt < 0:
            actvolt = voltset[0]
        else:
            actvolt = voltset[1]
        if actvolt == 'pass':

            xdata = ['0.0']
        else:
            xdata=transition(dev, actvolt, ser)
        print 'the voltage applied is '+str(actvolt)
        write_xdata(xdata,xname)
        #3. Measure the photodetector
        lq8switch_ch(3*count-1)
        out = kiethley_readpd(ser)
        store_current(fname, out)
        #4. Store data to file
        lqrelease7001()
    print('ended the loop') 
    #=============Now to move onto Keithley 70001 #2, gpib address 7============
    count = 0 #reset the device counter
    for dev in ['20151007_pedot7c60_liclo4_pfb_ub_d15','20150930_pedot7_liclo4spe_pfb_ub_d13',
            '20151007_pedot7_tbapf6_pfb_ub_d08',

            '20151007_pedot7c60_tbapf6_pfb_ub_d14','blank_pedot123dw_liclo4spe_pfb_ub_d05',
            '20150930_pedot123dw_liclo4spe_pfb_ub_d05','20150119_pedot_liclo4_ito_pet_db1',
            'blank_gb_pedot7_liclo4spe_ito_d02','20151007_pedot7_tbapf6_pfb_ub_d06']:
            #'20141213_pedot_lino3_ito_blank_d14_', '20141213_pedot_liclo4_ito_blank_d15_',
            #'20141213_blank_d13']:
        suffix = dev+'.txt'
        fname = prefix+suffix
        xname = xprefix+suffix
        volts = [[-2.4,1.5],[-2.4,1.5],
                 [-1.5,1.5],

                 [-2.4,1.5],[-6.0,0.8],
                 [-2.4,1.5],[-6.0,0.8],
                 [-6.0,1.5],[-1.4,1.5]]
                 #[-3.5,0.8],
                # [-3.0,0.8],[-3.5,0.8],
                # ]

        voltset = volts[count]
        count = count+1
        timeval = timediff(start)
        suffix = dev+'.txt'
        #fname = 'C:\\Users\\Toby\\Documents\\Aging\\Jan3\\NicePD'+suffix
        #xname = 'C:\\Users\\Toby\\Documents\\Aging\\Jan3\\Nicetrans'+suffix
        #1. First read the PD on target device
        print 'the target device is ' + dev
        lq7switch_ch(3*count-3)
        out = kiethley_readpd(ser)
        store_current(fname, out)
        #2. Transition the film and write it to file
        lq7switch_ch(3*count-2)
        if volt < 0:
            actvolt = voltset[0]
        else:
            actvolt = voltset[1]
        if actvolt == 'pass':
            xdata = ['0.0']
        else:
            xdata=transition(dev, actvolt, ser)
        print 'the voltage applied is '+str(actvolt)
        write_xdata(xdata,xname)
        #3. Measure the photodetector
        lq7switch_ch(3*count-1)
        out = kiethley_readpd(ser)
         #4. Store data to file
        store_current(fname, out)
        lqrelease7001()

    print('ended the loop')       
    
    #===OLD SKOOL!!!!=================OLD SKOOL!!!==========================
    count=0
    for dev in ['blank_pedot7f_liclo4spe_carbon_uv_d01','blank_pedot7_ecspe_ito_side_d51',
                'blank_pedot7_liclo4spe_ito_d02',
                'blank_pedot7_liclo4spe_carbon_ub_d07','blank_pedot7_liclo4spe_ito_ub_d01',

                'blank_p3ht_liclo4_ito_d13','20150930_pedot477dw_liclo4spe_pfb_ub_d09',
                'blank_pedot7_liclo4spe_ito_ub_uv_side_d32', '20150914_pedot7_liclo4spe_pfb_d02',

                'blank_p3ht_liclo4_ito_ub_d15', 'blank_pedot7f_ecspe_ito_uv_d14',
                '2blank_pedot477dw_liclo4spe_ito_ub_d11', 'blank_pedotf_liclo4spe_ito_d05',

                'blank_pedot7_liclo4spe_ito_side_d21', 'blank_pedot7f_liclo4spe_ito_d15',
                'blank_pedot7f_liclo4spe_ito_uv_d07', '20150928_pedot7dw123_liclo4spe_ito_d06',

                '20141103_PDref_']:
        volts = [[-6.0,0.8],[-5.0,1.5],
                 [-6.0,1.5],
                 [-6.0,1.5],[-6.0,1.5],

                 [-1.5,2.0],[-2.4,1.5],
                 [-5.0,1.5],[-1.8,1.5],

                 [-1.5,2.0],[-6.0,0.8],
                 [-3.5,1.5],[-6.0,1.5],

                 [-6.0,1.5],[-6.0,0.8],
                 [-6.0,0.8],[-3.5,1.5],
                 ['pass','pass']
                 ]
        voltset = volts[count]
        count = count+1
        timeval = timediff(start)
        suffix = dev+'.txt'
        fname = prefix+suffix
        xname = xprefix + suffix
        #fname = 'C:\\Users\\Toby\\Documents\\Aging\\Jan3\\NicePD'+suffix
        #xname = 'C:\\Users\\Toby\\Documents\\Aging\\Jan3\\Nicetrans'+suffix
        #1. First read the PD on target device
        print 'the target device is ' + dev
        switch_ch(3*count-3)
        out = kiethley_readpd(ser)
        store_current(fname, out)
        #2. Transition the film and write it to file
        switch_ch(3*count-2)
        if volt < 0:
            actvolt = voltset[0]
        else:
            actvolt = voltset[1]
        if actvolt == 'pass':
            xdata = ['0.0']
        else:
            xdata=transition(dev, actvolt, ser)
        print 'the voltage applied is '+str(actvolt)
        write_xdata(xdata,xname)
        #3. Measure the photodetector
        switch_ch(3*count-1)
        out = kiethley_readpd(ser)
        store_current(fname, out)
            #4. Store data to file
        release7001()
    print('ended the loop')       
    ser.close()

    print('that was the last one... restarting')
