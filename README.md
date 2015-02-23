Quick start
===========

```
$ sudo pip3 install virtualenv
$ virtualenv-3.4 ~/virtualenv/akamai
$ . ~/virtualenv/akamai/bin/activate

(akamai) $ python setup.py develop

# set the following environment variables
# - AK_BASE_URL
# - AK_CLIENT_TOKEN
# - AK_CLIENT_SECRET
# - AK_ACCESS_TOKEN

(akamai) $ akamai_cdn_report
```


Test dummy
==========

```
(akamai) $ pip install bottle
(akamai) $ python akamai_cdn_report/dummy.py

# from another terminal..

(akamai) $ AK_BASE_URL=http://localhost:8080/ akamai_cdn_report -d 2015-02-22
```
