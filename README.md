# OPNSense to qBittorrent Port Sync Tool
This Python script is designed to take an OPNSense alias containing a port number and configure qBittorrent with it.

There are two ways to configure this script:
- Environment Vars
- JSON

This script was built with the intention of being used in a orchestration tool such as Semaphore or Rundeck, so environment vars is the preferred and easiest approach without having to clone the repo and creating a settings file.

## Requirements

The only external library this script uses is `requests` and its own dependancies.

## Using this script via Semaphore

You can run this script directly from Semaphore, using the steps below:

1. Configure a new repository pointing to this repo:
![](https://github.com/user-attachments/assets/cce7d554-bb27-484b-b7f7-83a1f7aedf8a)
2. Head over to Variable Groups, and create a new one, containing all the variables found in the settings section below (you can put password either in the variables or secrets section):
![](https://github.com/user-attachments/assets/d3f5d966-2669-4053-b320-bd1fc47b7b45)
3. On the Task Templates page, create a new 'python script' template, typing "sync.py" as the script name and selecting the variable group you created on the last step.
![](https://github.com/user-attachments/assets/74647f28-0e35-4d0c-bce5-2cc4ce686a8d)
4. You can now hit the play button, and check that it works. You should get success, and output informing you if the script has made a change or not:
![](https://github.com/user-attachments/assets/6328ce70-e1c6-4d4c-abc4-5f89e1668595)
5. If you want to put this on a schedule, you can head to the schedule page and create new one for the script to run daily, hourly, etc

## Running the script locally
If you want to run the script manually, or you prefer having it local and running via a cron job, you can simply clone the repo to wherever you want to run it. You can then either use environment vars, or rename the included 'settings.json.example' file with your details. As long as this file is in the same directory and sync.py, it will work fine. To run the sync, simply execute the sync.py file, eg:

`python3 sync.py`

## Settings/Variables

These are the variables the script uses. The format is the same whether you are using environment vars or a JSON file:

```
{
    "Q_USER": "string",
    "Q_PASS": "string",
    "Q_HOST": "string",
    "O_HOST": "string",
    "O_PORT": integer,
    "O_API_KEY": "string",
    "O_API_SECRET": "string",
    "O_FORWARDED_PORT_ALIAS": "string",
    "Q_PORT": interger,
    "Q_SSL": bool,
    "Q_SSL_VERIFY": bool,
    "O_SSL": bool,
    "O_SSL_VERIFY": bool
}
```