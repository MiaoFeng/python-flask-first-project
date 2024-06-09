Introduction
This is a simple python crawler project with Python, Flask and akshare.
The project is designed to crawl fund data from the a fund webstation and also from akshare.
Flask is used as the web framework and akshare is used to get the fund data from the akshare webstation.

The project provides APIs for:

1. Fund hold structure data
2. Fund ranking data
3. Briefly data of all funds
4. Fund company data
5. Fund detail data

Installation

1. Clone the repository and please ensure you have python on your computer
2. Install the required packages using pip
   python3 -m venv venv
   source venv/bin/activate
   pip3 install flask
   pip3 install flask-cors
   pip3 install requests
   pip3 install dumpy
   pip3 install akshare

3. Run the server using python app.py
   python3 server.py
