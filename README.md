# simple-irc
A simple IRC client and server.

# Instructions
1. Create your virtual environment and install the required packages  
`python -m venv env`  
`source env/bin/activate` (or `env\Scripts\activate.bat` for Windows users)  
`pip install -r requirements.txt`

2. Run the server  
`cd src`  
`python irc_server.py --port <port>`

3. Run the client  
`python irc_client.py --host <host> --port <port>`  