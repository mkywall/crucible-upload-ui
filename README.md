# crucible-tem-upload-ui

This is a flask based application for uploading TEM generated data files to the [Crucible data platform](https://crucible.lbl.gov).<br>
The app is meant to run locally on instrument support PCs. To upload data, access to the local file system is required as well as an internet connection.<br>
The following workflow is supported by this application: 

- **Users can enter their ORCID or email address:**<br>
This will populate a list of projects for which the user has access. It will also ensure that the data uploaded is associated with that user account. 
<br>

- **Select a project to upload the dataset to**<br>
All members of the project will then have access to the uploaded data through the Crucible platform
<br>

- **Select the instrument from which they are uploading data**<br>

- **Search for a sample by sample_name or unique_id**<br>
This will display the sample details and create a relationship between any uploaded datasets and the sample provided.
<br>

- **Select a folder from their local file system to upload**<br>
The name of this folder will be used to create a dataset object in the Crucible platform with a measurement type of the format `{instrument_name} full session`.<br>
From this folder, all supported files* will be uploaded as datasets to the platform and linked as "children" of the session dataset.<br>
They will also be linked to the provided sample, user, and project_id. 
<br>

Once data is uploaded it can be viewed in the [Crucible Web Explorer](https://crucible-graph-explorer-776258882599.us-central1.run.app/)!<br>

*currently supported files include files smaller than 20GB with one of the following extensions: emd, ser, emi, dm3, dm4, mcr, bcf, and h5

### System requirements
- python >= 3.13
- internet connection
- [rclone](https://rclone.org/install/)
- if following the set up instructions it will be helpful to have [uv](https://docs.astral.sh/uv/getting-started/installation/#standalone-installer) installed `pipx install uv`
<br>

### Set Up
1. Clone this repository `git clone https://github.com/MolecularFoundryCrucible/crucible-tem-upload-ui.git`
2. Create the uv virtual environment (alternatively you should be able to use the package manager of your choice and install from the requirements file)
```
cd crucible-tem-upload-ui
uv sync
``` 
3. Configure rclone `rclone config`. You will need to configure 2 remotes:
    - The google drive that you would like data from the instrument to be copied to. Please name the mount in the format `{instrument_name}-gdrive`
    - mf-crucible google cloud storage. Please name the mount `mf-cloud-storage`. This will require access to the project. If you need access, please reach out to a member of the Molecular Foundry Data team. 

An example configuration file is included below: 

~/.config/rclone/rclone.conf
```
[titanx-gdrive]
type = drive
scope = drive
team_drive = <team-drive-id>
root_folder_id = 
token = {} # alternatively you can provide a service account key and add the service account email to your google shared drive.


[mf-cloud-storage]
type = google cloud storage
project_number = mf-crucible
service_account_file = <mf-crucible-service-account-key.json>
object_acl = projectPrivate
bucket_acl = projectPrivate
env_auth = true
bucket_policy_only = true
```
4. Run the app!

### Running the app
```
cd crucible-tem-upload-ui
uv python run main.py
```

### Additional Details
- instrument_conf.py allows configuration of instrument specific details that may be helpful (currently very limited (ha)):
    - `DEFAULT_BROWSE_DIR` will set the default directory 
- To prevent accidental uploads of system-level directories, the selected folder must be at least 3 levels deep from the filesystem root (e.g. D:\Users\data\session). 



