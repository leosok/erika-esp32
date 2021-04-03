from erika import Erika
import time

e1 = Erika()
# Setting a pulldown on RTS-Pin
#e1.rts.init(e1.rts.IN, e1.rts.PULL_DOWN)

for c in "Kurz  Test.":
    sent = False
    while not sent:      
        if e1.rts.value() == 0:
            # Erika is ready
            e1.uart.write(e1.ddr_2_ascii.encode(c))
            sent = True
        else:
            sent = False
        time.sleep(0.02)


    # print(e1.rts.value())
    # if e1.rts.value() == 0: # erika ready
    #     e1.uart.write(e1.ddr_2_ascii.encode(c))
    # else:
    #     time.sleep(0.2)
    #     e1.uart.write(e1.ddr_2_ascii.encode(c))
    # time.sleep(0.2)
