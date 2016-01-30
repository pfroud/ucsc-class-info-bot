@echo off

rem http://stackoverflow.com/a/1194991

set hour=%time:~0,2%
if "%hour:~0,1%" == " " set hour=0%hour:~1,1%

set min=%time:~3,2%
if "%min:~0,1%" == " " set min=0%min:~1,1%

set secs=%time:~6,2%
if "%secs:~0,1%" == " " set secs=0%secs:~1,1%


set year=%date:~-4%

set month=%date:~7,2%
if "%month:~0,1%" == " " set month=0%month:~1,1%

set day=%date:~4,2%
if "%day:~0,1%" == " " set day=0%day:~1,1%

set dayOfWeek=%date:~0,3%


set datetimef=%dayOfWeek%-%day%-%month%-%year%_at_%hour%-%min%-%secs%


rem the '2>&1' redirects stderr
scrape_reddit.py > logs\%datetimef%.txt 2>&1
rem scrape_reddit.py | wtee logs\%datetimef%.csv

rem makes an audible beep sound
echo 