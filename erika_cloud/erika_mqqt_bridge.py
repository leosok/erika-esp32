from secrets import MQQT_SERVER, MQQT_USERNAME, MQQT_PASSWORD
import utils.mqqt as mqqt
from models import initialize_models


# Create/Open database
initialize_models()

erika_mqqt = mqqt.ErikaMqqt(MQQT_SERVER, MQQT_USERNAME, MQQT_PASSWORD)
erika_mqqt.subscribe(subscribe_to="erika/#", qos=1)
erika_mqqt.run_forever()