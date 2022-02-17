from secrets import MQQT_SERVER, MQQT_USERNAME, MQQT_PASSWORD
import utils.mqqt
from erika_cloud import models

# Create/Open database
models.initialize_models()

erika_mqqt = utils.mqqt.ErikaMqqt(MQQT_SERVER, MQQT_USERNAME, MQQT_PASSWORD)
erika_mqqt.subscribe(subscribe_to="erika/upload", qos=1)
erika_mqqt.run_forever()