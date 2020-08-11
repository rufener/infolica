# infolica
Fork and clone Infolica.  

## Production
### back
Open a cmd window and move to back folder.
```
cd back
```
Create a Python virtual environment with venv 
```
python -m venv env
```
Launch the virtual environment  
```
env/Scripts/activate
```
Install requirements  
```
pip install -r requirements.txt
```

Make your changes in config files.
Rename `production.ini.template` to `production.ini`  
Open the file and adapt `sqlalchemy.url`, `ldap_url` and `ldap_passwd` etc.

Install the project in editable mode
```
pip install -e .
```

To test if the backend is responding, type the following in your virtual env. It will serve your api.
```
pserve development.ini
```
In a web browser, check this url:
```
localhost:6543/infolica/api/test
```
If you can read "Yeah, your api is working!", your installation is running correctly.


### front
Move to front.
```
cd ../front
```

Duplicate the `.env` file to `env.development.local` for development or `env.production.local` for production and adapt urls and config. Files ending with `*.local` are ignored by git.

Install dependencies.
```
npm install
```

Then build with:
```
npm run build
```


### Install and configure Apache
If you already have an Apache with mod_wsgi enabled, switch to Apache configuration step.

You'll need to have an Apache 32bits if your python is 32bits or Apache 64bits if your python is 64bits. Download a pre-compiled wheel of mod_wsgi for python: https://www.lfd.uci.edu/~gohlke/pythonlibs/ in the root folder of your project. Make sure to choose the right version.

1. Install the wheel with pip install. Make sure you have Microsoft Visual C++ installed on your machine. 
For an Apache 2.4, 64bits with Python 3.7 and Microsoft Visual C++ 15, download file mod_wsgi‑4.7.1+ap24vc15‑cp37‑cp37m‑win_amd64.whl on (https://www.lfd.uci.edu/~gohlke/pythonlibs/)[https://www.lfd.uci.edu/~gohlke/pythonlibs/
```
pip install .\mod_wsgi-4.6.4+ap24vc15-cp37-cp37m-win_amd64.whl
mod_wsgi-express module-config
```
2. You'll have an output showing the path of the generated wsgi module. Copy the module to your Apache modules folder (replace c:\Apache with your installation folder) and rename it with .so extension:

```
cp .\env\Lib\site-packages\mod_wsgi\server\mod_*.pyd C:\Apache24\modules\mod_wsgi.so
```

3. In the conf\httpd.conf file of your Apache installation directory, add this line to enable mod_wsgi:
```
LoadModule wsgi_module modules/mod_wsgi.so
```

### Apache configuration

1. Rename the apache/wsgi.conf.sample file to wsgi.conf and adapt the paths according to your setup.

2. Finally, make your apache aware of your app by adding to the end of your httpd.conf file:
```
Include path\to\your\project\apache\*.conf
```
3. Restart apache



