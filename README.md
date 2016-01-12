# hour_logger

![](https://raw.githubusercontent.com/udeyrishi/hour_logger/master/hour_logger.png)

hour_logger is a simple command line app for logging your work hours and managing the money you make at work.

  - You can start and end shifts, and see the duration that you worked for
  - You can see how much money you expect to earn in these shifts
  - You can record the money that you received on your paychecks, and hour_logger will keep a running tally of the pending payments
  - hour_logger is [BitBar](https://github.com/matryer/bitbar) compatible for displaying the status in your OS X menu bar. See BitBar usage below for setup.

### Installation

You will need [Python 3.5+](https://www.python.org/downloads/) installed in your /usr/local/bin directory as the executable 'python3'. For other configs, change the first line of './hour_logger.py' appropriately.

Install hours_logger like this:
```sh
# installed_name is optional, and if not supplied, defaults to 'hours'
$ chmod a+x path/to/repo/install.sh && path/to/repo/install.sh installed_name
```

This will add a symbolic link 'installed_name' to your '/usr/local/bin/' directory for the main 'hour_logger.py' file, and give it executable permissions. You may need to restart your terminal session. The following sections assume that '/usr/local/bin/' is in your PATH, and that you used the default installed_name ('hours').

### BitBar
![](https://raw.githubusercontent.com/udeyrishi/hour_logger/master/bitbar_start.png) ![](https://raw.githubusercontent.com/udeyrishi/hour_logger/master/bitbar_end.png)
Additionally, the install.sh will generate a shell script called installed_name.1m.sh in your repo directory, and gives it executable permissions. If you use [BitBar](https://github.com/matryer/bitbar), and want to use hour_logger as a plugin, then put this file in your plugins directory. Else, you can ignore/delete it. This plugin uses the '--bitbar' option of hour_logger for generating the BitBar friendly output.

### Usage

Before using, you need to configure the app like this, assuming you make $30/hour:

```sh
$ hours --config -logfile path/to/logfile.log -rate 30
```

Then for starting a shift:
```sh
$ hours --start
```

And for ending a shift:
```sh
$ hours --end
```

On receiving a paycheck of, say, $100.24:
```sh
$ hours --payment 100.24
```

Other options:
```sh
# For seeing the current status--whether a shift is ongoing or not, and if ongoing,
# what is the total pending payment of all the completed shifts plus this shift,
# if this shift were ended right now, minus all the payments made. Also shows today's hours
$ hours --status

# For seeing the current status in a BitBar friendly format (used by the plugin)
$ hours --bitbar

# For deleting the log file
$ hours --clear

# For deleting all the current config settings
$ hours --rconfig

# For deleting the log file and config settings
$ hours --reset

# For seeing the current config
$ hours --config

# If contributing, and want to see the entire Python exception stack trace,
# use --debug flag with any other option. e.g.:
$ hours --payment 34.5 --debug
```
### License

[Apache v2.0](https://github.com/udeyrishi/hour_logger/blob/master/LICENSE)

[![Bitdeli Badge](https://d2weczhvl823v0.cloudfront.net/udeyrishi/hour_logger/trend.png)](https://bitdeli.com/free "Bitdeli Badge")

