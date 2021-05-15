from secrets import MQQT_SERVER, MQQT_USERNAME, MQQT_PASSWORD
import app.model
import app.mqqt


# Create/Open database
app.model.initialize_models()

app.mqqt.start_mqqt(MQQT_SERVER, MQQT_USERNAME, MQQT_PASSWORD, subscribe_to="erika/upload")