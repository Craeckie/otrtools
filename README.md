## OTR Search & Download
This application allows to search for movies and series and then download and process it in one run.


### Setup

#### Rabbitmq

Commands for `rabbitmqctl`:
```
add_vhost my_host
list_users
add_user my_user <password> / change_password my_user <password>
set_permissions -p my_host my_user ".*" ".*" ".*"
delete_user guest
```