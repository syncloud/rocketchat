conn = new Mongo();
db = conn.getDB("rocketchat");
cursor = db.rocketchat_settings.find();
while ( cursor.hasNext() ) {
   printjson( cursor.next() );
}

db.rocketchat_settings.update(
  { _id : "LDAP_Enable" },
  { $set : { value: true } }
);

db.rocketchat_settings.update(
  { _id : "LDAP_Host" },
  { $set : { value: "ldap://localhost" } }
);

db.rocketchat_settings.update(
  { _id : "LDAP_Authentication" },
  { $set : { value: true } }
);

db.rocketchat_settings.update(
  { _id : "LDAP_Authentication_UserDN" },
  { $set : { value: "dc=syncloud,dc=org" } }
);

db.rocketchat_settings.update(
  { _id : "LDAP_Authentication_Password" },
  { $set : { value: "syncloud" } }
);

db.rocketchat_settings.update(
  { _id : "LDAP_User_Search_Filter" },
  { $set : { value: "(&(objectclass=inetOrgPerson)(uid=%s))" } }
);

cursor = db.rocketchat_settings.find();
while ( cursor.hasNext() ) {
   printjson( cursor.next() );
}
