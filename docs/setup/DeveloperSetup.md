# Developer Setup

To develop this application you need to **open the Repository folder as a workspace in VS Code** (do NOT open any subfolder).

Important folders:

- `dashboard` - Angular business dashboard source code
- `framework` - Common framework source code (used by Lambdas and SQS Listener)
- `serverless` - [Lambdas](#lambdas) source code
- `setup` - SQL Setup scripts for DB upgradation
- `sqs-listener` - [SQS Listener](#sqs-listener) application source code
- `terraform` - Terraform scripts to create/destroy the AWS services needed
- `tests` - Automated test system

## GRDB SQS Listener (Python)

Python code for the main business rule engine of GRDB, hosted on AWS EKS.

Directory: `sqs-listener`.

### Local testing workflow setup

1. Make sure node, npm and Python3 is installed.

2. **Windows 10** - Click Start > Type "powershell" > Right click Powershell and "Run as administrator". Then navigate to the Repository folder using `cd` command and run these:

```
pip install -r sqs-listener\requirements.txt
pip install -r sqs-listener\requirements-dev.txt
pip install -r serverless\requirements.txt
```

2. **Unix** - Open a console in the Repository folder and run these:

```
pip install -r sqs-listener/requirements.txt
pip install -r sqs-listener/requirements-dev.txt
pip install -r serverless/requirements.txt
```

3. Add this to your PATH variable (make sure the folder exists)

* For Windows: `C:\Users\<USERNAME>\AppData\Roaming\Python\Python39\Scripts`
* For Linux: `/usr/bin/python`

4. Open the Repository folder as a workspace in VS Code (do NOT open any subfolder)

5. Inside the `sqs-listener` folder, add the `config.yaml` file provided by a team member, or create it manually using the `config.yaml.template` and `config.yaml.template.dev` (combine both templates). 

6. Verify that your debug settings are correct: open `sqs-listener/config.yaml` and add the paths of your CSV input files in the setting shown below:

```yaml
local:
  inputFiles:
    - C:/path/to/file1.csv
    - C:/path/to/file2.csv
```

7. Click the green play button in VS Code's debug panel to start debugging

### Compile-time errors setup

Follow these steps to setup `mypy` for compile-time errors as part of your build toolchain. It will check the errors in the entire project everytime you save a file.

1. Install these extensions in VS Code: `Python`, `Pylance`, `Trigger Task on Save`

2. Go to VS Code > Settings > Search for this `triggertaskonsave` > Scroll down to `Trigger Task On Save: Tasks` > Click `Edit in settings.json`

3. Paste this in the `settings.json`:
	```json
	"triggerTaskOnSave.tasks": {
		"compile-python-project": ["**/*.*py"]
	}
	```

4. Press F1 > Search for `Linter` > click on `Python: Select Linter` > Select `Disable Linter`

5. Open any code file and save it. You will see compile-time errors in panel everytime you save a file.


### Local database setup

If you want to setup the GRDB DB locally, follow these:

1. Install [XAMPP](https://www.apachefriends.org/download.html) for Windows or [MySQL Server](https://www.digitalocean.com/community/tutorials/how-to-install-mysql-on-ubuntu-20-04) for Unix
2. In case of XAMPP, open the XAMPP control panel and start the MySQL service
3. Install and open an SQL client - [HeidiSQL](https://www.heidisql.com/download.php) for Windows, [DBeaver](https://dbeaver.io/) for Unix
4. Connect to your local DB by using these details:

   - Host : `localhost`
   - Port : `3306`
   - User : `root`
   - Pass : (blank)
   
5. Create a new database called `grdb_local` with `utf8_general_ci` locale
6. Run the script to import GRDB tables (ask team)
7. Run the script to import GRDB data (ask team)
8. Go into the GRDB repo and open the `serverless/config/dev.json`
9. Modify the properties as follows:
```json
	"dbHost": "localhost",
	"dbUser": "root",
	"dbPassword": "",
	"databaseName": "grdb_local",
	"dbPort": 3306,
```
10. Run the local testing pipeline as given above


## GRDB Lambda Functions (Python)

Python code for the lambda functions of GRDB, using the serverless framework and hosted on AWS Lambda.

Directory: `serverless`.

### Serverless local workflow setup
- Make sure node and npm is installed.
- Install `serverless` package (v2.x.x) from npm globally. e.g.
```
npm install -g serverless@2
```
- Run 'npm install' in root directory of the project.
```
npm install
```
- To run the code locally, execute
```
serverless offline
```
- If you encounter the error 'TypeError: Os.tmpDir is not a function' follow the steps described in [this link](https://github.com/alhazmy13/serverless-offline-python/issues/18).
- Please note, serverless-offline-python has dependencies on serverless v1 and it will generate error if run using serverless v2.

### Serverless local packaging

In order to test what gets packaged into the lambdas, you can do this:

1. Install [Docker](https://docs.docker.com/engine/install/) (for Windows 10 also install [WSL2](https://wslstorestorage.blob.core.windows.net/wslblob/wsl_update_x64.msi))

2. Run these commands in the `serverless` folder

```
serverless package
```

3. Browse to `serverless\.serverless` and check `grdb.zip` which is the final deployment package

