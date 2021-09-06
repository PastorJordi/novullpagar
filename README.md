# novullpagar
Retrieves visible paywalled articles from Spanish journals. Currently it only supports Linux.  
use it with command: `python novullpagar.py [url] [path_to_store_html]`  
or (after exporting the alias)  
`novullpagar [url] [path_to_store_html]`  
second argument is optional (defaults to current directory)  

# "install"
For simplicity it is released as a standalone python script. Use an alias to call it with `novullpagar.sh`.
You can generate the alias automatically calling `python3 export.py` which will already take into account the current directory and the active python environment (if any) and makes an alias called `novullpagar`.  
You can use `pip install -r requirements.txt` to install dependencies.

# installing chromedriver:
You can get an appropriaversion from [their site](https://sites.google.com/a/chromium.org/chromedriver/downloads) and install it.  
If you never did that before, you can follow [this guide](https://tecadmin.net/setup-selenium-chromedriver-on-ubuntu/) (until step3)

# motivation
There's some context in this [post](tbd). Also, thanks for contributing, [AFont24](https://github.com/AFont24)