from pyo import *
import threading
import time

s = Server()
s.setAmp(.1)
s.boot()
s.start()


class Eq(PyoObject):
    """
    Parametric Equalizer.

    Description:
    This script defines a parametric equalizer class with five bands. Each band has a frequency, a Q factor,
    a boost, and a bypass control. The boost and bypass controls are interpolated to avoid clicks when changing
    their values. The filter types supported are lowshelf, peak, and highshelf.

    Usage:
    1. Ensure you have the Pyo library installed.
    2. Run the script. An interactive GUI will open.
    3. Adjust the equalizer parameters using the OSC sliders and buttons.

    Dependencies:
    - Pyo library: http://ajaxsoundstudio.com/software/pyo/

    Class:
    Eq
    Parameters:
    - src: PyoObject, optional
        The audio source to be equalized. Default is a Noise generator.
    - port: int, optional
        The OSC port number for receiving control messages. Default is 9997.
    
    Methods:
    - out()
        Connects the equalizer's output to the audio output of the Pyo server.

    - play():
        Starts the ParamEq instance.
    
    - def stop():
        Stops the ParamEq instance.
        
    

    Example:
    if __name__ == '__main__':
        # Create an instance of Eq
        eq = Eq()

        # Connect the equalizer to the audio output and display its spectrum
        eq.out()
        Spectrum(eq)

        # Start the Pyo server GUI
        s.gui(locals())
    """
        
    def __init__(self,src= Noise(),port = 9997):
        
        super().__init__()
        
        self._src = src 
        self._port = port
        self._oscmsg = OscReceive(port=self._port, address=["/freq1","/freq2","/freq3","/freq4","/freq5","/q1","/q2","/q3","/q4","/q5","/boost1","/boost2","/boost3","/boost4","/boost5", "/mul","/bypass1","/bypass2","/bypass3","/bypass4","/bypass5"])       
       
        #FREQS

        self._lpfreq = self._oscmsg["/freq1"]
        self._p1freq = self._oscmsg["/freq2"]
        self._p2freq = self._oscmsg["/freq3"]
        self._p3freq = self._oscmsg["/freq4"]
        self._hpfreq = self._oscmsg["/freq5"]

        #Q
        self._lpq = self._oscmsg["/q1"]
        self._oscmsg.setValue("/q1", 1)
        self._p1q = self._oscmsg["/q2"]
        self._oscmsg.setValue("/q2", 1)
        self._p2q = self._oscmsg["/q3"]
        self._oscmsg.setValue("/q3", 1)
        self._p3q = self._oscmsg["/q4"]
        self._oscmsg.setValue("/q4", 1)
        self._hpq = self._oscmsg["/q5"]
        self._oscmsg.setValue("/q5", 1)

        #BOOST
        self._lpboost = self._oscmsg["/boost1"]
        self._p1boost = self._oscmsg["/boost2"]
        self._p2boost = self._oscmsg["/boost3"]
        self._p3boost = self._oscmsg["/boost4"]
        self._hpboost = self._oscmsg["/boost5"]


        #MUL
        self._mul = self._oscmsg["/mul"]
        self._oscmsg.setValue("/mul", 1)
        

        #BYPASS
        self._lpbypass = self._oscmsg["/bypass1"]
        self._p1bypass = self._oscmsg["/bypass2"]
        self._p2bypass = self._oscmsg["/bypass3"]
        self._p3bypass = self._oscmsg["/bypass4"]
        self._hpbypass = self._oscmsg["/bypass5"]

        #EQ CHAIN

        self._lowshelf = EQ(self._src, freq=self._lpfreq, q=self._lpq, boost=self._lpboost,mul=self._mul, type=1)
        self._lowshelf_out = Interp(self._src, self._lowshelf, interp=self._lpbypass)

        self._peak1 = EQ(self._lowshelf_out, freq=self._p1freq, q=self._p1q, boost=self._p1boost,mul=self._mul, type=0)
        self._peak1_out = Interp(self._lowshelf_out, self._peak1, interp=self._p1bypass) 

        self._peak2 = EQ(self._peak1_out, freq=self._p2freq, q=self._p2q, boost=self._p2boost,mul=self._mul, type=0)
        self._peak2_out = Interp(self._peak1_out, self._peak2, interp=self._p2bypass) 

        self._peak3 = EQ(self._peak2_out, freq=self._p3freq, q=self._p3q, boost=self._p3boost,mul=self._mul, type=0)
        self._peak3_out = Interp(self._peak2_out, self._peak3, interp=self._p3bypass) 

        self._highshelf = EQ(self._peak3_out, freq=self._hpfreq, q=self._hpq, boost=self._hpboost,mul=self._mul, type=2)
        self._highshelf_out = Interp(self._peak3_out, self._highshelf, interp=self._hpbypass) 

        self._p=Pan(self._highshelf_out, outs=2, pan=0.5)
        self._p.out()

        self._base_objs = self._p.getBaseObjects()
    
    # Add the properties and setters for each band's frequency and Q factor
    @property
    def lpFreq(self):
        return self._oscmsg.get(identifier="/freq1")

    @lpFreq.setter
    def lpFreq(self, freq):
        self._oscmsg.setValue("/freq1", freq)

    @property
    def p1Freq(self):
        return self._oscmsg.get(identifier="/freq2")
    
    @p1Freq.setter
    def p1Freq(self, freq):
        self._oscmsg.setValue("/freq2", freq)

    @property
    def p2Freq(self):
        return self._oscmsg.get(identifier="/freq3")
    
    @p2Freq.setter
    def p2Freq(self, freq):
        self._oscmsg.setValue("/freq3", freq)

    @property
    def p3Freq(self):
        return self._oscmsg.get(identifier="/freq4")
    
    @p3Freq.setter
    def p3Freq(self, freq):
        self._oscmsg.setValue("/freq4", freq)
    
    @property
    def hpFreq(self):
        return self._oscmsg.get(identifier="/freq5")
    
    @hpFreq.setter
    def hpFreq(self, freq):
        return self._oscmsg.setValue("/freq5", freq)
    
    @property
    def lpQ(self):
        return self._oscmsg.get(identifier="/q1")
    
    @lpQ.setter
    def lpQ(self, q):
        self._oscmsg.setValue("/q1", q)

    @property
    def p1Q(self):
        return self._oscmsg.get(identifier="/q2")
    
    @p1Q.setter
    def p1Q(self, q):
        self._oscmsg.setValue("/q2", q)

    @property
    def p2Q(self):
        return self._oscmsg.get(identifier="/q3")
    
    @p2Q.setter
    def p2Q(self, q):
        self._oscmsg.setValue("/q3", q)

    @property
    def p3Q(self):
        return self._oscmsg.get(identifier="/q4")
    
    @p3Q.setter
    def p3Q(self, q):
        self._oscmsg.setValue("/q4", q)
    
    @property
    def hpQ(self):
        return self._oscmsg.get(identifier="/q5")
    
    @hpQ.setter
    def hpQ(self, q):
        self._oscmsg.setValue("/q5", q)

    @property 
    def mul(self):
        return self._oscmsg.get(identifier="/mul")
    
    @mul.setter
    def mul(self, mul):
        self._oscmsg.setValue("/mul", mul)

    @property
    def lpBoost(self):
        return self._oscmsg.get(identifier="/boost1")
    
    @lpBoost.setter
    def lpBoost(self, boost):
        self._oscmsg.setValue("/boost1", boost)
    
    @property
    def p1Boost(self):
        return self._oscmsg.get(identifier="/boost2")
    
    @p1Boost.setter
    def p1Boost(self, boost):
        self._oscmsg.setValue("/boost2", boost)
    
    @property
    def p2Boost(self):
        return self._oscmsg.get(identifier="/boost3")
    
    @p2Boost.setter
    def p2Boost(self, boost):
        self._oscmsg.setValue("/boost3", boost)
    
    @property
    def p3Boost(self):
        return self._oscmsg.get(identifier="/boost4")
    
    @p3Boost.setter
    def p3Boost(self, boost):
        self._oscmsg.setValue("/boost4", boost)
    
    @property
    def hpBoost(self):
        return self._oscmsg.get(identifier="/boost5")
    
    @hpBoost.setter
    def hpBoost(self, boost):
        self._oscmsg.setValue("/boost5", boost)
    
    @property
    def lpBypass(self):
        return self._oscmsg.get(identifier="/bypass1")
    
    @lpBypass.setter
    def lpBypass(self, bypass):
        self._oscmsg.setValue("/bypass1", bypass)     
    
    @property
    def p1Bypass(self):
        return self._oscmsg.get(identifier="/bypass2")
    
    @p1Bypass.setter
    def p1Bypass(self, bypass):
        self._oscmsg.setValue("/bypass2", bypass)
    
    @property
    def p2Bypass(self):
        return self._oscmsg.get(identifier="/bypass3")
    
    @p2Bypass.setter
    def p2Bypass(self, bypass):
        self._oscmsg.setValue("/bypass3", bypass)
    
    @property   
    def p3Bypass(self):
        return self._oscmsg.get(identifier="/bypass4")
    
    @p3Bypass.setter
    def p3Bypass(self, bypass):
        self._oscmsg.setValue("/bypass4", bypass)

    @property
    def hpBypass(self):
        return self._oscmsg.get(identifier="/bypass5")
    
    @hpBypass.setter
    def hpBypass(self, bypass):
        self._oscmsg.setValue("/bypass5", bypass)

    @property
    def src(self):
        return self._src
            
      
    def play(self, dur=0, delay=0):
        """
        Starts the ParamEq instance.
        """
        self._p.play(dur, delay)
        return super().play(dur, delay)

    def stop(self):
        """
        Stops the ParamEq instance.
        """
        self._p.stop()
        return super().stop()
        
    def out(self, chnl=0, inc=1, dur=0, add=0):
        """
        Connects the ParamEq instance to the audio output of the Pyo server.
        """
        self._p.out(chnl, inc, dur, add)
        return super().out(chnl, inc, dur, add)
    
    def __repr__(self):
        
        return f"Lowpass freq={eq.lpFreq}\nPeak1 freq={eq.p1Freq}\nPeak2 freq={eq.p2Freq}\nPeak3 freq={eq.p3Freq}\nHighpass freq={eq.hpFreq}\nLowpass Q={eq.lpQ}\nPeak1 Q={eq.p1Q}\nPeak2 Q={eq.p2Q}\nPeak3 Q={eq.p3Q}\nHighpass Q={eq.hpQ}\nLowpass boost={eq.lpBoost}\nPeak1 boost={eq.p1Boost}\nPeak2 boost={eq.p2Boost}\nPeak3 boost={eq.p3Boost}\nHighpass boost={eq.hpBoost}\nLowpass bypass={eq.lpBypass}\nPeak1 bypass={eq.p1Bypass}\nPeak2 bypass={eq.p2Bypass}\nPeak3 bypass={eq.p3Bypass}\nHighpass bypass={eq.hpBypass}\nMul={eq.mul}\n"

if __name__ == '__main__':
    
    #sf = SfPlayer("nylon_guitar_loop_B1.wav", loop=True, mul=.5)


    eq = Eq()
    eq.out()
    print(eq)
    Spectrum(eq)

    # Define a function to continuously print EQ settings in a separate thread
    def print_eq_settings():
        while True:
            time.sleep(1)
            try:
                print(eq)
            except KeyboardInterrupt:
                break

    # Create a thread for printing EQ settings
    print_thread = threading.Thread(target=print_eq_settings)
    print_thread.start()

    s.gui(locals())