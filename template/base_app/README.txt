################## Initial Setup Guide ##################
1. Install MariaDB
2. Create a python3.9+ environment
3. Run the following commands to allow the installation of mysqlclient:
    sudo yum install -y python36-devel mysql-devel gcc
    sudo ln -s /usr/lib64/libmariadbclient.a /usr/lib64/libmariadb.a
    pip install mysqlclient
4. pip install the requirements.txt file 
5. Edit the config file as necessary
6. Setup version control


################# Unit Tests ###############
run tests with command: python -m unittest discover -s tests -p '*_test.py'