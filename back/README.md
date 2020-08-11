# infolica
Developped for Windows 64-bit

## Initialisation of the project
### Create a Python virtual environment with venv 
```
python3 -m venv env
```
### Launch the virtual environment  
```
env\Scripts\activate
```
### Install requirements  
```
pip install -r requirements.txt
```

### Make local changes
Rename `development.ini.template` to `development.ini`  
Open the file and adapt `sqlalchemy.url`, `ldap_url` and `ldap_passwd`

## Install the project in editable mode
```
pip install -e ".[testing]"
```

## In case of database migration  
Generate delta file
```
alembic -c development.ini revision --autogenerate -m "init"  
```
Apply modifications
```
alembic -c development.ini upgrade head
```

## Run your project  
```
pserve development.ini
```

## Testing
Tests are done with pytest python framework.
### Run your project's tests **Not implemented yet**  
```
pytest
```

