[![Build Status](http://runbot.odoo.com/runbot/badge/flat/1/master.svg)](http://runbot.odoo.com/runbot)
[![Tech Doc](http://img.shields.io/badge/master-docs-875A7B.svg?style=flat&colorA=8F8F8F)](http://www.odoo.com/documentation/master)
[![Help](http://img.shields.io/badge/master-help-875A7B.svg?style=flat&colorA=8F8F8F)](https://www.odoo.com/forum/help-1)
[![Nightly Builds](http://img.shields.io/badge/master-nightly-875A7B.svg?style=flat&colorA=8F8F8F)](http://nightly.odoo.com/)

Odoo
----

Odoo is a suite of web based open source business apps.

The main Odoo Apps include an <a href="https://www.odoo.com/page/crm">Open Source CRM</a>,
<a href="https://www.odoo.com/page/website-builder">Website Builder</a>,
<a href="https://www.odoo.com/page/e-commerce">eCommerce</a>,
<a href="https://www.odoo.com/page/warehouse">Warehouse Management</a>,
<a href="https://www.odoo.com/page/project-management">Project Management</a>,
<a href="https://www.odoo.com/page/accounting">Billing &amp; Accounting</a>,
<a href="https://www.odoo.com/page/point-of-sale">Point of Sale</a>,
<a href="https://www.odoo.com/page/employees">Human Resources</a>,
<a href="https://www.odoo.com/page/lead-automation">Marketing</a>,
<a href="https://www.odoo.com/page/manufacturing">Manufacturing</a>,
<a href="https://www.odoo.com/#apps">...</a>

Odoo Apps can be used as stand-alone applications, but they also integrate seamlessly so you get
a full-featured <a href="https://www.odoo.com">Open Source ERP</a> when you install several Apps.

Getting started with Odoo
-------------------------

For a standard installation please follow the <a href="https://www.odoo.com/documentation/14.0/setup/install.html">Setup instructions</a>
from the documentation.

To learn the software, we recommend the <a href="https://www.odoo.com/slides">Odoo eLearning</a>, or <a href="https://www.odoo.com/page/scale-up-business-game">Scale-up</a>, the <a href="https://www.odoo.com/page/scale-up-business-game">business game</a>. Developers can start with <a href="https://www.odoo.com/documentation/14.0/tutorials.html">the developer tutorials</a>.

## How to run server

The Odoo Meetings modules is on the local-addons folder. To run the server & update the custom module:

```
cd CommunityPath/
python3 odoo-bin --addons-path=addons/,local-addons/ -d mydb --dev all -u odoo_meetings
```

Dependencies
------------

### Pip3

Pip3 is a version of the pip installer for python3, which can download and configure new python modules with a simple one line command:

```
sudo apt update
sudo apt install python3-pip
```

To verify the installation:

```
pip3 --version
```

### Pandas

Pandas is a fast, powerful, flexible and easy to use open source data analysis and manipulation tool, built on top of the Python programming language:

```
pip3 install pandas
```

### Google Calendar

In Google Cloud Platform, create a new credential for Google Calendar API and download the OAuth client secret JSON (`credentials.json`). Put this file under `local-addons/odoo_meetings/static/google_calendar`.

After that, install the `Google client library`:

```
  pip3 install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib
```

When deploying you may update the path of `credentials.json` or of `token.json` (is where the credentials are saved for the next run) from the `local-addons/odoo_meetings/controllers/google_calendar_handler.py`.

Odoo Meetings menu does not appear on Website?
--------------------------------------------

On the website editor, click on `Pages` > `Edit Menu` > `Add menu item`. Insert the menu label (label seen by user) and on URL or Email type `/odoo-meetings/`.


Demo
----
There is a demo version available on https://odoomeetings.tk. If you want access to the back office, contact me.


How to install Odoo 14 on Amazon Web Services EC2 instance
---------------------------------------------------

To install Odoo 14 on AWS EC2 Ubuntu instance you can follow this guide: [Guide to deploy Odoo to AWS EC2 instance](https://www.cybrosys.com/blog/how-to-install-odoo-11-on-amazon-ec2). This guide refers to Odoo 11, so if you want to install version 14, on step 14 you must run:

```
wget -O - https://nightly.odoo.com/odoo.key | apt-key add -
echo "deb http://nightly.odoo.com/14.0/nightly/deb/ ./" >> /etc/apt/sources.list.d/odoo.list
apt-get update && apt-get install odoo
```
The odoo installation will be located in: `/usr/lib/python3/dist-packages/odoo`.

How to deploy the custom module to AWS EC2
------------------------------------------

For this you can use Secure copy protocol (SCP), which is a means of securely transferring computer files between a local host and a remote host or between two remote hosts. It is based on the Secure Shell (SSH) protocol:

```
scp -r -i ~/Documents/Odoo/odoo_aws.pem ~/Documents/Odoo/odoo/local-addons/odoo_meetings ubuntu@ec2-35-178-110-172.eu-west-2.compute.amazonaws.com:/usr/lib/python3/dist-packages/odoo/addons
```

Remember to update your key pairs (PEM file), custom module path and the destination username@IP (you can get it on AWS console).

Update Odoo default Port
------------------------

Odoo is running by default on port 8069, so the URL is `http://localhost:8069`. If you want to access to the website on `http://localhost` URL, you must update the port from 8069 to 80. This is because on a Web server or Hypertext Transfer Protocol daemon, port 80 is the port that the server “listens to” or expects to receive from a Web client.

To achieve that, you must configure Nginx which is a free, open-source, high-performance HTTP server and reverse proxy, as well as an IMAP/POP3 proxy server.

1. Install Nginx

`sudo apt-get install nginx`

2. Update the Nginx config file

Edit the Nginx main configuration file with a text editor and insert the following block after the line which specifies Nginx document root location.

`sudo nano /etc/nginx/sites-enabled/default`

Change the `location` with the following code and comment or delete the previous `location`:

```
location / {
  proxy_pass http://127.0.0.1:8069;
  proxy_redirect off;
  proxy_set_header Host $host;
  proxy_set_header X-Real-IP $remote_addr;
  proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
  proxy_set_header X-Forwarded-Proto $scheme;
}
```

Where `127.0.0.1` is the public IP address. Also add the IP address on `server_name`.

4. Check whether the configuration is correct or not:

`nginx -t`

5. Restart Nginx

`sudo service nginx restart`

Remember to update the inbound and outbound rules on AWS security groups.

SSL Certificate
---------------

The first step to using Let’s Encrypt to obtain an SSL certificate is to install the Certbot software on your server:

```
sudo apt update
sudo apt install python3-acme python3-certbot python3-mock python3-openssl python3-pkg-resources python3-pyparsing python3-zope.interface
sudo apt install python3-certbot-nginx
sudo certbot --nginx -d your_domain -d www.your_domain
```

After that, edit the Nginx main configuration file with a text editor and insert the following block after the line which specifies Nginx document root location.

```
sudo nano /etc/nginx/sites-enabled/default
```

After the `location` add the following code:

```
ssl_certificate /etc/letsencrypt/live/domainname.com/fullchain.pem;
ssl_certificate_key /etc/letsencrypt/live/domainname.com/privkey.pem;
```

Certificates provided by Let’s Encrypt are valid for 90 days only, so you need to renew them often. Now you set up a cronjob to check for the certificate which is due to expire in next 30 days and renew it automatically.

```
sudo crontab -e
```

Add this line at the end of the file. This cronjob will attempt to check for renewing the certificate twice daily.

```
0 0,12 * * * certbot renew >/dev/null 2>&1
```

More information on:
* https://www.cloudbooklet.com/install-odoo-13-on-ubuntu-18-04-with-nginx-google-cloud/ 
* https://www.digitalocean.com/community/tutorials/how-to-secure-nginx-with-let-s-encrypt-on-debian-10