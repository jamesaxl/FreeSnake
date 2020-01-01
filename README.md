# FreeSnake
FreeSnak is a package that contains:
   - Fcp (is a suite of command-line freenet applications, as well as a powerful Python library, for Freenet).
   - Fsite (Freenet site manager GUI)
   - Fchat (Freenet chat GUI).
   - Fradio (Freenet Radio GUI).
   - Ftube (freenet tube GUI. It will be used only in Darknet mode).
      - Darknet Mode is: When you have a number of connections with friends.

### Installation
Fcp requires python version 3 to run.

```sh
$ . /path/to/py3_virtualenv/active/bin
(py3_virtualenv)$ cd /path/to/FreeSnake
(py3_virtualenv)$ pip install -r requirements.txt
```

### Fsite demo
 ```sh
(py3_virtualenv)$ cd /path/to/FreeSnake
(py3_virtualenv)$ python
>>> from Fsite.Base.WebSite import WebSite
>>> w = WebSite()
>>> w.insert('name_of_your_web_site', 'absolute_path_of_your_web_site', 'default_index')
```
To Update a website

 ```sh
(py3_virtualenv)$ cd /path/to/FreeSnake
(py3_virtualenv)$ python
>>> from Fsite.Base.WebSite import WebSite
>>> w = WebSite()
>>> w.update('name_of_your_web_site', 'absolute_path_of_your_web_site', 'default_index')
```

### Fsite Radio
 ```sh
(py3_virtualenv)$ cd /path/to/FreeSnake
(py3_virtualenv)$ python
>>> from Fradio.Base.Radio import Radio
>>> r = Radio()
>>> r.insert('name_of_your_radio', 'absolute_path_of_your_radio')
```
To Update a website

 ```sh
(py3_virtualenv)$ cd /path/to/FreeSnake
(py3_virtualenv)$ python
>>> from Fradio.Base.Radio import Radio
>>> r = Radio()
>>> r.update('name_of_your_radio', 'absolute_path_of_your_radio')
```
To get list of files

 ```sh
 r.get_radio('PUBLIC_SSK_OF_RADIO', 'path', 'name_of_file')
```
To play

 ```sh
cvlc `sed 's,.*,url:port/&,' file_that_you_get_from_freenet`
```
