from secrets import MQQT_SERVER, MQQT_USERNAME, MQQT_PASSWORD
import app.model
import app.mqqt


# Create/Open database
app.model.initialize_models()

erika_mqqt = app.mqqt.ErikaMqqt(MQQT_SERVER, MQQT_USERNAME, MQQT_PASSWORD)
erika_mqqt.subscribe(subscribe_to="erika/#", qos=1)
erika_mqqt.run_forever()