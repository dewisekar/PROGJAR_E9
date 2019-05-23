# PROGJAR_E9
## Anggota Kelompok
* Dewi Sekarini 05111640000004
* Isye Putri Roselin 05111640000020
* Daniel Kurniawan 05111640000081

## Tugas 4
### Protocol
#### Old Protocol:
* Login: auth [username] [password]
* Send message: send [username-recipient] [message]
* Inbox: inbox
#### New Protocol
* Logout: logout 
* Create group: create_group [groupname]
* Join group: join_group [groupname]
* Leave group: leave_group [groupname]
* Getting group list: list_group
* Getting user's group list: list_mygroup
* Getting group members list: list_members [groupname]
* Send message to group: send_group [groupname] [message]
* Inbox of a group: inbox_group [groupname]
* Send file = send_file [username-destination] [filename]
